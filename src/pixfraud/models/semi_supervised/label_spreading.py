"""Label spreading (Zhou et al., 2004): fraudes **e** contas legítimas conhecidas espalham o rótulo pelo grafo."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import numpy as np
import pandas as pd
import scipy.sparse as sp


def label_spreading(
    graph: nx.DiGraph,
    positives: Iterable,
    negatives: Iterable = (),
    alpha: float = 0.85,
    weight: str | None = None,
    max_iter: int = 200,
    tol: float = 1e-6,
) -> pd.Series:
    """Propagação de rótulos com exemplos positivos **e negativos** (Zhou et al., 2004).

    Cada conta começa com +1 (fraude conhecida), -1 (legítima conhecida) ou 0
    (desconhecida), e a cada passo recebe a média dos vizinhos, normalizada
    pelos graus (``S = D^{-1/2} W D^{-1/2}``), sem esquecer o valor inicial:
    ``F <- alpha * S F + (1 - alpha) * Y``. No fim, o escore diz de qual dos
    dois lados a conta está mais perto no grafo.

    A diferença para ``propagate_risk`` é usar também o que se sabe de bom: uma
    conta ao lado de muitas legítimas conhecidas é puxada para baixo. O grafo é
    tratado como não direcionado, e com ``weight=None`` cada par de contas pesa
    1, para os comércios, com muitos Pix, não dominarem.
    """
    nodes = list(graph.nodes)
    position = {v: i for i, v in enumerate(nodes)}
    positives = [position[v] for v in positives if v in position]
    if not positives:
        raise ValueError("nenhuma conta positiva está no grafo")
    adjacency = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight=weight, format="csr")
    symmetric = (adjacency + adjacency.T).tocsr()
    degree = np.asarray(symmetric.sum(axis=1)).ravel()
    inv_sqrt = np.divide(1.0, np.sqrt(degree), out=np.zeros_like(degree, dtype=float), where=degree > 0)
    normalized = sp.diags(inv_sqrt) @ symmetric @ sp.diags(inv_sqrt)

    seeds = np.zeros(len(nodes))
    seeds[[position[v] for v in negatives if v in position]] = -1.0
    seeds[positives] = 1.0
    scores = seeds.copy()
    for _ in range(max_iter):
        updated = alpha * (normalized @ scores) + (1 - alpha) * seeds
        converged = np.abs(updated - scores).max() < tol
        scores = updated
        if converged:
            break
    return pd.Series(scores, index=nodes, name="risk").sort_values(ascending=False)
