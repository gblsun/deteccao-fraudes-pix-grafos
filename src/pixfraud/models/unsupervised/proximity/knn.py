"""kNN (Ramaswamy, Rastogi e Shim, 2000): a conta está longe dos seus vizinhos mais próximos."""

from __future__ import annotations

import pandas as pd
from sklearn.neighbors import NearestNeighbors

from pixfraud.models.base import Detection, detection, prepare_matrix, top_fraction


def knn(
    features: pd.DataFrame,
    n_neighbors: int = 10,
    method: str = "mean",
    contamination: float = 0.05,
) -> Detection:
    """kNN: distância da conta aos seus ``n_neighbors`` vizinhos mais próximos.

    É a ideia mais direta de "conta diferente das outras" (Ramaswamy, Rastogi e
    Shim, 2000; Angiulli e Pizzuti, 2002): uma conta cercada de contas parecidas
    tem vizinhos perto; uma laranja, com um perfil que quase ninguém tem, fica
    longe de todos. ``method="mean"`` usa a média das ``k`` distâncias, mais
    estável; ``"largest"`` usa só a ``k``-ésima (o escore do ``dbscan``). O
    rótulo binário marca a fração ``contamination`` de maior escore.
    """
    if method not in ("mean", "largest"):
        raise ValueError(f"method deve ser 'mean' ou 'largest', não {method!r}")
    X = prepare_matrix(features)
    k = max(1, min(n_neighbors, len(X) - 1))
    distances, _ = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X)
    distances = distances[:, 1:]  # a primeira coluna é a própria conta (distância 0)
    scores = distances.mean(axis=1) if method == "mean" else distances[:, -1]
    return detection(scores, top_fraction(scores, contamination), features.index)
