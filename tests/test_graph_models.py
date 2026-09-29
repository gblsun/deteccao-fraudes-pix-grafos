"""Testes de `pixfraud.graph_models` e de `communities.peeling_scores`: detectores que só olham o grafo."""

import networkx as nx
import numpy as np
import pytest

from pixfraud.communities import densest_subgraph, peeling_scores
from pixfraud.graph import build_graph
from pixfraud.graph_models import GRAPH_DETECTORS, fraudar, node2vec_embedding, node2vec_isolation_forest
from pixfraud.simulation import SimulationConfig, generate_dataset


@pytest.fixture
def sparse_graph_with_block():
    """Grafo esparso aleatório com um bloco denso plantado: 6 contas que pagam todas a todas."""
    graph = nx.gnm_random_graph(200, 300, seed=1, directed=True)
    block = list(range(200, 206))
    graph.add_edges_from((u, v) for u in block for v in block if u != v)
    graph.add_edges_from([(block[0], 5), (7, block[3])])  # o bloco também toca o resto
    return graph, set(block)


def test_peeling_scores_put_the_dense_block_on_top(sparse_graph_with_block):
    graph, block = sparse_graph_with_block
    scores = peeling_scores(graph)
    assert set(scores.nlargest(len(block)).index) == block
    assert scores.index.tolist() == list(graph.nodes)


def test_peeling_scores_give_each_block_its_own_level():
    # dois blocos de densidades diferentes: o mais denso na frente, e o outro logo atrás
    graph = nx.gnm_random_graph(150, 180, seed=2, directed=True)
    big, small = list(range(150, 158)), list(range(160, 164))
    graph.add_edges_from((u, v) for group in (big, small) for u in group for v in group if u != v)
    order = peeling_scores(graph).sort_values(ascending=False).index.tolist()
    assert set(order[:8]) == set(big) and set(order[8:12]) == set(small)


def test_densest_subgraph_still_finds_the_block(sparse_graph_with_block):
    graph, block = sparse_graph_with_block
    found, density = densest_subgraph(graph, fraudar=True)
    assert block <= found and density > 0


def test_fraudar_detector_marks_the_block(sparse_graph_with_block):
    graph, block = sparse_graph_with_block
    detection = fraudar(graph, contamination=0.03)
    assert set(detection.scores.nlargest(len(block)).index) == block
    assert detection.is_anomaly[list(block)].all()


def test_node2vec_embedding_is_reproducible(sparse_graph_with_block):
    graph, _ = sparse_graph_with_block
    first = node2vec_embedding(graph, dimensions=8, walks_per_node=4, walk_length=10, seed=3)
    assert first.shape == (graph.number_of_nodes(), 8)
    assert first.equals(node2vec_embedding(graph, dimensions=8, walks_per_node=4, walk_length=10, seed=3))
    assert not first.equals(node2vec_embedding(graph, dimensions=8, walks_per_node=4, walk_length=10, seed=4))


def test_node2vec_embedding_handles_isolated_accounts():
    graph = nx.DiGraph([(0, 1), (1, 2)])
    graph.add_nodes_from([3, 4])  # contas sem nenhum Pix
    embedding = node2vec_embedding(graph, dimensions=2, walks_per_node=2, walk_length=5)
    assert np.isfinite(embedding.to_numpy()).all() and len(embedding) == 5


@pytest.mark.parametrize("name", sorted(GRAPH_DETECTORS))
def test_graph_detectors_run_on_a_generated_dataset(name):
    accounts, transactions = generate_dataset(SimulationConfig(n_people=150, n_merchants=8, n_days=4, n_rings=2,
                                                               victims_per_ring=5))
    graph = build_graph(transactions, accounts["account_id"])
    params = {"walks_per_node": 3, "walk_length": 8} if name == "node2vec_if" else {}
    detection = GRAPH_DETECTORS[name](graph, **params)
    assert set(detection.scores.index) == set(accounts["account_id"])
    assert np.isfinite(detection.scores).all()
    assert 0 < detection.is_anomaly.sum() < len(accounts)


def test_node2vec_isolation_forest_returns_one_score_per_account(sparse_graph_with_block):
    graph, _ = sparse_graph_with_block
    detection = node2vec_isolation_forest(graph, dimensions=8, walks_per_node=3, walk_length=8, n_estimators=50)
    assert detection.scores.index.tolist() == list(graph.nodes)
