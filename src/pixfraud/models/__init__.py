"""Todos os modelos de detecção, um arquivo por modelo, agrupados por tipo e por família.

::

    models/
      base.py                  Detection, prepare_matrix: o que todos compartilham
      torch_utils.py           o que as redes neurais para grafos compartilham (torch opcional)
      unsupervised/            não veem o gabarito: procuram o que destoa
        proximity/             knn, dbscan, local_outlier_factor, kmeans
        statistical/           pca, ecod
        isolation/             isolation_forest
        boundary/              one_class_svm
        neural/                autoencoder, dominant (torch)
        graph/                 fraudar, node2vec
      semi_supervised/         usam só as poucas fraudes já conhecidas
        personalized_pagerank.py, label_spreading.py
      supervised/              aprendem com o gabarito, em validação cruzada
        cross_validation.py
        trees/                 random_forest, gradient_boosting
        neural/                graphsage, graphsage_directed (torch)

Os registros ``DETECTORS``, ``GRAPH_DETECTORS`` e ``SUPERVISED`` ligam o nome
de cada modelo (o mesmo de ``configs/experimento.yaml``) à função. Os módulos
antigos ``pixfraud.anomaly``, ``pixfraud.graph_models`` e ``pixfraud.gnn`` (e
as funções de propagação em ``pixfraud.flow``) continuam funcionando: só
reexportam o que está aqui.
"""

from pixfraud.models.base import Detection, prepare_matrix
from pixfraud.models.supervised import FACTORIES, SUPERVISED
from pixfraud.models.unsupervised import DETECTORS, FAMILIES, GRAPH_DETECTORS

__all__ = ["DETECTORS", "FACTORIES", "FAMILIES", "GRAPH_DETECTORS", "SUPERVISED", "Detection", "prepare_matrix"]
