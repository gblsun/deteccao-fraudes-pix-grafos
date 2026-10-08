"""k-means com a regra do CBLOF (He, Xu e Deng, 2003): a conta está longe dos grupos grandes."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from pixfraud.models.base import Detection, detection, prepare_matrix, top_fraction


def kmeans(
    features: pd.DataFrame,
    n_clusters: int = 8,
    large_fraction: float = 0.9,
    contamination: float = 0.05,
    seed: int = 42,
) -> Detection:
    """k-means: distância da conta ao centro do grupo grande mais próximo.

    O k-means divide as contas em ``n_clusters`` grupos de perfis parecidos
    (pessoas que usam pouco o Pix, comércios, quem paga muito...). Uma conta
    longe de todos os centros é anômala. Só que um grupo pequeno de contas
    estranhas pode ganhar um centro só para ele, e aí ficaria com distância
    zero; por isso, como no CBLOF (He, Xu e Deng, 2003), os grupos são
    separados em grandes (os maiores, que juntos somam ``large_fraction`` das
    contas) e pequenos, e o escore é a distância ao centro **grande** mais
    próximo. O rótulo binário marca a fração ``contamination`` de maior escore.
    """
    X = prepare_matrix(features)
    distinct = len(np.unique(X, axis=0))
    model = KMeans(n_clusters=max(1, min(n_clusters, distinct)), n_init=10, random_state=seed).fit(X)
    sizes = np.bincount(model.labels_, minlength=model.n_clusters)
    order = np.argsort(-sizes)
    covered = np.cumsum(sizes[order]) / len(X)
    large = order[: int(np.searchsorted(covered, large_fraction)) + 1]
    distances = np.linalg.norm(X[:, None, :] - model.cluster_centers_[large][None, :, :], axis=2)
    scores = distances.min(axis=1)
    return detection(scores, top_fraction(scores, contamination), features.index)
