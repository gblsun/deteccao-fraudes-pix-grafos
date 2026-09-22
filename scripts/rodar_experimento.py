"""Executa o experimento: grafo -> atributos -> detectores -> métricas e figuras.

Compara Isolation Forest e DBSCAN em cada conjunto de atributos de
``pixfraud.features.FEATURE_SETS``. Salva as métricas em
reports/results/metricas.csv e as figuras (grafo de calor e heatmap de risco)
em reports/figures/.

Uso:
    python scripts/rodar_experimento.py --config configs/experimento.yaml --dados data/synthetic
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from pixfraud.experiment import load_experiment_config, prepare, run_detectors  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import load_dataset  # noqa: E402
from pixfraud.visualization import plot_heat_graph, plot_risk_heatmap  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o experimento de detecção de fraudes.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--atributos", default="data/processed/features.csv")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    figures = Path(args.saida) / "figures"
    results = Path(args.saida) / "results"
    figures.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)

    accounts, transactions = load_dataset(args.dados)
    prepared = prepare(accounts, transactions, config)
    graph, features, y = prepared.graph, prepared.features, prepared.labels
    print(f"grafo: {graph.number_of_nodes()} vértices, {graph.number_of_edges()} arestas")
    Path(args.atributos).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.atributos)

    metrics, detections = run_detectors(features, y, config["modelos"])
    for (set_name, model_name), detection in detections.items():
        columns = FEATURE_SETS[set_name]
        fig, ax = plt.subplots(figsize=(10, 8))
        plot_heat_graph(graph, detection.scores, fraud=y, ax=ax)
        fig.savefig(figures / f"grafo_de_calor_{model_name}_{set_name}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(1.5 + 0.55 * len(columns), 8.5))
        plot_risk_heatmap(features[columns], detection.scores, fraud=y, ax=ax)
        fig.savefig(figures / f"heatmap_risco_{model_name}_{set_name}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    metrics.to_csv(results / "metricas.csv", index=False)
    print(metrics.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
