"""Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários."""

from pathlib import Path

import pytest

from pixfraud.anomaly import DETECTORS
from pixfraud.experiment import COMPARISONS, load_scenarios, run_seeds
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
