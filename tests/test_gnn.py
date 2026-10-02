"""Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")."""

import networkx as nx
import numpy as np
import pandas as pd
import pytest

from pixfraud import gnn  # noqa: E402

if gnn.torch is None:  # sem o extra "gnn", ou com a DLL do torch bloqueada pelo Windows
    pytest.skip("torch indisponível", allow_module_level=True)

from pixfraud.gnn import dominant_scores, sage_known_fraud_scores, sage_supervised_scores  # noqa: E402


@pytest.fixture
def ring_in_sparse_network():
    """300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.

    Os atributos são ruído puro: só a estrutura separa a quadrilha.
    """
    graph = nx.gnm_random_graph(300, 450, seed=3, directed=True)
    ring = list(range(300, 312))
    graph.add_edges_from((u, v) for u in ring for v in ring if u != v)
    rng = np.random.default_rng(3)
    features = pd.DataFrame(rng.uniform(0, 1, size=(312, 4)), index=range(312), columns=list("abcd"))
    labels = pd.Series(features.index.isin(ring), index=features.index)
    return graph, features, labels


def test_sage_learns_the_ring_from_structure_alone(ring_in_sparse_network):
    graph, features, labels = ring_in_sparse_network
    scores = sage_supervised_scores(graph, features, labels, folds=3, epochs=150)
    assert scores.index.equals(features.index) and scores.between(0, 1).all()
    top = scores.nlargest(int(labels.sum())).index
    assert labels[top].mean() >= 0.75  # sem estrutura, o esperado ao acaso seria ~4%


def test_sage_finds_the_rest_of_the_ring_from_a_few_known(ring_in_sparse_network):
    graph, features, labels = ring_in_sparse_network
    known = [300, 301, 302]  # 3 das 12 contas da quadrilha já contestadas
    scores = sage_known_fraud_scores(graph, features, known, folds=3, epochs=150)
    assert scores.index.equals(features.index) and (scores[known] == 1.0).all()
    rest = labels.drop(known)
    top = scores[rest.index].nlargest(int(rest.sum())).index
    assert rest[top].mean() >= 0.25  # ao acaso, ~3%: com 3 rótulos, o PU é bem mais difícil


def test_dominant_scores_are_aligned_and_flag_the_ring(ring_in_sparse_network):
    graph, features, labels = ring_in_sparse_network
    scores = dominant_scores(graph, features, epochs=150)
    assert scores.index.equals(features.index) and np.isfinite(scores).all()
    assert scores[labels].mean() > scores[~labels].mean()  # a quadrilha é mal reconstruída


def test_dominant_refuses_graphs_that_would_not_fit(ring_in_sparse_network):
    graph, features, _ = ring_in_sparse_network
    with pytest.raises(ValueError, match="max_nodes"):
        dominant_scores(graph, features, max_nodes=100)
