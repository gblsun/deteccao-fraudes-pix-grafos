"""Avalia os detectores em cenários de dificuldade (configs/cenarios.yaml).

O gerador sintético embute sinais "fáceis" por construção (golpes a qualquer
hora, contas fraudulentas recém-abertas, pessoas sempre ativas). Cada cenário
desliga parte deles; o script repete o experimento com várias sementes em
cada cenário para mostrar quais conclusões sobrevivem, em especial a
comparação entre atributos tabulares e de grafo.

Saídas em reports/results/:
    cenarios_execucoes.csv    uma linha por (cenário, semente, atributos, modelo)
    cenarios_resumo.csv       média, desvio e IC 95% de cada métrica, por cenário
    cenarios_comparacoes.csv  testes pareados entre conjuntos de atributos, por cenário
    cenarios_efeitos.csv      delta de Cliff (fraude × normal) de cada atributo, por cenário
e as figuras reports/figures/cenarios_average_precision.png e cenarios_efeitos.png.

Uso:
    python scripts/avaliar_cenarios.py --sementes 20 --processos 3
    python scripts/avaliar_cenarios.py --cenarios base realista --sementes 3
    python scripts/avaliar_cenarios.py --cenarios calibrado --modelos isolation_forest dbscan ecod
    python scripts/avaliar_cenarios.py --so-figuras    # redesenha as figuras sem rodar de novo
"""

import argparse
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    COMPARISONS,
    REPEATED_METRICS,
    load_experiment_config,
    load_scenarios,
    run_seeds,
    save_metadata,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_groups, compare_runs, effect_size_label, summarize_runs  # noqa: E402
