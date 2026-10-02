"""Testes de `pixfraud.anomaly` e `pixfraud.evaluation`: detectores e métricas."""

import numpy as np
import pandas as pd
import pytest

from pixfraud.anomaly import (
    DETECTORS,
    autoencoder,
    dbscan,
    ecod,
    isolation_forest,
    kmeans,
    knn,
    local_outlier_factor,
    one_class_svm,
    pca,
    prepare_matrix,
)
from pixfraud.evaluation import evaluate


@pytest.fixture
def blob_with_outlier():
    rng = np.random.default_rng(0)
    features = pd.DataFrame(
        rng.lognormal(0, 0.3, size=(300, 3)), columns=["a", "b", "c"], index=[f"n{i}" for i in range(300)]
    )
    features.loc["outlier"] = [50.0, 50.0, 50.0]
    return features


@pytest.mark.parametrize("detector", [isolation_forest, dbscan, ecod, one_class_svm, autoencoder, knn, kmeans])
def test_detector_flags_outlier(detector, blob_with_outlier):
    detection = detector(blob_with_outlier)
    assert detection.scores.idxmax() == "outlier"
    assert detection.is_anomaly["outlier"]


@pytest.mark.parametrize("name", sorted(DETECTORS))
def test_every_detector_returns_aligned_finite_scores(name, blob_with_outlier):
    detection = DETECTORS[name](blob_with_outlier)
    assert detection.scores.index.equals(blob_with_outlier.index)
    assert detection.is_anomaly.index.equals(blob_with_outlier.index)
    assert np.isfinite(detection.scores).all()
    assert 0 < detection.is_anomaly.sum() < len(blob_with_outlier)


@pytest.mark.parametrize("name", sorted(DETECTORS))
def test_every_detector_survives_few_and_repeated_columns(name):
    # como o conjunto "temporal": 2 atributos, a maioria das contas com valores iguais
    features = pd.DataFrame({"a": [0.0] * 150 + [3.0, 9.0, 40.0], "b": [1.0] * 150 + [2.0, 7.0, 30.0]})
    detection = DETECTORS[name](features)
    assert np.isfinite(detection.scores).all()
    assert detection.scores.iloc[-1] >= detection.scores.iloc[:150].max()


def test_ecod_uses_both_tails():
    # o ECOD soma a raridade de cada atributo: extremos nos dois atributos, para
    # baixo ou para cima, ficam no topo
    rng = np.random.default_rng(1)
    features = pd.DataFrame(rng.lognormal(0, 0.4, (400, 2)), columns=["a", "b"])
    features.loc[400] = [0.0, 0.0]  # cauda esquerda dos dois
    features.loc[401] = [60.0, 60.0]  # cauda direita dos dois
    top = ecod(features).scores.nlargest(2).index
    assert set(top) == {400, 401}


def test_one_class_svm_approximation_on_big_datasets():
    rng = np.random.default_rng(0)
    features = pd.DataFrame(rng.lognormal(0, 0.4, (600, 3)), columns=list("abc"))
    features.loc[600] = [80.0, 80.0, 80.0]
    exact = one_class_svm(features)
    approximate = one_class_svm(features, max_exact=100, n_components=100)  # força Nyström + SGD
    assert exact.scores.idxmax() == approximate.scores.idxmax() == 600
    assert approximate.is_anomaly[600]


def test_autoencoder_is_reproducible_with_the_seed(blob_with_outlier):
    first = autoencoder(blob_with_outlier, seed=3).scores
    assert first.equals(autoencoder(blob_with_outlier, seed=3).scores)
    assert not first.equals(autoencoder(blob_with_outlier, seed=4).scores)


def test_knn_averages_all_neighbors_unlike_dbscan():
    # um par de contas iguais e isoladas: para o DBSCAN com k = 2, a vizinha coincidente
    # não ajuda (a 2ª vizinha está longe); para a média do KNN, metade da distância some
    rng = np.random.default_rng(2)
    features = pd.DataFrame(rng.lognormal(0, 0.3, (200, 2)), columns=["a", "b"])
    features.loc[200] = features.loc[201] = [30.0, 30.0]
    scores = knn(features, n_neighbors=2).scores
    assert scores[200] == pytest.approx(scores[201])
    assert scores[200] < 2 * dbscan(features, min_samples=3).scores[200]


def test_kmeans_ignores_tiny_clusters_of_anomalies():
    # 6 contas anômalas iguais formariam um grupo próprio, e ficariam a distância 0 do centro dele
    rng = np.random.default_rng(3)
    features = pd.DataFrame(rng.lognormal(0, 0.3, (300, 2)), columns=["a", "b"])
    for i in range(300, 306):
        features.loc[i] = [40.0, 0.01]
    scores = kmeans(features, n_clusters=4, min_cluster_fraction=0.05).scores
    assert scores.iloc[300:].min() > scores.iloc[:300].max()
    assert kmeans(features, seed=1).scores.equals(kmeans(features, seed=1).scores)


def test_pca_flags_accounts_that_break_the_correlation():
    # a e b andam juntos; a conta com a alto e b baixo foge da direção principal
    rng = np.random.default_rng(4)
    base = rng.lognormal(0, 0.5, 400)
    features = pd.DataFrame({"a": base, "b": base * rng.lognormal(0, 0.05, 400), "c": rng.lognormal(0, 0.05, 400)})
    features.loc[400] = [features["a"].max(), features["b"].min(), 1.0]
    detection = pca(features, variance=0.6)
    assert detection.scores.idxmax() == 400
    assert detection.is_anomaly[400]


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
