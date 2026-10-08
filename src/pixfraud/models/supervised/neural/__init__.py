"""Redes neurais **para grafos** supervisionadas (precisam do ``torch``, extra ``gnn``).

* ``graphsage``: GraphSAGE própria, com todos os rótulos ou só com as fraudes conhecidas;
* ``graphsage_directed``: GraphSAGE com PyTorch Geometric, uma convolução por sentido do Pix.

Sem o ``torch`` os módulos ainda importam; as funções avisam o que instalar quando chamadas.
"""

from pixfraud.models.supervised.neural.graphsage import sage_known_fraud_scores, sage_supervised_scores
from pixfraud.models.supervised.neural.graphsage_directed import graphsage_scores

__all__ = ["graphsage_scores", "sage_known_fraud_scores", "sage_supervised_scores"]
