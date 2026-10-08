"""Redes neurais **de reconstrução**: aprendem a reconstruir as contas típicas e erram na suspeita.

* ``autoencoder``: rede densa sobre a tabela de atributos (scikit-learn);
* ``dominant``: autoencoder de grafo, que reconstrói também as ligações
  (PyTorch, extra ``gnn``).
"""

from pixfraud.models.unsupervised.neural.autoencoder import autoencoder
from pixfraud.models.unsupervised.neural.dominant import dominant_scores

__all__ = ["autoencoder", "dominant_scores"]
