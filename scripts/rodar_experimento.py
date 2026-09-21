"""Executa o experimento: grafo -> atributos -> detectores -> métricas e figuras.

Compara Isolation Forest e DBSCAN usando atributos tabulares, de grafo e
combinados. Salva as métricas em reports/results/metricas.csv e as figuras
(grafo de calor e heatmap de risco) em reports/figures/.

Uso:
    python scripts/rodar_experimento.py --config configs/experimento.yaml --dados data/synthetic
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.evaluation import evaluate  # noqa: E402
from pixfraud.features import FEATURE_SETS, build_features  # noqa: E402
from pixfraud.graph import build_graph  # noqa: E402
from pixfraud.simulation import load_dataset  # noqa: E402
from pixfraud.visualization import plot_heat_graph, plot_risk_heatmap  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa o experimento de detecção de fraudes.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--atributos", default="data/processed/features.csv")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    figures = Path(args.saida) / "figures"
    results = Path(args.saida) / "results"
    figures.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)

    accounts, transactions = load_dataset(args.dados)
    graph = build_graph(transactions, accounts["account_id"])
    print(f"grafo: {graph.number_of_nodes()} vértices, {graph.number_of_edges()} arestas")

    features = build_features(transactions, accounts, graph, **config["atributos"])
    Path(args.atributos).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.atributos)
    y = accounts.set_index("account_id")["is_fraud"]

    rows = []
    for set_name, columns in FEATURE_SETS.items():
        for model_name, detect in DETECTORS.items():
            detection = detect(features[columns], **config["modelos"][model_name])
            rows.append({"atributos": set_name, "modelo": model_name, **evaluate(y, detection)})

            fig, ax = plt.subplots(figsize=(10, 8))
            plot_heat_graph(graph, detection.scores, fraud=y, ax=ax)
            fig.savefig(figures / f"grafo_de_calor_{model_name}_{set_name}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(1.5 + 0.55 * len(columns), 8.5))
            plot_risk_heatmap(features[columns], detection.scores, fraud=y, ax=ax)
            fig.savefig(figures / f"heatmap_risco_{model_name}_{set_name}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(results / "metricas.csv", index=False)
    print(metrics.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
