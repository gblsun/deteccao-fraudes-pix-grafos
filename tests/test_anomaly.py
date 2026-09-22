"""Testes de `pixfraud.anomaly` e `pixfraud.evaluation`: detectores e métricas."""

import numpy as np
import pandas as pd
import pytest

from pixfraud.anomaly import dbscan, isolation_forest
from pixfraud.evaluation import evaluate


@pytest.fixture
def blob_with_outlier():
    rng = np.random.default_rng(0)
    features = pd.DataFrame(
        rng.lognormal(0, 0.3, size=(300, 3)), columns=["a", "b", "c"], index=[f"n{i}" for i in range(300)]
    )
    features.loc["outlier"] = [50.0, 50.0, 50.0]
    return features


@pytest.mark.parametrize("detector", [isolation_forest, dbscan])
def test_detector_flags_outlier(detector, blob_with_outlier):
    detection = detector(blob_with_outlier)
    assert detection.scores.idxmax() == "outlier"
    assert detection.is_anomaly["outlier"]


def test_evaluate_perfect_ranking(blob_with_outlier):
    detection = isolation_forest(blob_with_outlier)
    y = pd.Series(blob_with_outlier.index == "outlier", index=blob_with_outlier.index)
    metrics = evaluate(y, detection)
    assert metrics["roc_auc"] == 1.0
    assert metrics["precision_at_k"] == 1.0
    assert metrics["recall"] == 1.0


def test_dbscan_handles_mostly_identical_accounts():
    # 97% das contas idênticas: o eps automático seria 0, que o DBSCAN recusa
    features = pd.DataFrame({"a": [1.0] * 97 + [5.0, 8.0, 50.0], "b": [2.0] * 97 + [1.0, 9.0, 40.0]})
    detection = dbscan(features, min_samples=5)
    assert not detection.is_anomaly.iloc[:97].any()
    assert detection.is_anomaly.iloc[97:].all()
