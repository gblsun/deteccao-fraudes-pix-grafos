"""Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e OddBall."""

import networkx as nx
import pandas as pd
import pytest

from pixfraud.communities import (
    STRUCTURAL_EXTRA,
    community_summary,
    core_numbers,
    densest_subgraph,
    detect_communities,
    oddball_scores,
    participation_coefficient,
    structural_features,
)


@pytest.fixture
def two_cliques():
    """Dois cliques de 5 contas ligados por uma única aresta a4 -> b0."""
    graph = nx.DiGraph()
    for prefix in "ab":
        nodes = [f"{prefix}{i}" for i in range(5)]
        graph.add_edges_from((u, v) for u in nodes for v in nodes if u < v)
    graph.add_edge("a4", "b0")
    return graph


@pytest.mark.parametrize("method", ["louvain", "label_propagation"])
def test_communities_split_the_cliques(two_cliques, method):
    communities = detect_communities(two_cliques, method=method)
    assert communities["a0"] == communities["a3"] != communities["b1"] == communities["b4"]
    summary = community_summary(two_cliques, communities, labels=pd.Series({"a0": True}))
    assert summary["contas"].tolist() == [5, 5]
    assert summary["arestas internas"].tolist() == [10, 10]
    assert summary["fraudes"].sum() == 1


def test_participation_and_cores(two_cliques):
    communities = detect_communities(two_cliques)
    participation = participation_coefficient(two_cliques, communities)
    assert participation["a0"] == 0.0
    assert participation["a4"] > 0.0  # a ponte
    assert core_numbers(two_cliques)["a0"] == 4


def test_densest_subgraph_finds_planted_clique():
    graph = nx.gnm_random_graph(200, 300, seed=1, directed=True)
    clique = list(range(200, 210))
    graph.add_edges_from((u, v) for u in clique for v in clique if u != v)
    nodes, density = densest_subgraph(graph)
    assert set(clique) <= nodes and len(nodes) <= 15
    assert density >= 4.5  # 45 arestas / 10 contas
    fraudar_nodes, _ = densest_subgraph(graph, fraudar=True)
    assert set(clique) <= fraudar_nodes


def test_oddball_flags_star():
    graph = nx.Graph()
    for size in (4, 5, 6, 7):  # cliques de vários tamanhos definem a lei de potência E ~ N^α
        for copy in range(3):
            nodes = [f"k{size}_{copy}_{i}" for i in range(size)]
            graph.add_edges_from((u, v, {"amount": 10.0}) for u in nodes for v in nodes if u < v)
    graph.add_edges_from(("centro", f"folha{i}", {"amount": 10.0}) for i in range(8))
    scores = oddball_scores(graph)
    assert scores["oddball_en"].idxmax() == "centro"


def test_structural_features_columns(two_cliques):
    features = structural_features(two_cliques)
    assert list(features.columns) == STRUCTURAL_EXTRA
    assert len(features) == two_cliques.number_of_nodes()
