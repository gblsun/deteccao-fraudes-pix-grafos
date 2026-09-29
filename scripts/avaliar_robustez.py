"""Avalia a robustez do experimento repetindo-o com várias sementes.

Cada semente gera um dataset sintético diferente (e muda a semente dos
detectores aleatórios). Para cada conjunto de atributos e modelo, o script calcula
a média e o intervalo de confiança das métricas. Depois compara abordagens
com testes pareados (a mesma semente é avaliada pelas duas abordagens), com
correção de Holm para as várias comparações de cada métrica. Para repetir a
avaliação em cenários de dificuldade diferentes, use ``avaliar_cenarios.py``.

Saídas em reports/results/:
    robustez_execucoes.csv    uma linha por (semente, atributos, modelo)
    robustez_resumo.csv       média, desvio e IC de cada métrica
    robustez_comparacoes.csv  testes pareados entre conjuntos de atributos
e a figura reports/figures/robustez_<métrica>.png.

Uso:
    python scripts/avaliar_robustez.py --sementes 20 --processos 3
    python scripts/avaliar_robustez.py --modelos isolation_forest ecod   # só alguns detectores
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
    run_seeds,
    save_metadata,
)
from pixfraud.simulation import load_config  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import model_color  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Repete o experimento com várias sementes.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--sementes", type=int, default=20, help="nº de repetições (sementes 1, 2, ...)")
    parser.add_argument("--modelos", nargs="+", choices=sorted(DETECTORS), help="detectores (padrão: todos)")
    parser.add_argument("--processos", type=int, default=1, help="sementes rodando ao mesmo tempo (memória!)")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    runs = []
    for seed, _, metrics in run_seeds(base, config, range(1, args.sementes + 1), models=args.modelos,
                                     processes=args.processos):
        runs.append(metrics)
        print(f"semente {seed}/{args.sementes} concluída")
    runs = pd.concat(runs, ignore_index=True)

    results = Path(args.saida) / "results"
    figures = Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "robustez_execucoes.csv", index=False)

    summary = pd.concat({m: summarize_runs(runs, m) for m in REPEATED_METRICS}, names=["métrica"])
    summary.to_csv(results / "robustez_resumo.csv")

    comparisons = compare_runs(runs, COMPARISONS, REPEATED_METRICS)
    comparisons.to_csv(results / "robustez_comparacoes.csv", index=False)
    save_metadata(results / "robustez_meta.json", config, sementes=list(range(1, args.sementes + 1)),
                  modelos=args.modelos or list(DETECTORS), duracao_s=round(time.time() - began))

    _plot(summary.loc["average_precision"], figures / "robustez_average_precision.png", args.sementes)
    print("\naverage precision (média e IC 95%):")
    print(summary.loc["average_precision"].round(3).to_string())
    print("\ncomparações pareadas (average precision):")
    columns = ["modelo", "comparação", "diferença média", "ic_inferior", "ic_superior", "p Wilcoxon (Holm)"]
    print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))


def _plot(summary: pd.DataFrame, path: Path, n: int) -> None:
    table = summary.reset_index()
    order = table.groupby("atributos")["mean"].max().sort_values().index
    models = [m for m in DETECTORS if m in set(table["modelo"])]
    # uma posição por detector dentro de cada conjunto de atributos
    offsets = np.linspace(-0.32, 0.32, len(models)) if len(models) > 1 else [0.0]
    fig, ax = plt.subplots(figsize=(8, 1.5 + len(order) * (0.3 + 0.12 * len(models))))
    for offset, model in zip(offsets, models):
        group = table[table["modelo"] == model].set_index("atributos").loc[order]
        y = np.arange(len(order)) + offset
        ax.errorbar(group["mean"], y,
                    xerr=[group["mean"] - group["ic_inferior"], group["ic_superior"] - group["mean"]],
                    fmt="o", ms=4, capsize=2, color=model_color(model), label=model)
    ax.set_yticks(range(len(order)), order)
    ax.set_xlabel(f"average precision (média e IC 95%, {n} sementes)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
