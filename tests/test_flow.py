"""Testes de `pixfraud.flow`: fluxo máximo, corte mínimo, contas a bloquear e propagação de risco."""

from pathlib import Path

import pytest

from pixfraud.flow import blocking_accounts, blocking_cut, max_money_flow, propagate_risk
from pixfraud.graph import build_graph, graph_from_csv
from pixfraud.simulation import SimulationConfig, generate_dataset

EXEMPLO = Path(__file__).parents[1] / "estudos" / "dados" / "exemplo_transacoes.csv"


@pytest.fixture(scope="module")
def A():
    return graph_from_csv(EXEMPLO)


def test_max_flow_equals_min_cut(A):
    value, flow = max_money_flow(A, ["carla", "fabio"], "conta_z")
    cut_value, cut = blocking_cut(A, ["carla", "fabio"], "conta_z")
    assert value == pytest.approx(3300.0)  # gargalo: conta_y -> conta_z
    assert cut_value == pytest.approx(value)
    assert cut == [("conta_y", "conta_z", 3300.0)]
    assert flow["conta_y"]["conta_z"] == pytest.approx(3300.0)


def test_single_source_is_limited_by_its_route(A):
    # o dinheiro de ana só chega à quadrilha pelo Pix bruno -> carla (R$ 30)
    value, _ = max_money_flow(A, "ana", "conta_z")
    assert value == pytest.approx(30.0)
    assert blocking_cut(A, "ana", "conta_z")[1] == [("bruno", "carla", 30.0)]


def test_blocking_accounts(A):
    accounts = blocking_accounts(A, ["carla", "fabio"], "conta_z")
    assert len(accounts) == 1 and accounts[0] in {"conta_x", "conta_y"}
    assert blocking_accounts(A, "conta_y", "conta_z") is None  # pagamento direto
    assert max_money_flow(A, "conta_z", "ana") == (0.0, {})  # sem caminho


def test_propagate_risk_reaches_ring_members():
    accounts, tx = generate_dataset(SimulationConfig(n_people=400, n_merchants=20, n_days=10, n_rings=3))
    graph = build_graph(tx, accounts["account_id"])
    roles = accounts.set_index("account_id")["role"]
    seeds = list(roles[roles == "laranja"].index[::4])  # 1 laranja em cada 4
    risk = propagate_risk(graph, seeds).drop(seeds)
    fraud = accounts.set_index("account_id")["is_fraud"]
    k = int(fraud.sum()) - len(seeds)
    precision = fraud[risk.head(k).index].mean()
    assert precision > 5 * fraud.mean()  # bem melhor que sortear ao acaso
    with pytest.raises(ValueError):
        propagate_risk(graph, ["não existe"])
