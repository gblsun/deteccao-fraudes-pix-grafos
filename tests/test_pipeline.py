"""Teste de fumaça: o pipeline completo roda de ponta a ponta num dataset pequeno."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.evaluation import evaluate  # noqa: E402
from pixfraud.features import FEATURE_SETS, build_features  # noqa: E402
from pixfraud.graph import build_graph  # noqa: E402
from pixfraud.simulation import SimulationConfig, generate_dataset  # noqa: E402
from pixfraud.visualization import plot_heat_graph, plot_risk_heatmap  # noqa: E402


def test_pipeline_end_to_end():
    accounts, transactions = generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=7, n_rings=2))
    graph = build_graph(transactions, accounts["account_id"])
    features = build_features(transactions, accounts, graph, betweenness_k=100)
    y = accounts.set_index("account_id")["is_fraud"]
    assert len(features) == len(accounts)

    for columns in FEATURE_SETS.values():
        for detect in DETECTORS.values():
            detection = detect(features[columns])
            metrics = evaluate(y, detection)
            assert 0 <= metrics["roc_auc"] <= 1

    plot_heat_graph(graph, detection.scores, fraud=y)
    plot_risk_heatmap(features, detection.scores, fraud=y)
    plt.close("all")
