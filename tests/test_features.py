import pandas as pd
import pytest

from pixfraud.features import build_features
from pixfraud.graph import build_graph


@pytest.fixture
def chain():
    """Cadeia A -> B -> C -> D, um pagamento extra E -> B e uma conta F sem transações."""
    transactions = pd.DataFrame({
        "sender": ["A", "A", "B", "C", "E"],
        "receiver": ["B", "B", "C", "D", "B"],
        "amount": [60.0, 40.0, 95.0, 90.0, 10.0],
        "timestamp": pd.to_datetime([
            "2026-01-01 10:00", "2026-01-01 10:05", "2026-01-01 10:30", "2026-01-01 03:00", "2026-01-01 12:00",
        ]),
    })
    accounts = pd.DataFrame({"account_id": list("ABCDEF"), "account_age_days": [100] * 6})
    return transactions, accounts


def test_graph_aggregates_repeated_pairs(chain):
    transactions, accounts = chain
    graph = build_graph(transactions, accounts["account_id"])
    assert graph.number_of_nodes() == 6
    assert graph["A"]["B"] == {"amount": 100.0, "count": 2}


def test_features(chain):
    transactions, accounts = chain
    graph = build_graph(transactions, accounts["account_id"])
    features = build_features(transactions, accounts, graph, betweenness_k=None)

    assert features.loc["B", "in_degree"] == 2
    assert features.loc["B", "out_degree"] == 1
    assert features.loc["B", "betweenness"] > 0
    assert features.loc["A", "betweenness"] == 0
    assert features.loc["C", "pass_through"] == pytest.approx(90 / 95)
    assert features.loc["C", "night_ratio"] == pytest.approx(0.5)
    # conta sem transações: tudo zero, exceto a idade, o PageRank (que distribui uma massa mínima a
    # todos) e o tempo de permanência (quem nunca repassa recebe o valor máximo)
    assert (features.loc["F"].drop(["account_age_days", "pagerank", "dwell_time_min"]) == 0).all()
    assert features.loc["F", "dwell_time_min"] == features["dwell_time_min"].max()
