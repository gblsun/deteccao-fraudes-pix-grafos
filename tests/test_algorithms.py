from pathlib import Path

import networkx as nx
import pytest

from pixfraud.algorithms import (
    bipartite_projection,
    find_pattern,
    hubs_authorities,
    laundering_depth,
    longest_chain,
    money_backbone,
    similar_accounts,
    widest_path,
)
from pixfraud.graph import graph_from_csv, graph_from_edges
from pixfraud.patterns import cycle, fan_in, inject, mule_ring, scatter_gather

EXEMPLO = Path(__file__).parents[1] / "estudos" / "dados" / "exemplo_transacoes.csv"


def test_widest_path():
    graph = graph_from_edges([("s", "a", 10), ("a", "t", 3), ("s", "b", 5), ("b", "t", 5)])
    assert widest_path(graph, "s", "t") == (["s", "b", "t"], 5.0)
    assert widest_path(graph, "t", "s") == ([], 0.0)


def test_money_backbone_keeps_main_source():
    graph = graph_from_csv(EXEMPLO)
    backbone = money_backbone(graph)
    assert nx.is_branching(backbone)
    assert set(backbone) == set(graph)
    assert list(backbone.predecessors("conta_x")) == ["carla"]  # R$ 2.700 contra R$ 900 de fabio


def test_laundering_depth_and_longest_chain():
    graph = graph_from_edges([("a", "b"), ("b", "c"), ("x", "y"), ("y", "x"), ("y", "a")])
    depth = laundering_depth(graph)
    assert depth[["c", "b", "a"]].tolist() == [0, 1, 2]
    assert depth["x"] == depth["y"] == 3  # o ciclo x <-> y vira uma componente só
    assert longest_chain(graph_from_edges([("a", "b"), ("b", "c"), ("a", "c")])) == ["a", "b", "c"]
    with pytest.raises(ValueError):
        longest_chain(cycle())


def test_find_pattern_locates_injected_scatter_gather():
    background = graph_from_edges([(f"c{i}", f"c{(i + 1) % 30}") for i in range(30)])
    graph = inject(background, scatter_gather(n_middle=3), prefix="sg", camouflage=0, seed=0)
    matches = find_pattern(graph, scatter_gather(n_middle=3), max_results=50)
    assert any(m["laranja"] == "sg_laranja" and m["coletor"] == "sg_coletor" for m in matches)
    assert find_pattern(graph, cycle(3)) == []


def test_hits_similarity_and_projection():
    ring = mule_ring(n_victims=6, n_mules=2, chain_length=1)
    assert hubs_authorities(fan_in())["authority"].idxmax() == "laranja"
    similar = similar_accounts(ring, "laranja_0", method="jaccard_out")
    assert similar.index[0] == "laranja_1" and similar.iloc[0] == 1.0
    assert "laranja_1" in similar_accounts(ring, "laranja_0", method="simrank").index
    victims = [v for v, r in ring.nodes(data="role") if r == "vitima"]
    mules = [v for v, r in ring.nodes(data="role") if r == "laranja"]
    projection = bipartite_projection(ring, victims, mules)
    assert nx.number_connected_components(projection) == 2  # uma por laranja
    assert projection["vitima_0"]["vitima_2"]["weight"] == 1
