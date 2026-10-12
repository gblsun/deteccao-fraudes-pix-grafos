"""Testes da GraphSAGE direcionada de `pixfraud.gnn` (`graphsage_scores`). Pulados sem o `torch_geometric`."""

import numpy as np
import pytest
from sklearn.metrics import average_precision_score

from pixfraud import gnn
from pixfraud.experiment import prepare
from pixfraud.simulation import SimulationConfig, generate_dataset

if not gnn.available():  # sem o extra "gnn", ou com a DLL do torch bloqueada pelo Windows
    pytest.skip("PyTorch Geometric indisponível", allow_module_level=True)

CONFIG = {"atributos": {"betweenness_k": 50}}


@pytest.fixture(scope="module")
def prepared():
    accounts, transactions = generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=6, n_rings=4,
                                                               victims_per_ring=8))
    return prepare(accounts, transactions, CONFIG)


def test_graphsage_is_available():
    assert gnn.available()


def test_graphsage_beats_chance_and_covers_every_account(prepared):
    features = prepared.features[["in_degree", "out_degree", "n_received", "amount_received"]]
    scores = gnn.graphsage_scores(prepared.graph, features, prepared.labels, epochs=60, hidden=16)
    assert scores.index.equals(features.index)
    assert scores.between(0, 1).all()
    y = prepared.labels.reindex(scores.index)
    assert average_precision_score(y, scores) > 3 * y.mean()  # bem acima do acaso


def test_graphsage_is_reproducible_with_the_seed(prepared):
    features = prepared.features[["in_degree", "out_degree"]]
    first = gnn.graphsage_scores(prepared.graph, features, prepared.labels, epochs=10, hidden=8, seed=1)
    second = gnn.graphsage_scores(prepared.graph, features, prepared.labels, epochs=10, hidden=8, seed=1)
    assert np.allclose(first, second)
