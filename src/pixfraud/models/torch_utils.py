"""O que as redes neurais para grafos (DOMINANT e GraphSAGE) compartilham.

Depende do ``torch``, que é opcional: ``pip install -e ".[gnn]"`` (a versão só
para CPU basta: ``--index-url https://download.pytorch.org/whl/cpu``). Sem ele
este módulo ainda importa, com ``torch = None``, para os scripts poderem
perguntar e pular as GNN.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from pixfraud.communities import undirected_simple

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - depende do ambiente
    torch = nn = None


def require_torch() -> None:
    """Para com uma mensagem clara (e o comando de instalação) se o ``torch`` não estiver instalado."""
    if torch is None:
        raise ImportError('as redes neurais para grafos precisam do torch: pip install -e ".[gnn]"')


def available() -> bool:
    """O PyTorch e o PyTorch Geometric (usado pela GraphSAGE direcionada) estão instalados?"""
    try:
        import torch  # noqa: F401
        import torch_geometric  # noqa: F401
    except ImportError:
        return False
    return True


def adjacency(graph: nx.Graph, index: pd.Index) -> tuple[torch.Tensor, torch.Tensor]:
    """Matrizes esparsas do grafo não direcionado, na ordem de ``index``.

    Devolve a adjacência normalizada da GCN, $\\hat A = D^{-1/2}(A + I)D^{-1/2}$,
    e a média dos vizinhos da GraphSAGE, $D^{-1}A$ (linha zerada para conta sem
    vizinhos).
    """
    simple = undirected_simple(graph)
    position = {v: i for i, v in enumerate(index)}
    edges = np.array([(position[u], position[v]) for u, v in simple.edges() if u in position and v in position],
                     dtype=np.int64).reshape(-1, 2)
    n = len(index)
    rows = np.concatenate([edges[:, 0], edges[:, 1]])
    cols = np.concatenate([edges[:, 1], edges[:, 0]])
    degree = np.bincount(rows, minlength=n).astype(np.float32)

    self_loops = np.arange(n)
    gcn_rows, gcn_cols = np.concatenate([rows, self_loops]), np.concatenate([cols, self_loops])
    inv_sqrt = 1.0 / np.sqrt(degree + 1.0)
    gcn_values = inv_sqrt[gcn_rows] * inv_sqrt[gcn_cols]
    gcn = torch.sparse_coo_tensor(np.vstack([gcn_rows, gcn_cols]), gcn_values.astype(np.float32), (n, n),
                                  check_invariants=False)

    mean_values = 1.0 / np.maximum(degree[rows], 1.0)
    mean = torch.sparse_coo_tensor(np.vstack([rows, cols]), mean_values.astype(np.float32), (n, n),
                                   check_invariants=False)
    return gcn.coalesce(), mean.coalesce()
