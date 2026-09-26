"""FRAUDAR: blocos densos acham as quadrilhas? E quando a rede legítima também é densa?

O FRAUDAR (Hooi et al., 2016) procura, um depois do outro, os subgrafos mais densos com
pesos que resistem a camuflagem (``pixfraud.communities.fraudar_blocks``). Não usa rótulos
nem atributos, só a estrutura do grafo. Este script compara, em cada cenário e semente:

* ``fraudar``: escore por conta = densidade do bloco em que ela está
  (``fraudar_scores``; blocos com mais de 5% das contas não pontuam);
* ``completo_dbscan``: o melhor detector não supervisionado de atributos;
* ``combinado``: média dos percentis dos dois.

Também mede o conjunto marcado pelo FRAUDAR (contas com escore > 0): quantas contas e que
fração das fraudes ele cobre.

Saídas em reports/results/: fraudar_execucoes.csv, fraudar_resumo.csv,
fraudar_comparacoes.csv e fraudar_meta.json, e a figura
reports/figures/fraudar_average_precision.png.

Uso:
    python scripts/avaliar_fraudar.py --sementes 10
    python scripts/avaliar_fraudar.py --cenarios base realista --sementes 3
"""

import argparse
import copy
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.communities import fraudar_scores  # noqa: E402
from pixfraud.experiment import load_experiment_config, load_scenarios, prepare, save_metadata  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

METHODS = ["fraudar", "completo_dbscan", "combinado"]
COMPARISONS = [("fraudar", "completo_dbscan"), ("combinado", "completo_dbscan")]
METRICS = ["average_precision", "precision_at_k"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia o FRAUDAR (blocos densos) contra os detectores.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["base", "sem_atalhos", "com_inativos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--blocos", type=int, default=10, help="nº máximo de blocos do FRAUDAR")
    parser.add_argument("--fatia-maxima", type=float, default=0.05,
                        help="blocos com mais que esta fração das contas não pontuam")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")

    rows = []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            prepared = prepare(accounts, tx, config)
            models = copy.deepcopy(config["modelos"])
            labels = prepared.labels
            fraudar = fraudar_scores(prepared.graph, args.blocos, max_share=args.fatia_maxima).reindex(labels.index)
            dbscan = DETECTORS["dbscan"](prepared.features[FEATURE_SETS["completo"]], **models.get("dbscan", {}))
            scores = {"fraudar": fraudar.fillna(0.0), "completo_dbscan": dbscan.scores.reindex(labels.index)}
            scores["combinado"] = (scores["fraudar"].rank(pct=True) + scores["completo_dbscan"].rank(pct=True)) / 2
            flagged = scores["fraudar"] > 0
            k = int(labels.sum())
            for method in METHODS:
                rows.append({
                    "cenario": name, "semente": seed, "atributos": method, "modelo": "-",
                    "average_precision": average_precision_score(labels, scores[method]),
                    "precision_at_k": float(labels[scores[method].nlargest(k).index].mean()),
                    "fraudes": k, "contas_marcadas": int(flagged.sum()),
                    "fraudes_marcadas": int((flagged & labels).sum()),
                })
            print(f"{name}: semente {seed}/{args.sementes}, {int(flagged.sum())} contas em blocos, "
                  f"{int((flagged & labels).sum())}/{k} fraudes", flush=True)

    runs = pd.DataFrame(rows)
    runs["cobertura"] = runs["fraudes_marcadas"] / runs["fraudes"]
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    summary = pd.concat({m: summarize_runs(runs, m, by=["cenario"]) for m in METRICS}, names=["métrica"])
    comparisons = compare_runs(runs, COMPARISONS, METRICS, by=["cenario"])
    # "atributos" e "modelo" são as colunas que stats espera; aqui a coluna certa é "metodo"
    runs.rename(columns={"atributos": "metodo"}).drop(columns="modelo").to_csv(
        results / "fraudar_execucoes.csv", index=False)
    summary.droplevel("modelo").rename_axis(index={"atributos": "metodo"}).to_csv(results / "fraudar_resumo.csv")
    comparisons.drop(columns="modelo").to_csv(results / "fraudar_comparacoes.csv", index=False)
    save_metadata(results / "fraudar_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), blocos=args.blocos, fatia_maxima=args.fatia_maxima,
                  duracao_s=round(time.time() - began))
    _plot(summary.loc["average_precision"], args, figures / "fraudar_average_precision.png")

    print("\naverage precision média:")
    print(summary.loc["average_precision", "mean"].droplevel("modelo").unstack("cenario")[args.cenarios]
          .round(3).to_string())
    marked = runs[runs["atributos"] == "fraudar"].groupby("cenario", sort=False)[["contas_marcadas", "cobertura"]]
    print("\nconjunto marcado pelo FRAUDAR (média por semente):")
    print(marked.mean().round(3).to_string())
    print("\ncomparações pareadas (average precision):")
    columns = ["cenario", "comparação", "diferença média", "a vence em", "p Wilcoxon (Holm)"]
    print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))


def _plot(summary: pd.DataFrame, args, path: Path) -> None:
    """Matriz método × cenário da AP média."""
    mean = summary["mean"].droplevel("modelo")
    matrix = pd.DataFrame({c: [mean.get((c, m), np.nan) for m in METHODS] for c in args.cenarios}, index=METHODS)
    fig, ax = plt.subplots(figsize=(2.8 + 1.2 * len(args.cenarios), 1.6 + 0.5 * len(METHODS)), layout="constrained")
    mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, ax=ax)
    colorbar = fig.colorbar(mesh, ax=ax, shrink=0.6, pad=0.02)
    colorbar.set_label("average precision", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    ax.set_title(f"FRAUDAR contra o melhor detector: AP média ({args.sementes} sementes)",
                 color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
