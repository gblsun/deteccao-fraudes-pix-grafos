"""Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score

from pixfraud.anomaly import DETECTORS
from pixfraud.experiment import (
    COMPARISONS,
    feature_ablation,
    known_fraud_scores,
    load_scenarios,
    run_seeds,
    save_metadata,
    seeded_models,
    supervised_scores,
)
from pixfraud.features import FEATURE_SETS
from pixfraud.simulation import SimulationConfig

ROOT = Path(__file__).parents[1]
TINY = SimulationConfig(n_people=150, n_merchants=8, n_days=4, n_rings=2, victims_per_ring=5)
CONFIG = {
    "atributos": {"betweenness_k": 50},
    "modelos": {"isolation_forest": {"n_estimators": 50}, "dbscan": {"min_samples": 5}},
}


def test_run_seeds_one_dataset_per_seed():
    results = list(run_seeds(TINY, CONFIG, [1, 2]))
    assert [seed for seed, _, _ in results] == [1, 2]
    (_, first, metrics), (_, second, _) = results
    assert set(metrics["semente"]) == {1}
    assert len(metrics) == len(FEATURE_SETS) * len(DETECTORS)
    assert first.labels.sum() > 0 and not first.labels.index.equals(second.labels.index)
    assert CONFIG["modelos"]["isolation_forest"] == {"n_estimators": 50}  # a configuração não é alterada


def test_seeded_models_reach_every_random_detector():
    seeded = seeded_models(CONFIG["modelos"], 7)
    assert {m for m, params in seeded.items() if params.get("seed") == 7} == {
        "isolation_forest", "one_class_svm", "autoencoder", "kmeans", "node2vec_if"}
    assert "seed" not in seeded["dbscan"]  # determinístico: não recebe semente
    assert seeded["isolation_forest"]["n_estimators"] == 50
    assert "seed" not in CONFIG["modelos"]["isolation_forest"]  # a original não muda


def test_run_seeds_in_parallel_gives_the_same_results():
    sequential = [m for _, _, m in run_seeds(TINY, CONFIG, [1, 2], models=["dbscan", "ecod"])]
    parallel = [m for _, _, m in run_seeds(TINY, CONFIG, [1, 2], models=["dbscan", "ecod"], processes=2)]
    for a, b in zip(sequential, parallel):
        pd.testing.assert_frame_equal(a, b)


def test_run_seeds_can_run_only_some_detectors():
    (_, _, metrics), = run_seeds(TINY, CONFIG, [1], models=["ecod", "dbscan"])
    assert set(metrics["modelo"]) == {"ecod", "dbscan"}


def test_comparisons_use_known_feature_sets():
    assert {name for pair in COMPARISONS for name in pair} <= set(FEATURE_SETS)


def test_repository_scenarios_are_valid():
    scenarios = load_scenarios(ROOT / "configs" / "cenarios.yaml")
    assert scenarios["base"] == {}
    assert {"sem_atalhos", "realista"} <= set(scenarios)


def test_load_scenarios_rejects_unknown_parameter(tmp_path):
    path = tmp_path / "cenarios.yaml"
    path.write_text("ruim:\n  n_pessoas: 3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="n_pessoas"):
        load_scenarios(path)


def test_save_metadata(tmp_path):
    path = save_metadata(tmp_path / "sub" / "x_meta.json", CONFIG, sementes=[1, 2])
    meta = json.loads(path.read_text(encoding="utf-8"))
    assert meta["sementes"] == [1, 2] and meta["configuracao"] == CONFIG
    assert meta["commit"] is None or len(meta["commit"]) == 40  # sem git, fica None
    assert set(meta["pacotes"]) >= {"numpy", "pandas", "networkx", "scikit-learn"}


def _planted(n_normal=300, n_fraud=15, seed=0):
    """Contas em que só ``sinal`` separa fraude de normal; ``ruido_*`` não informam nada."""
    rng = np.random.default_rng(seed)
    labels = pd.Series([False] * n_normal + [True] * n_fraud)
    features = pd.DataFrame({
        "sinal": np.r_[rng.lognormal(0, 0.3, n_normal), rng.lognormal(2.5, 0.3, n_fraud)],
        "ruido_1": rng.lognormal(0, 1, n_normal + n_fraud),
        "ruido_2": rng.lognormal(0, 1, n_normal + n_fraud),
    })
    return features, labels


def test_feature_ablation_finds_the_informative_feature():
    features, labels = _planted()
    table = feature_ablation(features, labels, list(features.columns), {"isolation_forest": {"seed": 0}},
                             models=["isolation_forest"])
    assert len(table) == 3 and set(table["atributo"]) == {"sinal", "ruido_1", "ruido_2"}
    assert table.set_index("atributo")["queda"].idxmax() == "sinal"
    assert (table["queda"] == table["ap_com_todos"] - table["ap_sem"]).all()


@pytest.mark.parametrize("model", ["random_forest", "gradient_boosting"])
def test_supervised_scores_are_out_of_fold(model):
    features, labels = _planted()
    scores = supervised_scores(features, labels, seed=0, model=model)
    assert scores.index.equals(features.index) and scores.between(0, 1).all()
    assert average_precision_score(labels, scores) > 0.9  # o sinal é fácil: fraudes no topo


def test_known_fraud_scores_learn_from_a_few_known():
    features, labels = _planted()
    fraud = labels.index[labels]
    known = list(fraud[: max(1, len(fraud) // 4)])
    scores = known_fraud_scores(features, known, seed=0)
    assert scores.index.equals(features.index) and (scores[known] == 1.0).all()
    rest = labels.drop(known)
    assert average_precision_score(rest, scores[rest.index]) > 0.3  # ao acaso, ~4%


def test_supervised_scores_rejects_unknown_model():
    features, labels = _planted()
    with pytest.raises(ValueError, match="desconhecido"):
        supervised_scores(features, labels, model="svm")
