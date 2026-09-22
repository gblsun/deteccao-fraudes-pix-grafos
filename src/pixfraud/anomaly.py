"""Detectores de anomalia não supervisionados aplicados aos atributos das contas.

Os três partem da mesma matriz (``prepare_matrix``: log1p e padronização) e
devolvem um ``Detection``: um escore contínuo, que ordena as contas, e um
rótulo binário. O que muda é a ideia de "anômalo":

* ``isolation_forest``: a conta é isolada com poucos cortes aleatórios;
* ``dbscan``: a conta está fora das regiões densas (raio único para todos);
* ``local_outlier_factor``: a vizinhança da conta é menos densa que a dos
  seus vizinhos, o que acha anomalias **locais**, em regiões de densidade
  diferente, que um raio único não pega.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from sklearn.preprocessing import StandardScaler


@dataclass
class Detection:
    """Resultado de um detector: um escore contínuo e um rótulo binário por conta.

    Os escores servem para ordenar as contas (AP, precision@k, grafo de calor); a
    escala depende do modelo, então só a ordem é comparável entre detectores.
    """

    scores: pd.Series  # quanto maior, mais anômala a conta
    is_anomaly: pd.Series  # rótulo binário atribuído pelo modelo


def prepare_matrix(features: pd.DataFrame) -> np.ndarray:
    """Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza cada coluna."""
    values = features.to_numpy(dtype=float)
    negativas = features.columns[(values < 0).any(axis=0)]
    if len(negativas):  # log1p de valor negativo vira NaN, e o erro só apareceria lá na frente
        raise ValueError(f"atributos com valores negativos não são aceitos: {list(negativas)}")
    return StandardScaler().fit_transform(np.log1p(values))


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
    return Detection(
        scores=pd.Series(k_distance, index=features.index, name="score"),
        is_anomaly=pd.Series(is_anomaly, index=features.index, name="is_anomaly"),
    )


def local_outlier_factor(features: pd.DataFrame, n_neighbors: int = 20) -> Detection:
    """Local Outlier Factor: compara a densidade da conta com a dos seus vizinhos.

    Enquanto o DBSCAN usa o mesmo raio para toda a base, o LOF olha para cada
    conta em relação à sua vizinhança: uma conta em região esparsa não é
    anômala se os vizinhos também estão espalhados. O escore é o fator de
    outlier (1 = igual aos vizinhos; quanto maior, mais isolada), e o rótulo
    binário é o do próprio LOF.

    Gasta memória proporcional a ``n_neighbors`` por conta, e não ao quadrado
    do número de contas como o rótulo exato do DBSCAN.
    """
    X = prepare_matrix(features)
    model = LocalOutlierFactor(n_neighbors=min(n_neighbors, len(X) - 1))
    labels = model.fit_predict(X)
    return Detection(
        scores=pd.Series(-model.negative_outlier_factor_, index=features.index, name="score"),
        is_anomaly=pd.Series(labels == -1, index=features.index, name="is_anomaly"),
    )


DETECTORS = {
    "isolation_forest": isolation_forest,
    "dbscan": dbscan,
    "local_outlier_factor": local_outlier_factor,
}
