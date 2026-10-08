"""Local Outlier Factor (Breunig et al., 2000): a vizinhança da conta é menos densa que a dos vizinhos."""

from __future__ import annotations

import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

from pixfraud.models.base import Detection, detection, prepare_matrix


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
    return detection(-model.negative_outlier_factor_, labels == -1, features.index)
