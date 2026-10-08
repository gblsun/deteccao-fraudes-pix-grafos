"""Modelos **estatísticos**: a conta suspeita é rara segundo a distribuição dos atributos.

* ``pca``: foge da correlação entre os atributos (componentes principais);
* ``ecod``: está na cauda de vários atributos, cada um olhado sozinho.
"""

from pixfraud.models.unsupervised.statistical.ecod import ecod
from pixfraud.models.unsupervised.statistical.pca import pca

__all__ = ["ecod", "pca"]
