"""Avalia os detectores num dataset externo (AMLworld), janela por janela.

Usa a mesma configuração do dataset sintético (configs/experimento.yaml), sem
reajustar nada. Cada janela de --dias-janela dias é uma repetição, no lugar das
sementes: as comparações entre conjuntos de atributos são pareadas por janela.
Se a pasta de dados tiver patterns.csv (importar_dataset.py --padroes), mede
também o recall@k de cada tipologia de lavagem.

Saídas em <saida>/results/, com o nome da pasta de dados como prefixo:
    <nome>_execucoes.csv     uma linha por (janela, atributos, modelo)
    <nome>_resumo.csv        média, desvio e IC 95% de cada métrica
    <nome>_comparacoes.csv   testes pareados entre conjuntos de atributos
    <nome>_tipologias.csv    recall@k por tipologia (se houver patterns.csv)
e a figura <saida>/figures/<nome>_tipologias.png.

Uso:
    python scripts/04_avaliacao/avaliar_externo.py --dados data/external/amlworld_pix --saida reports/amlworld
    python scripts/04_avaliacao/avaliar_externo.py --dados data/external/amlworld --max-janelas 1   # teste rápido

Cada janela é salva em <saida>/results/<nome>_janelas/ assim que termina. Se a
execução for interrompida, rodar de novo reaproveita as janelas prontas
(--refazer recalcula tudo, por exemplo depois de mudar a configuração).
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
from pixfraud.evaluation import recall_by_group  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    COMPARISONS,
    REPEATED_METRICS,
    load_experiment_config,
    prepare,
    run_detectors,
    save_metadata,
)
from pixfraud.external import time_windows  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import load_dataset  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia os detectores num dataset externo, por janelas de tempo.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", required=True, help="pasta com accounts.csv e transactions.csv (e patterns.csv)")
    parser.add_argument("--dias-janela", type=int, default=3)
    parser.add_argument("--min-fraudes", type=int, default=20, help="pula janelas com menos contas fraudulentas")
    parser.add_argument("--max-fracao-fraude", type=float, default=0.2,
                        help="pula janelas em que as contas fraudulentas passam dessa fração (sem movimento normal)")
    parser.add_argument("--max-janelas", type=int, help="para depois de N janelas avaliadas (teste rápido)")
    parser.add_argument("--modelos", nargs="+", choices=sorted(DETECTORS), help="detectores (padrão: todos)")
    parser.add_argument("--saida", default="reports/externo")
    parser.add_argument("--refazer", action="store_true", help="recalcula as janelas já salvas")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    models = args.modelos or list(DETECTORS)
    data = Path(args.dados)
    name = data.name
    _, transactions = load_dataset(data)
    members = pd.read_csv(data / "patterns.csv") if (data / "patterns.csv").exists() else None
    # Cada janela é salva assim que termina; ao rodar de novo, as prontas são reaproveitadas.
    cache = Path(args.saida) / "results" / f"{name}_janelas"
    cache.mkdir(parents=True, exist_ok=True)

    runs, recalls = [], []
    for i, (start, accounts, tx) in enumerate(time_windows(transactions, args.dias_janela), start=1):
        n_fraud = int(accounts["is_fraud"].sum())
        if n_fraud < args.min_fraudes or n_fraud > args.max_fracao_fraude * len(accounts):
            print(f"janela {i} ({start.date()}): {n_fraud} de {len(accounts)} contas fraudulentas, pulada")
            continue
        metrics_file, typology_file = cache / f"janela_{i:02d}.csv", cache / f"janela_{i:02d}_tipologias.csv"
        cached = pd.read_csv(metrics_file) if metrics_file.exists() and not args.refazer else None
        cached_recalls = pd.read_csv(typology_file) if cached is not None and typology_file.exists() else None
        # Uma janela salva antes de um detector existir é completada só com o que falta.
        missing = models if cached is None else [m for m in models if m not in set(cached["modelo"])]
        if not missing:
            runs.append(cached[cached["modelo"].isin(models)])
            if cached_recalls is not None:
                recalls.append(cached_recalls[cached_recalls["modelo"].isin(models)])
            print(f"janela {i} ({start.date()}): já calculada, reaproveitada", flush=True)
        else:
            window_began = time.time()
            prepared = prepare(accounts, tx, config)
            metrics, detections = run_detectors(prepared.features, prepared.labels, config["modelos"], models=missing)
            metrics = metrics.assign(janela=i, inicio=start.date(), fraudes=n_fraud, contas=len(accounts))
            if cached is not None:
                metrics = pd.concat([cached, metrics], ignore_index=True)
            if members is not None:
                fraud = members[members["account_id"].isin(prepared.labels.index[prepared.labels])]
                window_recalls = pd.concat(
                    [cached_recalls] * (cached_recalls is not None)
                    + [recall_by_group(fraud, detection.scores, k=n_fraud).assign(janela=i, atributos=s, modelo=m)
                       for (s, m), detection in detections.items()],
                    ignore_index=True,
                )
                window_recalls.to_csv(typology_file, index=False)
                recalls.append(window_recalls[window_recalls["modelo"].isin(models)])
            metrics.to_csv(metrics_file, index=False)  # por último: marca a janela como pronta
            runs.append(metrics[metrics["modelo"].isin(models)])
            size = f"{len(accounts):,} contas e {len(tx):,} transações".replace(",", ".")
            print(f"janela {i} ({start.date()}): {size}, {n_fraud} fraudulentas, "
                  f"{time.time() - window_began:.0f} s", flush=True)
        if args.max_janelas and len(runs) >= args.max_janelas:
            break
    if not runs:
        parser.error("nenhuma janela com contas fraudulentas suficientes (veja --min-fraudes)")

    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs = pd.concat(runs, ignore_index=True)
    first = ["janela", "inicio", "atributos", "modelo"]
    runs = runs[first + [c for c in runs.columns if c not in first]]
    runs.to_csv(results / f"{name}_execucoes.csv", index=False)
    summary = pd.concat({m: summarize_runs(runs, m) for m in REPEATED_METRICS}, names=["métrica"])
    summary.to_csv(results / f"{name}_resumo.csv")
    save_metadata(results / f"{name}_meta.json", config, dados=str(data), dias_janela=args.dias_janela,
                  janelas=sorted(runs["janela"].unique().tolist()), modelos=models,
                  duracao_s=round(time.time() - began))
    print("\naverage precision média por janela:")
    print(summary.loc["average_precision"].round(3).to_string())

    if runs["janela"].nunique() > 1:
        comparisons = compare_runs(runs, COMPARISONS, REPEATED_METRICS, unit="janela")
        comparisons.to_csv(results / f"{name}_comparacoes.csv", index=False)
        print("\ncomparações pareadas por janela (average precision):")
        columns = ["modelo", "comparação", "diferença média", "a vence em", "n", "p Wilcoxon (Holm)"]
        print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))

    if recalls:
        typologies = _pool(pd.concat(recalls, ignore_index=True))
        typologies.to_csv(results / f"{name}_tipologias.csv", index=False)
        _plot_typologies(typologies, figures / f"{name}_tipologias.png", name)
        print("\nrecall@k por tipologia (todas as janelas juntas):")
        print(typologies.pivot_table(index="typology", columns=["modelo", "atributos"], values="recall_at_k")
              .round(2).to_string())


def _pool(recalls: pd.DataFrame) -> pd.DataFrame:
    """Junta as janelas: acertos somados sobre contas somadas, por tipologia, atributos e modelo."""
    recalls = recalls.assign(acertos=recalls["contas"] * recalls["recall_at_k"])
    pooled = recalls.groupby(["typology", "atributos", "modelo"], as_index=False)[["contas", "acertos"]].sum()
    pooled["recall_at_k"] = pooled["acertos"] / pooled["contas"]
    return pooled.drop(columns="acertos")


def _plot_typologies(typologies: pd.DataFrame, path: Path, name: str) -> None:
    """Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo."""
    models = [m for m in DETECTORS if m in set(typologies["modelo"])]
    sets = [s for s in FEATURE_SETS if s in set(typologies["atributos"])]
    counts = typologies.groupby("typology")["contas"].max()
    fig, axes = plt.subplots(len(models), 1, figsize=(2.8 + 0.95 * len(sets), 1.4 + 0.45 * len(counts) * len(models)),
                             sharex=True, layout="constrained")
    axes = np.atleast_1d(axes)
    for ax, model in zip(axes, models):
        matrix = typologies[typologies["modelo"] == model].pivot(index="typology", columns="atributos",
                                                                 values="recall_at_k").reindex(columns=sets)
        mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, ax=ax)
        ax.set_yticks(np.arange(len(matrix)) + 0.5, [f"{t} ({counts[t]})" for t in matrix.index], fontsize=8)
        ax.set_title(model.replace("_", " "), color=INK, fontsize=10, loc="left")
    colorbar = fig.colorbar(mesh, ax=axes, shrink=0.6, pad=0.02)
    colorbar.set_label("recall@k", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    fig.suptitle(f"{name}: fração das contas de cada tipologia entre as k mais suspeitas\n"
                 "(k = nº de contas fraudulentas da janela; entre parênteses, nº de contas)", color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
