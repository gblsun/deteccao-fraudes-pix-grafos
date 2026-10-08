"""Testes de `pixfraud.tuning` (busca de hiperparâmetros) e da organização de `pixfraud.models`."""

import json

import pandas as pd
import pytest

from pixfraud import anomaly, flow, gnn, graph_models
from pixfraud.experiment import load_experiment_config, prepare
from pixfraud.features import FEATURE_SETS
from pixfraud.models import DETECTORS, FAMILIES, GRAPH_DETECTORS, SUPERVISED
from pixfraud.models.semi_supervised import label_spreading, propagate_risk
from pixfraud.simulation import SimulationConfig, generate_dataset
from pixfraud.tuning import (
    Param,
    candidates,
    choose,
    chosen_params,
    expand,
    full_params,
    grid,
    load_search_spaces,
    params_key,
    score_candidates,
)

CONFIG = load_experiment_config("configs/experimento.yaml")
SPACES = load_search_spaces()


def test_old_modules_reexport_the_same_models():
    assert anomaly.DETECTORS is DETECTORS and graph_models.GRAPH_DETECTORS is GRAPH_DETECTORS
    assert anomaly.knn is DETECTORS["knn"] and callable(gnn.dominant_scores) and callable(gnn.available)
    assert flow.propagate_risk is propagate_risk and flow.label_spreading is label_spreading
    assert set(FAMILIES) == set(DETECTORS) | set(GRAPH_DETECTORS)  # todo modelo tem família


def test_every_grid_names_real_models_and_parameters():
    for model, space in SPACES.items():
        assert model in {**DETECTORS, **GRAPH_DETECTORS, **SUPERVISED}
        assert set(space) <= set(full_params(model, {}))  # nenhum nome de hiperparâmetro inventado


def test_grid_and_candidates_include_the_current_config_once():
    assert grid({"a": [1, 2], "b": ["x"]}) == [{"a": 1, "b": "x"}, {"a": 2, "b": "x"}]
    found = candidates("knn", CONFIG["modelos"]["knn"], SPACES["knn"])
    assert found[0] == full_params("knn", CONFIG["modelos"]["knn"], SPACES["knn"])  # a configuração atual primeiro
    assert len(found) == len(grid(SPACES["knn"]))  # e não aparece duas vezes


def test_param_goes_beyond_the_edge_with_the_same_step_and_stops_at_the_limit():
    neighbors = Param((10, 20, 50, 100), low=2, high=1000, integer=True)
    assert neighbors.beyond(100) == 200 and neighbors.beyond(10) == 5  # 10 × (10/20)
    assert neighbors.beyond(50) is None  # no meio da lista: nada a ampliar
    fraction = Param((0.8, 0.9, 0.95), low=0.5, high=0.99)
    assert fraction.beyond(0.95) == pytest.approx(0.99)  # cortado no limite
    assert Param((0.9, 0.99), low=0.5, high=0.99).beyond(0.99) is None  # já está no limite
    assert Param(("mean", "largest")).beyond("mean") is None  # lista sem limites é fixa


def test_expand_only_touches_parameters_whose_winner_is_at_an_edge():
    space = {"n_clusters": Param((2, 4, 8, 16), 2, 256, True), "large_fraction": Param((0.8, 0.9, 0.95), 0.5, 0.99)}
    new, changes = expand(space, {"n_clusters": 16, "large_fraction": 0.9})
    assert new["n_clusters"].values == (2, 4, 8, 16, 32) and new["large_fraction"] == space["large_fraction"]
    assert len(changes) == 1
    assert expand(space, {"n_clusters": 8, "large_fraction": 0.9}) == (space, [])


def test_choose_keeps_the_current_config_on_a_tie():
    runs = pd.DataFrame([
        {"modelo": "knn", "parametros": '{"k": 10}', "padrao": True, "average_precision": 0.5},
        {"modelo": "knn", "parametros": '{"k": 5}', "padrao": False, "average_precision": 0.5},
        {"modelo": "pca", "parametros": '{"w": true}', "padrao": True, "average_precision": 0.4},
        {"modelo": "pca", "parametros": '{"w": false}', "padrao": False, "average_precision": 0.6},
    ])
    assert chosen_params(choose(runs)) == {"knn": {"k": 10}, "pca": {"w": False}}


@pytest.mark.lento
def test_score_candidates_on_a_small_network():
    accounts, tx = generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=7, n_rings=2, seed=3))
    prepared = prepare(accounts, tx, CONFIG)
    models = ["pca", "random_forest"]
    todo = {m: candidates(m, CONFIG["modelos"].get(m, {}), SPACES[m]) for m in models}
    current = {m: full_params(m, CONFIG["modelos"].get(m, {}), SPACES[m]) for m in models}
    rows = score_candidates(prepared, FEATURE_SETS["completo"], todo, current, seed=3)
    for model in models:
        mine = [r for r in rows if r["modelo"] == model]
        assert len(mine) == len(todo[model])
        assert [r["padrao"] for r in mine].count(True) == 1
        assert all(0 <= r["average_precision"] <= 1 and json.loads(r["parametros"]) for r in mine)
    assert params_key(todo["pca"][0]) == params_key(current["pca"])
