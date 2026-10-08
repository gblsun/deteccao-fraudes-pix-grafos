"""Testes de `pixfraud.explorer`: layout por comunidades e página da rede inteira."""

import json
import re

import numpy as np
import pytest

from pixfraud.communities import detect_communities
from pixfraud.explorer import community_layout, explorer_payload, save_network_explorer
from pixfraud.graph import build_graph
from pixfraud.simulation import SimulationConfig, generate_dataset


@pytest.fixture(scope="module")
def data():
    accounts, tx = generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=7, n_rings=2))
    return accounts, tx, build_graph(tx, accounts["account_id"])


def test_community_layout_keeps_groups_apart(data):
    _, _, graph = data
    communities = detect_communities(graph)
    positions = community_layout(graph, communities)
    assert set(positions) == set(graph)
    centers = {c: np.mean([positions[v] for v in communities.index[communities == c]], axis=0)
               for c in communities.unique()}
    inside = np.mean([np.linalg.norm(positions[v] - centers[communities[v]]) for v in graph])
    between = np.mean([np.linalg.norm(a - b) for a in centers.values() for b in centers.values() if a is not b])
    assert between > 2 * inside  # grupos ficam separados no desenho


def test_ring_accounts_are_drawn_in_the_center(data):
    accounts, _, graph = data
    roles = accounts.set_index("account_id")["role"]
    payload = explorer_payload(graph, roles=roles)
    distance = {n["id"]: np.hypot(n["x"], n["y"]) for n in payload["nodes"]}
    ring = [d for v, d in distance.items() if roles[v] in ("laranja", "intermediario", "coletor")]
    others = [d for v, d in distance.items() if roles[v] not in ("laranja", "intermediario", "coletor")]
    assert max(ring) < np.median(others)  # a quadrilha inteira fica mais perto do centro que a maioria
    off = explorer_payload(graph, roles=roles, center_roles=())
    assert off["nodes"] != payload["nodes"]  # center_roles=() volta ao layout só por comunidades


def test_payload_and_page(data, tmp_path):
    accounts, tx, graph = data
    roles = accounts.set_index("account_id")["role"]
    risk = roles.map({"normal": 0.1, "comercio": 0.2}).fillna(0.9)
    payload = explorer_payload(graph, transactions=tx, roles=roles, risk=risk)
    assert len(payload["nodes"]) == graph.number_of_nodes()
    assert len(payload["edges"]["s"]) == graph.number_of_edges()
    assert len(payload["days"]) == 7 and max(payload["edges"]["d"]) <= 6
    assert payload["hasRisk"] and payload["hasFraudEdges"]
    assert sum(payload["edges"]["f"]) == len(tx.loc[tx["is_fraud"], ["sender", "receiver"]].drop_duplicates())

    path = save_network_explorer(tmp_path / "rede.html", graph, transactions=tx, roles=roles, title="Rede <teste>")
    page = path.read_text(encoding="utf-8")
    assert 'id="normal-alpha"' in page and 'id="edge-scale"' in page  # controles de opacidade e espessura
    assert 'data-mode="hits"' in page and 'id="top-k"' in page  # modo "Acertos" e o top-k
    assert "<title>Rede &lt;teste&gt;</title>" in page
    embedded = re.search(r"const DATA = (\{.*?\});\n", page, re.S).group(1)
    assert json.loads(embedded)["communities"] >= 2
    assert "sigma.min.js" in page and "graphology.umd.min.js" in page


def test_several_risk_models_go_to_the_model_picker(data):
    accounts, tx, graph = data
    roles = accounts.set_index("account_id")["role"]
    up = roles.map({"normal": 0.1, "comercio": 0.2}).fillna(0.9)
    risk = {"kNN": up, "Random Forest": -up}
    groups = {"kNN": "Não supervisionados", "Random Forest": "Supervisionados"}
    payload = explorer_payload(graph, transactions=tx, roles=roles, risk=risk, risk_groups=groups)
    assert payload["models"] == [{"name": "kNN", "group": "Não supervisionados"},
                                 {"name": "Random Forest", "group": "Supervisionados"}]
    coletor = next(n for n in payload["nodes"] if n["r"] == "coletor")
    normal = next(n for n in payload["nodes"] if n["r"] == "normal")
    assert coletor["k"][0] > normal["k"][0] and coletor["k"][1] < normal["k"][1]  # um percentil por modelo

    labels = accounts.set_index("account_id")["is_fraud"]
    with_truth = explorer_payload(graph, roles=roles, risk=risk, labels=labels)
    assert with_truth["hasLabels"] and sum(n["g"] for n in with_truth["nodes"]) == int(labels.sum())
    assert not payload["hasLabels"] and payload["nodes"][0]["g"] is None  # sem gabarito, sem modo "Acertos"

    single = explorer_payload(graph, roles=roles, risk=up)  # um escore só continua funcionando
    assert single["hasRisk"] and len(single["models"]) == 1 and len(single["nodes"][0]["k"]) == 1
    assert not explorer_payload(graph, roles=roles)["hasRisk"]
