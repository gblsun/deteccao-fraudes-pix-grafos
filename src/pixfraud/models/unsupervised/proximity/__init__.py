"""Modelos de **proximidade**: a conta suspeita está longe das outras ou numa região pouco densa.

Todos medem distâncias entre contas no espaço dos atributos; muda a régua.

* ``knn``: distância aos ``k`` vizinhos mais próximos;
* ``dbscan``: fora das regiões densas, com um raio único para todos;
* ``local_outlier_factor``: densidade da conta comparada com a dos vizinhos;
* ``kmeans``: distância ao centro do grupo grande de perfis mais próximo.
"""

from pixfraud.models.unsupervised.proximity.dbscan import dbscan
from pixfraud.models.unsupervised.proximity.kmeans import kmeans
from pixfraud.models.unsupervised.proximity.knn import knn
from pixfraud.models.unsupervised.proximity.local_outlier_factor import local_outlier_factor

__all__ = ["dbscan", "kmeans", "knn", "local_outlier_factor"]
