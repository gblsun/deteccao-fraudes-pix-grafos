"""Testes de `pixfraud.graph`: criação de grafos, trilha do dinheiro e resumo."""

from pathlib import Path

import networkx as nx
import pytest

from pixfraud.graph import adjacency_matrix, describe, graph_from_csv, graph_from_edges, money_trail

EXAMPLE = Path(__file__).parents[1] / "estudos" / "dados" / "exemplo_transacoes.csv"


def test_graph_from_edges_aggregates_or_keeps_parallel_edges():
    edges = [("a", "b", 50), ("b", "c"), ("a", "b", 30)]
    simple = graph_from_edges(edges)
    assert simple["a"]["b"] == {"amount": 80.0, "count": 2}
    assert simple["b"]["c"]["amount"] == 1.0
    multi = graph_from_edges(edges, multigraph=True)
    assert multi.number_of_edges("a", "b") == 2
    assert not graph_from_edges(edges, directed=False).is_directed()


def test_graph_from_csv_example():
    aggregated = graph_from_csv(EXAMPLE)
    multi = graph_from_csv(EXAMPLE, aggregate=False)
    assert aggregated.number_of_nodes() == multi.number_of_nodes() == 11
    assert multi.number_of_edges() == 20
    assert aggregated["carla"]["conta_x"] == {"amount": 2700.0, "count": 2}
    assert "timestamp" in next(iter(multi.edges(data=True)))[2]


def test_adjacency_matrix_sums_are_degrees():
    graph = graph_from_csv(EXAMPLE)
    unweighted = adjacency_matrix(graph)
    weighted = adjacency_matrix(graph, weight="amount")
    assert unweighted.sum(axis=1).to_dict() == dict(graph.out_degree())
    assert unweighted.sum(axis=0).to_dict() == dict(graph.in_degree())
    assert weighted.loc["conta_x"].sum() == pytest.approx(graph.out_degree("conta_x", weight="amount"))


def test_money_trail_directions():
    graph = graph_from_csv(EXAMPLE)
    forward = money_trail(graph, "fabio", max_hops=3, direction="forward")
    assert {"conta_x", "conta_y", "conta_z", "mercado"} <= set(forward)
    backward = money_trail(graph, "conta_z", max_hops=2, direction="backward")
    assert set(backward) == {"conta_z", "conta_y", "conta_x"}
    with pytest.raises(ValueError):
        money_trail(graph, "ana", direction="sideways")


def test_describe():
    info = describe(nx.DiGraph([("a", "b"), ("b", "a"), ("b", "c")]))
    assert info["vértices"] == 3
    assert info["arestas"] == 3
    assert info["componentes fortemente conexas"] == 2
    assert info["reciprocidade"] == pytest.approx(2 / 3)
    assert not info["acíclico (DAG)"]
