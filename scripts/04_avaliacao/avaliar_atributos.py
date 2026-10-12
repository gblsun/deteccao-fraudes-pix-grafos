"""Quanto cada atributo contribui, e quão longe estamos de um modelo que viu os rótulos?

Duas análises, nos cenários escolhidos e com várias sementes:

* **ablação**: tira um atributo de cada vez do conjunto (padrão: ``completo``) e
  mede a queda da average precision de cada detector;
* **teto supervisionado**: modelos treinados com os rótulos (validação cruzada
  de 5 partes), ao lado dos detectores não supervisionados: Random Forest e
  gradient boosting em cada conjunto de atributos, e, se o extra ``gnn`` estiver
  instalado, uma GraphSAGE com os atributos ``tabular`` e ``completo`` (ela
  aprende a estrutura do grafo sozinha, então dá para ver se isso supre a
  falta dos atributos de grafo).

Saídas em reports/04_avaliacao/results/:
    atributos_ablacao.csv          uma linha por (cenário, semente, modelo, atributo removido)
    atributos_ablacao_resumo.csv   queda média de AP por (cenário, modelo, atributo)
    atributos_teto.csv             AP de cada (cenário, semente, conjunto, modelo), com o supervisionado
    atributos_teto_resumo.csv      média e IC 95% da AP
    atributos_meta.json            como o resultado foi gerado
e as figuras reports/04_avaliacao/figures/atributos_ablacao.png e atributos_teto.png.

Uso:
    python scripts/04_avaliacao/avaliar_atributos.py --sementes 5
    python scripts/04_avaliacao/avaliar_atributos.py --cenarios realista --sementes 2 --conjunto grafo_avancado
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from pixfraud import gnn  # noqa: E402
from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    SUPERVISED_MODELS,
    feature_ablation,
    load_experiment_config,
    load_scenarios,
    prepare,
    run_detectors,
    save_metadata,
    seeded_models,
    supervised_scores,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import summarize_runs  # noqa: E402
from pixfraud.visualization import (  # noqa: E402
    DIVERGING_CMAP,
    INK,
    INK_SECONDARY,
    SEQUENTIAL_CMAP,
    SURFACE,
    model_label,
    plot_value_matrix,
)

GNN_SETS = ["tabular", "completo"]  # conjuntos em que a GraphSAGE roda (é o teto mais caro)


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Ablação por atributo e teto supervisionado.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--conjunto", default="completo", choices=list(FEATURE_SETS),
                        help="conjunto de atributos da ablação")
    parser.add_argument("--modelos", nargs="+", choices=sorted(DETECTORS), help="detectores (padrão: todos)")
    parser.add_argument("--saida", default="reports/04_avaliacao")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    use_gnn = gnn.available()
    if not use_gnn:
        print("aviso: sem o extra 'gnn' (PyTorch Geometric), o teto da GraphSAGE fica de fora", flush=True)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")

    ablations, ceilings = [], []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            seed_began = time.time()
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            prepared = prepare(accounts, tx, config)
            models = seeded_models(config["modelos"], seed)
            ids = {"cenario": name, "semente": seed}

            ablation = feature_ablation(prepared.features, prepared.labels, FEATURE_SETS[args.conjunto], models,
                                        args.modelos)
            ablations.append(ablation.assign(**ids))

            metrics, _ = run_detectors(prepared.features, prepared.labels, models, models=args.modelos)
            ceilings.append(metrics[["atributos", "modelo", "average_precision"]].assign(**ids))
            supervised = [(s, m, lambda c=c, m=m: supervised_scores(prepared.features[c], prepared.labels,
                                                                     seed=seed, model=m))
                          for s, c in FEATURE_SETS.items() for m in SUPERVISED_MODELS]
            if use_gnn:
                supervised += [(s, "graphsage", lambda s=s: gnn.graphsage_scores(
                    prepared.graph, prepared.features[FEATURE_SETS[s]], prepared.labels, seed=seed))
                    for s in GNN_SETS]
            for set_name, model_name, fit in supervised:
                scores = fit()
                ap = average_precision_score(prepared.labels.reindex(scores.index), scores)
                ceilings.append(pd.DataFrame([{"atributos": set_name, "modelo": model_name,
                                               "average_precision": ap, **ids}]))
            print(f"{name}: semente {seed}/{args.sementes}, {time.time() - seed_began:.0f} s", flush=True)

    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    ablations = pd.concat(ablations, ignore_index=True)
    ablations.to_csv(results / "atributos_ablacao.csv", index=False)
    ablation_summary = (ablations.groupby(["cenario", "modelo", "atributo"], sort=False)["queda"]
                        .agg(queda_media="mean", desvio="std").reset_index())
    ablation_summary.to_csv(results / "atributos_ablacao_resumo.csv", index=False)
    ceilings = pd.concat(ceilings, ignore_index=True)
    ceilings.to_csv(results / "atributos_teto.csv", index=False)
    ceiling_summary = summarize_runs(ceilings, "average_precision", by=["cenario"])
    ceiling_summary.to_csv(results / "atributos_teto_resumo.csv")
    save_metadata(results / "atributos_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), conjunto=args.conjunto,
                  modelos=args.modelos or list(DETECTORS),
                  duracao_s=round(time.time() - began))

    _plot_ablation(ablation_summary, args, figures / "atributos_ablacao.png")
    _plot_ceiling(ceiling_summary, args, figures / "atributos_teto.png")

    print(f"\nqueda média de AP ao tirar cada atributo de '{args.conjunto}':")
    print(ablation_summary.pivot_table(index="atributo", columns=["cenario", "modelo"], values="queda_media",
                                       sort=False).round(3).to_string())
    print("\naverage precision média (com o teto supervisionado):")
    print(ceiling_summary["mean"].unstack("cenario")[args.cenarios].round(3).to_string())


def _plot_ablation(summary: pd.DataFrame, args, path: Path) -> None:
    """Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo."""
    matrix = summary.pivot_table(index="atributo", columns=["cenario", "modelo"], values="queda_media", sort=False)
    matrix = matrix.reindex(FEATURE_SETS[args.conjunto])
    matrix.columns = [f"{c}\n{m.replace('_', ' ')}" for c, m in matrix.columns]
    limit = max(0.05, float(np.nanmax(np.abs(matrix.to_numpy()))))
    fig, ax = plt.subplots(figsize=(2.4 + 1.3 * matrix.shape[1], 0.34 * len(matrix) + 1.8), layout="constrained")
    mesh = plot_value_matrix(matrix, DIVERGING_CMAP, vmin=-limit, vmax=limit, fmt="{:+.3f}", ax=ax)
    colorbar = fig.colorbar(mesh, ax=ax, shrink=0.6, pad=0.02)
    colorbar.set_label("queda de AP ao tirar o atributo", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    ax.set_title(f"Ablação do conjunto '{args.conjunto}' ({args.sementes} sementes)\n"
                 "vermelho: o atributo ajudava · azul: atrapalhava", color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _plot_ceiling(summary: pd.DataFrame, args, path: Path) -> None:
    """Um painel por cenário: conjunto de atributos × modelo, da AP média (tetos supervisionados à direita)."""
    mean = summary["mean"]
    present = set(mean.index.get_level_values("modelo"))
    models = [m for m in [*DETECTORS, *SUPERVISED_MODELS, "graphsage"] if m in present]
    fig, axes = plt.subplots(len(args.cenarios), 1, figsize=(2.6 + 0.95 * len(models), 0.6 + 3.2 * len(args.cenarios)),
                             squeeze=False, layout="constrained")
    for ax, scenario in zip(axes[:, 0], args.cenarios):
        matrix = pd.DataFrame({model_label(m): [mean.get((scenario, s, m), np.nan) for s in FEATURE_SETS]
                               for m in models}, index=list(FEATURE_SETS))
        mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, ax=ax)
        ax.tick_params(axis="x", labelrotation=30)
        ax.set_title(scenario, color=INK, fontsize=10, loc="left")
    colorbar = fig.colorbar(mesh, ax=axes, shrink=0.6, pad=0.02)
    colorbar.set_label("average precision", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    fig.suptitle(f"Não supervisionados × tetos supervisionados (treinados com os rótulos), {args.sementes} sementes",
                 color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
