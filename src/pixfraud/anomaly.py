"""Detectores de anomalia não supervisionados aplicados aos atributos das contas.

Os modelos moraram aqui até serem separados, um arquivo por modelo, em
``pixfraud.models.unsupervised`` (ver ``pixfraud.models``). Este módulo só
reexporta o que estava aqui, para scripts, notebooks e notas antigos
continuarem funcionando; código novo deve importar de ``pixfraud.models``.
"""

from pixfraud.models.base import Detection, prepare_matrix
from pixfraud.models.base import detection as _detection
from pixfraud.models.base import top_fraction as _top_fraction
from pixfraud.models.unsupervised import (
    DETECTORS,
    autoencoder,
    dbscan,
    ecod,
    isolation_forest,
    kmeans,
    knn,
    local_outlier_factor,
    one_class_svm,
    pca,
)

__all__ = [
    "DETECTORS", "Detection", "_detection", "_top_fraction", "autoencoder", "dbscan", "ecod", "isolation_forest",
    "kmeans", "knn", "local_outlier_factor", "one_class_svm", "pca", "prepare_matrix",
]
