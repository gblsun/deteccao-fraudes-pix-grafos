"""Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num grafo."""

import matplotlib

matplotlib.use("Agg")

import networkx as nx  # noqa: E402
import pytest  # noqa: E402

from pixfraud.graph import graph_from_edges  # noqa: E402
from pixfraud.patterns import PATTERNS, chain, cycle, fraud_nodes, inject, mule_ring  # noqa: E402
from pixfraud.visualization import draw_graph, flow_layout, save_graph  # noqa: E402


@pytest.mark.parametrize("name", sorted(PATTERNS))
def test_patterns_are_well_formed(name):
    graph = PATTERNS[name]()
    assert nx.is_weakly_connected(graph)
    assert all("role" in data for _, data in graph.nodes(data=True))
    assert all(data["amount"] > 0 and data["count"] == 1 for *_, data in graph.edges(data=True))
    assert nx.is_directed_acyclic_graph(graph) == (name != "cycle")


def test_chain_loses_fee_at_each_hop():
    graph = chain(length=3, amount=1000, fee=0.1)
    assert [d["amount"] for *_, d in graph.edges(data=True)] == [1000.0, 900.0]
    assert nx.dag_longest_path_length(graph) == 2


def test_cycle_is_strongly_connected():
    assert nx.is_strongly_connected(cycle(5))


def test_mule_ring_money_reaches_collector():
    graph = mule_ring(n_victims=4, n_mules=2, chain_length=1)
    assert graph.in_degree("coletor") == 1
    assert all(nx.has_path(graph, f"vitima_{i}", "coletor") for i in range(4))


def test_inject_maps_victims_to_existing_accounts():
    background = graph_from_edges([(f"c{i}", f"c{(i + 1) % 20}", 10) for i in range(20)])
    result = inject(background, mule_ring(n_victims=3), prefix="q1", seed=0)
    assert background.number_of_nodes() == 20  # original intacto
    new = set(result) - set(background)
    assert new == {f"q1_{v}" for v in ["laranja_0", "laranja_1", "intermediario_0", "intermediario_1", "coletor"]}
    victims = [v for v, role in result.nodes(data="role") if role == "vitima"]
    assert len(victims) == 3 and set(victims) <= set(background)
    assert set(fraud_nodes(result)) == new
    assert nx.is_weakly_connected(result)
    with pytest.raises(ValueError):
        inject(result, mule_ring(), prefix="q1")


def test_flow_layout_and_exports(tmp_path):
    graph = mule_ring()
    pos = flow_layout(graph)
    assert pos["vitima_0"][0] < pos["laranja_0"][0] < pos["coletor"][0]
    with pytest.raises(ValueError):
        flow_layout(cycle())
    draw_graph(cycle(), layout="circular")
    for ext in ("png", "html", "gexf", "graphml"):
        assert save_graph(graph, tmp_path / f"anel.{ext}").stat().st_size > 0
    assert "vis-network" in (tmp_path / "anel.html").read_text(encoding="utf-8")
