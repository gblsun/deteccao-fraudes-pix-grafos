"""Detectores que olham só para a estrutura do grafo, sem a tabela de atributos.

Os detectores de ``pixfraud.anomaly`` recebem os atributos já calculados
(grau, PageRank, OddBall...). Estes recebem o **grafo** e tiram dele o que
precisam, e por isso ficam num registro separado, ``GRAPH_DETECTORS``, com a
mesma saída (``Detection``):

* ``fraudar``: o núcleo ponderado da remoção gulosa com os pesos do FRAUDAR
  (Hooi et al., 2016). Contas em blocos densos, como uma quadrilha em que
  várias laranjas mandam para os mesmos intermediários, ficam no topo; os
  pesos fazem Pix para comércios muito procurados valerem pouco, e assim
  "pagar a padaria" não camufla a quadrilha;
* ``node2vec_if``: cada conta vira um vetor aprendido da sua vizinhança
  (passeios aleatórios, como no DeepWalk/node2vec com p = q = 1), e o
  Isolation Forest procura as contas em posições raras desse espaço.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from pixfraud.anomaly import Detection, _detection, _top_fraction
from pixfraud.communities import peeling_scores


def fraudar(graph: nx.Graph, contamination: float = 0.05) -> Detection:
    """FRAUDAR como escore por conta (``communities.peeling_scores``).

    O rótulo binário marca a fração ``contamination`` de maior escore. Não usa
    valores nem horários, só quem pagou quem.
    """
    scores = peeling_scores(graph, fraudar=True)
    return _detection(scores.to_numpy(), _top_fraction(scores.to_numpy(), contamination), scores.index)


def node2vec_embedding(
    graph: nx.Graph,
    dimensions: int = 32,
    walks_per_node: int = 10,
    walk_length: int = 20,
    window: int = 5,
    seed: int = 42,
) -> pd.DataFrame:
    """Um vetor por conta, aprendido dos passeios aleatórios que passam por ela.

    Faz ``walks_per_node`` passeios uniformes de ``walk_length`` passos a partir
    de cada conta (no grafo não direcionado), conta quantas vezes duas contas
    aparecem a até ``window`` passos uma da outra, transforma as contagens em
    PPMI (informação mútua pontual positiva) e reduz a ``dimensions`` colunas
    com SVD truncado. É a formulação do skip-gram (word2vec) como fatoração de
    matriz (Levy e Goldberg, 2014), o mesmo objetivo do DeepWalk e do node2vec
    com p = q = 1, sem precisar de uma biblioteca de redes neurais.
    """
    nodes = list(graph.nodes)
    n = len(nodes)
    position = {v: i for i, v in enumerate(nodes)}
    undirected = graph.to_undirected(as_view=True) if graph.is_directed() else graph
    rows, cols = [], []
    for u, v in undirected.edges():
        if u != v:
            rows += [position[u], position[v]]
            cols += [position[v], position[u]]
    adjacency = sp.csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=(n, n))
    adjacency.data[:] = 1.0  # pares repetidos contam uma vez
    indptr, indices = adjacency.indptr, adjacency.indices
    degree = np.diff(indptr)

    rng = np.random.default_rng(seed)
    current = np.repeat(np.arange(n, dtype=np.int32), walks_per_node)
    walks = np.empty((current.size, walk_length), dtype=np.int32)
    walks[:, 0] = current
    for step in range(1, walk_length):
        if adjacency.nnz:  # conta sem vizinhos fica parada: o passeio dela é só ela mesma
            d = degree[current]
            offset = (rng.random(current.size) * np.maximum(d, 1)).astype(np.int64)
            current = np.where(d > 0, indices[np.minimum(indptr[current] + offset, len(indices) - 1)], current)
        walks[:, step] = current

    pairs_i, pairs_j = [], []
    for gap in range(1, window + 1):
        pairs_i += [walks[:, :-gap].ravel(), walks[:, gap:].ravel()]
        pairs_j += [walks[:, gap:].ravel(), walks[:, :-gap].ravel()]
    i, j = np.concatenate(pairs_i), np.concatenate(pairs_j)
    counts = sp.coo_matrix((np.ones(i.size, dtype=np.float32), (i, j)), shape=(n, n)).tocsr()
    counts.sum_duplicates()

    total = counts.sum()
    row = np.asarray(counts.sum(axis=1)).ravel()
    col = np.asarray(counts.sum(axis=0)).ravel()
    coo = counts.tocoo()
    pmi = np.log(coo.data * total / (row[coo.row] * col[coo.col]))
    keep = pmi > 0
    ppmi = sp.csr_matrix((pmi[keep], (coo.row[keep], coo.col[keep])), shape=(n, n))

    k = max(1, min(dimensions, n - 1))
    embedding = TruncatedSVD(n_components=k, random_state=seed).fit_transform(ppmi) if n > 1 else np.zeros((n, 1))
    return pd.DataFrame(embedding, index=nodes, columns=[f"d{c}" for c in range(embedding.shape[1])])


def node2vec_isolation_forest(
    graph: nx.Graph,
    dimensions: int = 32,
    walks_per_node: int = 10,
    walk_length: int = 20,
    window: int = 5,
    n_estimators: int = 300,
    contamination: float = 0.05,
    seed: int = 42,
) -> Detection:
    """Isolation Forest sobre o vetor de ``node2vec_embedding``.

    O vetor pode ter valores negativos, então não passa por
    ``anomaly.prepare_matrix`` (que aplica log1p): é só padronizado. O rótulo
    binário marca a fração ``contamination`` de maior escore.
    """
    embedding = node2vec_embedding(graph, dimensions, walks_per_node, walk_length, window, seed)
    X = StandardScaler().fit_transform(embedding.to_numpy())
    scores = -IsolationForest(n_estimators=n_estimators, random_state=seed).fit(X).score_samples(X)
    return _detection(scores, _top_fraction(scores, contamination), embedding.index)


GRAPH_DETECTORS = {
    "fraudar": fraudar,
    "node2vec_if": node2vec_isolation_forest,
}
