"""Redes neurais para grafos: aprender a estrutura ajuda a achar fraude?

Compara, em cada cenário e semente, as GNN de ``pixfraud.gnn`` com o que o projeto
já tinha:

* não supervisionados (sem rótulos): ``dominant_tabular`` e ``dominant_completo``
  (autoencoder de grafo DOMINANT com os atributos tabulares ou com todos) contra
  ``completo_dbscan``, o melhor detector de atributos;
* supervisionados (tetos, em validação cruzada de 5 dobras): ``sage_tabular`` e
  ``sage_completo`` (GraphSAGE) contra ``rf_tabular`` e ``rf_completo`` (o Random Forest
  de ``avaliar_atributos.py``). A pergunta do ``tabular``: com os mesmos atributos
  simples, a GNN aprende sozinha o que os atributos de grafo feitos à mão capturam?

Precisa do torch: ``pip install -e ".[gnn]"``.

Saídas em reports/04_avaliacao/results/: gnn_execucoes.csv, gnn_resumo.csv, gnn_comparacoes.csv e
gnn_meta.json, e a figura reports/04_avaliacao/figures/gnn_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_gnn.py --sementes 10
    python scripts/04_avaliacao/avaliar_gnn.py --cenarios realista --sementes 3
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
from pixfraud.experiment import (  # noqa: E402
    load_experiment_config,
    load_scenarios,
    prepare,
    save_metadata,
    supervised_scores,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.gnn import dominant_scores, sage_supervised_scores  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

METHODS = ["completo_dbscan", "dominant_tabular", "dominant_completo",
           "rf_tabular", "sage_tabular", "rf_completo", "sage_completo"]
COMPARISONS = [
    ("sage_tabular", "rf_tabular"),
    ("sage_completo", "rf_completo"),
    ("sage_tabular", "rf_completo"),
    ("dominant_completo", "completo_dbscan"),
]
METRICS = ["average_precision", "precision_at_k"]


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Avalia redes neurais para grafos (DOMINANT e GraphSAGE).")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--epocas", type=int, default=None, help="épocas de treino (padrão: as de pixfraud.gnn)")
    parser.add_argument("--saida", default="reports/04_avaliacao")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    epochs = {"epochs": args.epocas} if args.epocas else {}

    rows = []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            seed_began = time.time()
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            prepared = prepare(accounts, tx, config)
            models = copy.deepcopy(config["modelos"])
            labels = prepared.labels
            graph = prepared.graph
            tabular = prepared.features[FEATURE_SETS["tabular"]]
            completo = prepared.features[FEATURE_SETS["completo"]]
            scores = {
                "completo_dbscan": DETECTORS["dbscan"](completo, **models.get("dbscan", {})).scores,
                "dominant_tabular": dominant_scores(graph, tabular, seed=seed, **epochs),
                "dominant_completo": dominant_scores(graph, completo, seed=seed, **epochs),
                "rf_tabular": supervised_scores(tabular, labels, seed=seed),
                "sage_tabular": sage_supervised_scores(graph, tabular, labels, seed=seed, **epochs),
                "rf_completo": supervised_scores(completo, labels, seed=seed),
                "sage_completo": sage_supervised_scores(graph, completo, labels, seed=seed, **epochs),
            }
            k = int(labels.sum())
            for method in METHODS:
                score = scores[method].reindex(labels.index)
                rows.append({
                    "cenario": name, "semente": seed, "atributos": method, "modelo": "-",
                    "supervisionado": method.startswith(("rf_", "sage_")),
                    "average_precision": average_precision_score(labels, score),
                    "precision_at_k": float(labels[score.nlargest(k).index].mean()),
                })
            print(f"{name}: semente {seed}/{args.sementes}, {time.time() - seed_began:.0f} s", flush=True)

    runs = pd.DataFrame(rows)
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    summary = pd.concat({m: summarize_runs(runs, m, by=["cenario"]) for m in METRICS}, names=["métrica"])
    comparisons = compare_runs(runs, COMPARISONS, METRICS, by=["cenario"])
    # "atributos" e "modelo" são as colunas que stats espera; aqui a coluna certa é "metodo"
    runs.rename(columns={"atributos": "metodo"}).drop(columns="modelo").to_csv(
        results / "gnn_execucoes.csv", index=False)
    summary.droplevel("modelo").rename_axis(index={"atributos": "metodo"}).to_csv(results / "gnn_resumo.csv")
    comparisons.drop(columns="modelo").to_csv(results / "gnn_comparacoes.csv", index=False)
    save_metadata(results / "gnn_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), epocas=args.epocas,
                  duracao_s=round(time.time() - began))
    _plot(summary.loc["average_precision"], args, figures / "gnn_average_precision.png")

    print("\naverage precision média:")
    print(summary.loc["average_precision", "mean"].droplevel("modelo").unstack("cenario")[args.cenarios]
          .reindex(METHODS).round(3).to_string())
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
    ax.set_title(f"GNN contra detectores e Random Forest: AP média ({args.sementes} sementes)",
                 color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
