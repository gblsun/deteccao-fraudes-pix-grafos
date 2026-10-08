"""Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch.

Os modelos moraram aqui até serem separados, um arquivo por modelo, em
``pixfraud.models``:

* ``dominant_scores`` (**não supervisionado**): ``models.unsupervised.neural.dominant``;
* ``sage_supervised_scores`` e ``sage_known_fraud_scores`` (**supervisionado**
  e **poucos rótulos**): ``models.supervised.neural.graphsage``;
* ``graphsage_scores`` (**supervisionado**, variante **direcionada**, com
  PyTorch Geometric): ``models.supervised.neural.graphsage_directed``.

Este módulo só reexporta o que estava aqui, para scripts, notebooks e notas
antigos continuarem funcionando; código novo deve importar de ``pixfraud.models``.
"""

from pixfraud.models.supervised.neural.graphsage import GraphSAGE as _GraphSAGE
from pixfraud.models.supervised.neural.graphsage import fit_sage as _fit_sage
from pixfraud.models.supervised.neural.graphsage import sage_known_fraud_scores, sage_supervised_scores
from pixfraud.models.supervised.neural.graphsage_directed import directed_sage as _DirectedSAGE
from pixfraud.models.supervised.neural.graphsage_directed import graphsage_scores
from pixfraud.models.torch_utils import adjacency as _adjacency
from pixfraud.models.torch_utils import available, nn, torch
from pixfraud.models.torch_utils import require_torch as _require_torch
from pixfraud.models.unsupervised.neural.dominant import dominant_scores

__all__ = [
    "_DirectedSAGE", "_GraphSAGE", "_adjacency", "_fit_sage", "_require_torch", "available", "dominant_scores",
    "graphsage_scores", "nn", "sage_known_fraud_scores", "sage_supervised_scores", "torch",
]
