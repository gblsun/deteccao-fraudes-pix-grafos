"""DBSCAN (Ester et al., 1996): a conta fora das regiões densas é anômala."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from pixfraud.models.base import Detection, detection, prepare_matrix


def dbscan(
    features: pd.DataFrame,
    eps: float | str = "auto",
    min_samples: int = 10,
    eps_quantile: float = 0.95,
    max_exact: int = 20_000,
) -> Detection:
    """DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.

    Como o DBSCAN não produz um escore contínuo, usamos como escore a distância
    ao ``min_samples``-ésimo vizinho mais próximo (k-distance): um ponto é
    núcleo de cluster exatamente quando essa distância é <= ``eps``. Com
    ``eps="auto"``, ``eps`` é o quantil ``eps_quantile`` dessas distâncias.
    Isso é só uma heurística; o ideal é escolher ``eps`` pelo gráfico de
    k-distance (ver notebook de análise exploratória).

    ``max_exact``: acima desse número de contas, o rótulo binário deixa de sair
    do DBSCAN e passa a ser "não é ponto de núcleo" (k-distance > ``eps``). O
    motivo é memória: o DBSCAN guarda a vizinhança de **cada** ponto e, com
    ``eps`` no quantil 0,95, cada conta tem ~20% das contas como vizinhas, o
    que cresce com o quadrado do número de contas (7 MB com 2 mil contas,
    ~16 GB com 100 mil). Os escores não mudam, então average precision e
    precision@k são idênticas; muda só o rótulo binário, que passa a incluir os
    pontos de borda (97,6% de concordância no dataset sintético).
    """
    X = prepare_matrix(features)
    distances, _ = NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)
    k_distance = distances[:, -1]
    if eps == "auto":
        # Com muitas contas idênticas (ex.: poucos atributos numa janela curta), o
        # quantil pode ser 0, que o DBSCAN recusa. Um eps mínimo mantém as contas
        # idênticas como vizinhas, e qualquer conta diferente delas vira ruído.
        eps = max(float(np.quantile(k_distance, eps_quantile)), 1e-9)
    if len(X) <= max_exact:
        is_anomaly = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X) == -1
    else:
        is_anomaly = k_distance > eps  # aproximação barata: não é ponto de núcleo
    return detection(k_distance, is_anomaly, features.index)
