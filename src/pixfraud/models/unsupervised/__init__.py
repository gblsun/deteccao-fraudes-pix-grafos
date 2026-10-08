"""Modelos **não supervisionados**: não veem o gabarito, procuram as contas que destoam das outras.

Organizados por família, cada uma num subpacote:

* ``proximity/``: ``knn``, ``dbscan``, ``local_outlier_factor`` e ``kmeans``
  (a conta está longe das outras ou numa região pouco densa);
* ``statistical/``: ``pca`` e ``ecod`` (a conta é rara pela distribuição dos atributos);
* ``isolation/``: ``isolation_forest`` (poucos cortes aleatórios isolam a conta);
* ``boundary/``: ``one_class_svm`` (a conta fica fora da fronteira das normais);
* ``neural/``: ``autoencoder`` e ``dominant`` (a rede erra ao reconstruir a conta);
* ``graph/``: ``fraudar`` e ``node2vec`` (só a estrutura do grafo).

Dois registros, com a mesma saída (``base.Detection``):

* ``DETECTORS``: recebem a tabela de atributos das contas, sempre preparada por
  ``base.prepare_matrix`` (log1p e padronização);
* ``GRAPH_DETECTORS``: recebem o grafo.

Fora dos registros, por precisar do ``torch`` e devolver só o escore:
``neural.dominant_scores``.
"""

from pixfraud.models.unsupervised.boundary import one_class_svm
from pixfraud.models.unsupervised.graph import fraudar, node2vec_embedding, node2vec_isolation_forest
from pixfraud.models.unsupervised.isolation import isolation_forest
from pixfraud.models.unsupervised.neural import autoencoder
from pixfraud.models.unsupervised.proximity import dbscan, kmeans, knn, local_outlier_factor
from pixfraud.models.unsupervised.statistical import ecod, pca

DETECTORS = {
    "isolation_forest": isolation_forest,
    "dbscan": dbscan,
    "local_outlier_factor": local_outlier_factor,
    "ecod": ecod,
    "one_class_svm": one_class_svm,
    "autoencoder": autoencoder,
    "knn": knn,
    "kmeans": kmeans,
    "pca": pca,
}

GRAPH_DETECTORS = {
    "fraudar": fraudar,
    "node2vec_if": node2vec_isolation_forest,
}

# Família de cada modelo, para tabelas e figuras agrupadas.
FAMILIES = {
    "isolation_forest": "isolamento",
    "dbscan": "proximidade",
    "local_outlier_factor": "proximidade",
    "knn": "proximidade",
    "kmeans": "proximidade",
    "ecod": "estatístico",
    "pca": "estatístico",
    "one_class_svm": "fronteira",
    "autoencoder": "rede neural",
    "fraudar": "estrutura do grafo",
    "node2vec_if": "estrutura do grafo",
}

__all__ = [
    "DETECTORS", "FAMILIES", "GRAPH_DETECTORS", "autoencoder", "dbscan", "ecod", "fraudar", "isolation_forest",
    "kmeans", "knn", "local_outlier_factor", "node2vec_embedding", "node2vec_isolation_forest", "one_class_svm",
    "pca",
]
