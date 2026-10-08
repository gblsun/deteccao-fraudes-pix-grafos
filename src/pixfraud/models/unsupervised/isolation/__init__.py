"""Modelos de **isolamento**: a conta suspeita se separa das outras com poucos cortes aleatórios.

* ``isolation_forest``: uma floresta de árvores de cortes aleatórios.
"""

from pixfraud.models.unsupervised.isolation.isolation_forest import isolation_forest

__all__ = ["isolation_forest"]
