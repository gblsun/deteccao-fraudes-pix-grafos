"""Modelos **semi-supervisionados**: usam só as poucas fraudes já conhecidas, como um banco de verdade.

No Pix real, parte das fraudes vira conhecida quando as vítimas contestam
(MED). Estes modelos não são treinados: espalham a suspeita dessas contas pelo
grafo, para achar as que ainda não foram descobertas.

* ``propagate_risk``: PageRank personalizado ("culpa por associação");
* ``label_spreading``: o mesmo, usando também as contas sabidamente legítimas.
"""

from pixfraud.models.semi_supervised.label_spreading import label_spreading
from pixfraud.models.semi_supervised.personalized_pagerank import propagate_risk

__all__ = ["label_spreading", "propagate_risk"]