from pixfraud.visualization import (  # noqa: E402
    DIVERGING_CMAP,
    INK,
    INK_SECONDARY,
    SEQUENTIAL_CMAP,
    SURFACE,
    plot_value_matrix,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Repete o experimento em cenários de dificuldade.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", help="cenários a rodar (padrão: todos, na ordem do arquivo)")
    parser.add_argument("--sementes", type=int, default=20, help="nº de repetições por cenário (sementes 1, 2, ...)")
    parser.add_argument("--modelos", nargs="+", choices=sorted(DETECTORS), help="detectores (padrão: todos)")
    parser.add_argument("--processos", type=int, default=1, help="sementes rodando ao mesmo tempo (memória!)")
    parser.add_argument("--saida", default="reports")
    parser.add_argument("--so-figuras", action="store_true",
                        help="não roda nada: redesenha as figuras a partir dos CSVs já salvos em --saida")
    args = parser.parse_args()
    began = time.time()
    results = Path(args.saida) / "results"
    figures = Path(args.saida) / "figures"

    if args.so_figuras:
        runs = pd.read_csv(results / "cenarios_execucoes.csv")
        summary = pd.read_csv(results / "cenarios_resumo.csv", index_col=[0, 1, 2, 3]).sort_index()
        comparisons = pd.read_csv(results / "cenarios_comparacoes.csv")
        effects = pd.read_csv(results / "cenarios_efeitos.csv")
        names = list(dict.fromkeys(runs["cenario"]))
    else:
        config = load_experiment_config(args.config)
        base = load_config(args.config)
        scenarios = load_scenarios(args.arquivo_cenarios)
        names = args.cenarios or list(scenarios)
        unknown = [n for n in names if n not in scenarios]
        if unknown:
            parser.error(f"cenários desconhecidos: {', '.join(unknown)} (existem: {', '.join(scenarios)})")
        runs, summary, comparisons, effects = _evaluate(config, base, {n: scenarios[n] for n in names},
                                                        args.sementes, args.modelos, args.processos)
        results.mkdir(parents=True, exist_ok=True)
        runs.to_csv(results / "cenarios_execucoes.csv", index=False)
        summary.to_csv(results / "cenarios_resumo.csv")
        comparisons.to_csv(results / "cenarios_comparacoes.csv", index=False)
        effects.to_csv(results / "cenarios_efeitos.csv", index=False)
        save_metadata(results / "cenarios_meta.json", config, cenarios={n: scenarios[n] for n in names},
                      sementes=list(range(1, args.sementes + 1)), modelos=args.modelos or list(DETECTORS),
                      duracao_s=round(time.time() - began))

    figures.mkdir(parents=True, exist_ok=True)
    fraud_rate = (runs["fraudes"] / runs["contas"]).groupby(runs["cenario"]).mean()
    _plot_metric(summary.loc["average_precision"], names, fraud_rate, figures / "cenarios_average_precision.png",
                 runs["semente"].nunique())
    _plot_effects(effects, names, figures / "cenarios_efeitos.png")

    ap = summary.loc["average_precision", "mean"].unstack("cenario")[names]
    ap = ap.reindex(list(FEATURE_SETS), level="atributos")
    print("\naverage precision média por cenário:")
    print(ap.round(3).to_string())
    print("\ncomparações pareadas (average precision, p com correção de Holm):")
    key = comparisons[(comparisons["métrica"] == "average_precision")
                      & comparisons["comparação"].isin(["grafo - tabular", "completo - tabular"])]
    columns = ["cenario", "modelo", "comparação", "diferença média", "ic_inferior", "ic_superior", "p Wilcoxon (Holm)"]
    print(key[columns].round(4).to_string(index=False))


def _evaluate(config: dict, base, scenarios: dict[str, dict], n_seeds: int, models: list[str] | None = None,
              processes: int = 1):
    """Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo, comparações e efeitos."""
    runs, effects = [], []
    for name, overrides in scenarios.items():
        simulation = with_overrides(base, overrides)
        for seed, prepared, metrics in run_seeds(simulation, config, range(1, n_seeds + 1), models=models,
                                                 processes=processes):
            n_fraud = int(prepared.labels.sum())
            runs.append(metrics.assign(cenario=name, fraudes=n_fraud, contas=len(prepared.labels)))
            delta = compare_groups(prepared.features, prepared.labels)["delta de Cliff"]
            effects.append(delta.rename_axis("atributo").reset_index().assign(cenario=name, semente=seed))
            print(f"{name}: semente {seed}/{n_seeds} concluída ({n_fraud} contas fraudulentas)", flush=True)

    runs = pd.concat(runs, ignore_index=True)
    first = ["cenario", "semente", "atributos", "modelo"]
    runs = runs[first + [c for c in runs.columns if c not in first]]
    summary = pd.concat(
        {m: summarize_runs(runs, m, by=["cenario"]) for m in REPEATED_METRICS}, names=["métrica"]
    )
    comparisons = compare_runs(runs, COMPARISONS, REPEATED_METRICS, by=["cenario"])
    effects = (
        pd.concat(effects, ignore_index=True)
        .groupby(["cenario", "atributo"], sort=False)["delta de Cliff"]
        .agg(delta_medio="mean", desvio="std")
        .reset_index()
    )
    effects["efeito"] = effects["delta_medio"].map(effect_size_label)
    return runs, summary, comparisons, effects


def _plot_metric(summary: pd.DataFrame, names: list, fraud_rate: pd.Series, path: Path, n: int) -> None:
    """Matriz conjunto de atributos × cenário da média da métrica, um painel por modelo.

    Com mais de 3 detectores, os painéis ficam numa grade de 2 colunas, para a
    figura não crescer só para baixo.
    """
    mean = summary["mean"]
    models = [m for m in DETECTORS if m in set(mean.index.get_level_values("modelo"))]
    sets = [s for s in FEATURE_SETS if s in set(mean.index.get_level_values("atributos"))]
    ncols = 2 if len(models) > 3 else 1
    nrows = -(-len(models) // ncols)
    cell = 1.05 if ncols == 1 else 0.8
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * (2.2 + cell * len(names)), 1.4 + 2.9 * nrows),
                             sharex=True, sharey=True, squeeze=False, layout="constrained")
    for ax in axes.flat[len(models):]:
        ax.set_visible(False)
    labels = [f"{c}\n{fraud_rate[c]:.1%} fraude".replace(".", ",") for c in names]
    for ax, model in zip(axes.flat, models):
        matrix = mean.xs(model, level="modelo").unstack("cenario").reindex(index=sets, columns=names)
        mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, fmt="{:.2f}", ax=ax)
        ax.set_title(model.replace("_", " "), color=INK, fontsize=10, loc="left")
        ax.set_yticks(np.arange(len(sets)) + 0.5, sets, fontsize=9)
        ax.set_xticks(np.arange(len(names)) + 0.5, labels, fontsize=7, rotation=90 if ncols > 1 else 0)
        ax.tick_params(labelbottom=True)
    colorbar = fig.colorbar(mesh, ax=axes, shrink=0.6, pad=0.02)
    colorbar.set_label("average precision", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    fig.suptitle(f"Average precision média ({n} sementes por cenário)\n"
                 "ao acaso, ela é igual à % de fraude", color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _plot_effects(effects: pd.DataFrame, names: list, path: Path) -> None:
    """Matriz atributo × cenário do delta de Cliff médio (> 0: maior nas contas fraudulentas)."""
    matrix = effects.pivot(index="atributo", columns="cenario", values="delta_medio")[names]
    order = [c for s in FEATURE_SETS.values() for c in s]
    matrix = matrix.reindex([c for c in dict.fromkeys(order) if c in matrix.index])
    fig, ax = plt.subplots(figsize=(2.6 + 1.05 * len(names), 0.34 * len(matrix) + 1.6), layout="constrained")
    mesh = plot_value_matrix(matrix, DIVERGING_CMAP, vmin=-1, vmax=1, fmt="{:+.2f}", ax=ax)
    colorbar = fig.colorbar(mesh, ax=ax, shrink=0.6, pad=0.02)
    colorbar.set_label("delta de Cliff: fraude × normal", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    ax.set_title("Delta de Cliff, fraude × normal\n"
                 "vermelho: maior nas fraudes · azul: menor\n|δ| ≥ 0,47: efeito grande",
                 color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
