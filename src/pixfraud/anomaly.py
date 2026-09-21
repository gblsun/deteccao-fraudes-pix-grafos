"""Detectores de anomalia não supervisionados aplicados aos atributos das contas."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


@dataclass
class Detection:
    scores: pd.Series  # quanto maior, mais anômala a conta
    is_anomaly: pd.Series  # rótulo binário atribuído pelo modelo


def prepare_matrix(features: pd.DataFrame) -> np.ndarray:
    """Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza cada coluna."""
    return StandardScaler().fit_transform(np.log1p(features.to_numpy(dtype=float)))


def isolation_forest(
    features: pd.DataFrame,
    n_estimators: int = 300,
    contamination: float | str = "auto",
    seed: int = 42,
) -> Detection:
    """Isolation Forest: contas isoladas com poucas partições aleatórias são anômalas."""
    X = prepare_matrix(features)
    model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=seed).fit(X)
    return Detection(
        scores=pd.Series(-model.score_samples(X), index=features.index, name="score"),
        is_anomaly=pd.Series(model.predict(X) == -1, index=features.index, name="is_anomaly"),
    )


def dbscan(
    features: pd.DataFrame,
    eps: float | str = "auto",
    min_samples: int = 10,
    eps_quantile: float = 0.95,
) -> Detection:
    """DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.

    Como o DBSCAN não produz um escore contínuo, usamos como escore a distância
    ao ``min_samples``-ésimo vizinho mais próximo (k-distance): um ponto é
    núcleo de cluster exatamente quando essa distância é <= ``eps``. Com
    ``eps="auto"``, ``eps`` é o quantil ``eps_quantile`` dessas distâncias.
    Isso é só uma heurística; o ideal é escolher ``eps`` pelo gráfico de
    k-distance (ver notebook de análise exploratória).
    """
    X = prepare_matrix(features)
    distances, _ = NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)
    k_distance = distances[:, -1]
    if eps == "auto":
        eps = float(np.quantile(k_distance, eps_quantile))
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X)
    return Detection(
        scores=pd.Series(k_distance, index=features.index, name="score"),
        is_anomaly=pd.Series(labels == -1, index=features.index, name="is_anomaly"),
    )


DETECTORS = {"isolation_forest": isolation_forest, "dbscan": dbscan}
