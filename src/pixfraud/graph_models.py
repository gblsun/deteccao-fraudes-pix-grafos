"""Detectores que olham só para a estrutura do grafo, sem a tabela de atributos.

Os modelos (FRAUDAR e node2vec + Isolation Forest) moraram aqui até serem
separados em ``pixfraud.models.unsupervised.fraudar`` e ``.node2vec``. Este
módulo só reexporta o que estava aqui, para scripts, notebooks e notas antigos
continuarem funcionando; código novo deve importar de ``pixfraud.models``.
"""

from pixfraud.models.unsupervised import GRAPH_DETECTORS, fraudar, node2vec_embedding, node2vec_isolation_forest

__all__ = ["GRAPH_DETECTORS", "fraudar", "node2vec_embedding", "node2vec_isolation_forest"]
