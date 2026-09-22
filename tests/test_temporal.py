from pathlib import Path

import networkx as nx
import pandas as pd
import pytest

from pixfraud.graph import build_graph
from pixfraud.temporal import (
    dwell_time,
    temporal_features,
    temporal_reachability,
    temporal_trail,
    temporal_trail_transactions,
    windowed_in_degree,
)

DADOS = Path(__file__).parents[1] / "estudos" / "dados"


@pytest.fixture(scope="module")
def tx():
    return pd.read_csv(DADOS / "exemplo_transacoes.csv", parse_dates=["timestamp"])


def test_backward_reachability_respects_time(tx):
    # davi e elisa alcançam conta_x no grafo estático, mas só por Pix fora de ordem
    static = nx.ancestors(build_graph(tx), "conta_x")
    temporal = temporal_reachability(tx, "conta_x", direction="backward")
    assert {"davi", "elisa"} <= static
    assert set(temporal.index) == {"ana", "bruno", "carla", "fabio"}
    assert temporal["bruno"] == pd.Timestamp("2026-03-02 19:40")


def test_forward_reachability_gives_earliest_arrival(tx):
    arrival = temporal_reachability(tx, "ana", direction="forward")
    assert arrival["conta_z"] == pd.Timestamp("2026-03-06 11:02")
    assert "elisa" in nx.descendants(build_graph(tx), "ana")
    assert "elisa" not in arrival.index  # davi -> elisa acontece antes de o dinheiro chegar em davi


def test_trail_with_max_delay_and_hops(tx):
    slow = temporal_trail_transactions(tx, "carla", max_delay="1h")
    assert "conta_y" not in set(slow["receiver"])  # conta_x só repassa 8h depois
    fast = temporal_trail(tx, "carla", max_delay="12h")
    assert fast.has_edge("conta_x", "conta_y") and fast.has_edge("conta_y", "conta_z")
    one_hop = temporal_trail_transactions(tx, "carla", max_hops=1)
    assert set(one_hop["sender"]) == {"carla"}
    with pytest.raises(ValueError):
        temporal_reachability(tx, "ana", direction="sideways")


def test_dwell_time_and_windows(tx):
    dwell = dwell_time(tx)
    assert dwell["conta_x"] == pytest.approx(499.0)  # esperas de 506, 499 e 35 minutos
    assert dwell["conta_y"] == pytest.approx(22.0)
    assert "conta_z" not in dwell.index  # nunca repassa
    windows = windowed_in_degree(tx)
    assert windows.loc[pd.Timestamp("2026-03-03"), "padaria"] == 2


def test_temporal_features(tx):
    accounts = pd.DataFrame({"account_id": sorted(set(tx["sender"]) | set(tx["receiver"]))})
    features = temporal_features(tx, accounts)
    span = (tx["timestamp"].max() - tx["timestamp"].min()).total_seconds() / 60
    assert features.loc["conta_z", "dwell_time_min"] == pytest.approx(span)
    assert features.loc["conta_x", "max_daily_in_degree"] == 2
    assert list(features.columns) == ["dwell_time_min", "max_daily_in_degree"]
