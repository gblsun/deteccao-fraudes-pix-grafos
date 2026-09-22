"""Testes de `pixfraud.anomaly` e `pixfraud.evaluation`: detectores e métricas."""

import numpy as np
import pandas as pd
import pytest

from pixfraud.anomaly import dbscan, isolation_forest, local_outlier_factor, prepare_matrix
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


def test_dbscan_falls_back_to_core_points_on_big_datasets():
    rng = np.random.default_rng(0)
    features = pd.DataFrame({"a": np.r_[rng.lognormal(0, 0.5, 500), [400.0]],
                             "b": np.r_[rng.lognormal(0, 0.5, 500), [400.0]]})
    exato = dbscan(features, min_samples=5)
    aproximado = dbscan(features, min_samples=5, max_exact=100)  # força a aproximação
    assert exato.scores.equals(aproximado.scores)  # o escore (k-distance) é o mesmo
    assert exato.is_anomaly.iloc[-1] and aproximado.is_anomaly.iloc[-1]  # o ponto isolado é anômalo nos dois
    assert (exato.is_anomaly == aproximado.is_anomaly).mean() > 0.9


def test_prepare_matrix_rejects_negative_features():
    with pytest.raises(ValueError, match="negativos"):
        prepare_matrix(pd.DataFrame({"ok": [1.0, 2.0], "ruim": [-1.0, 2.0]}))


def test_local_outlier_factor_flags_the_point_in_the_sparse_region():
    # dois aglomerados com densidades diferentes: o LOF compara cada conta com a vizinhança
    rng = np.random.default_rng(0)
    denso = rng.normal(10, 0.2, (100, 2))
    esparso = rng.normal(30, 2.0, (40, 2))
    fora = np.array([[22.0, 22.0]])  # entre os dois, longe de ambos
    features = pd.DataFrame(np.vstack([denso, esparso, fora]) , columns=["a", "b"])
    detection = local_outlier_factor(features, n_neighbors=15)
    assert detection.scores.idxmax() == len(features) - 1  # o ponto do meio é o mais anômalo
    assert detection.is_anomaly.iloc[-1]
    assert detection.scores.iloc[:100].mean() < detection.scores.iloc[-1]
    assert np.isfinite(detection.scores).all()
