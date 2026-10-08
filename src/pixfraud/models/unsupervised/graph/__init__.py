"""Modelos de **estrutura do grafo**: recebem o grafo, não a tabela de atributos.

* ``fraudar``: contas num bloco denso, como uma quadrilha;
* ``node2vec_isolation_forest``: posição rara num vetor aprendido de passeios aleatórios.
"""

from pixfraud.models.unsupervised.graph.fraudar import fraudar
from pixfraud.models.unsupervised.graph.node2vec import node2vec_embedding, node2vec_isolation_forest

__all__ = ["fraudar", "node2vec_embedding", "node2vec_isolation_forest"]
