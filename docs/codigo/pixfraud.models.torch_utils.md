---
tags: [codigo]
---

# `pixfraud.models.torch_utils`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/torch_utils.py`](../../src/pixfraud/models/torch_utils.py) · [mapa do código](mapa-do-codigo.md)

O que as redes neurais para grafos (DOMINANT e GraphSAGE) compartilham.

Depende do `torch`, que é opcional: `pip install -e ".[gnn]"` (a versão só
para CPU basta: `--index-url https://download.pytorch.org/whl/cpu`). Sem ele
este módulo ainda importa, com `torch = None`, para os scripts poderem
perguntar e pular as GNN.

## Classes e funções

### `require_torch` (função)

```python
def require_torch() -> None
```

Para com uma mensagem clara (e o comando de instalação) se o `torch` não estiver instalado.

### `available` (função)

```python
def available() -> bool
```

O PyTorch e o PyTorch Geometric (usado pela GraphSAGE direcionada) estão instalados?

### `adjacency` (função)

```python
def adjacency(graph: nx.Graph, index: pd.Index) -> tuple[torch.Tensor, torch.Tensor]
```

Matrizes esparsas do grafo não direcionado, na ordem de `index`.

Devolve a adjacência normalizada da GCN, $\hat A = D^{-1/2}(A + I)D^{-1/2}$,
e a média dos vizinhos da GraphSAGE, $D^{-1}A$ (linha zerada para conta sem
vizinhos).

## Quem usa este módulo

- [`pixfraud.gnn`](pixfraud.gnn.md)
- [`pixfraud.models.supervised.neural.graphsage`](pixfraud.models.supervised.neural.graphsage.md)
- [`pixfraud.models.unsupervised.neural.dominant`](pixfraud.models.unsupervised.neural.dominant.md)
