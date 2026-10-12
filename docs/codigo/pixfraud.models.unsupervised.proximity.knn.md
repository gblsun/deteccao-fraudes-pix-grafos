---
tags: [codigo]
---

# `pixfraud.models.unsupervised.proximity.knn`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/proximity/knn.py`](../../src/pixfraud/models/unsupervised/proximity/knn.py) · [mapa do código](mapa-do-codigo.md)

kNN (Ramaswamy, Rastogi e Shim, 2000): a conta está longe dos seus vizinhos mais próximos.

## Classes e funções

### `knn` (função)

```python
def knn(features: pd.DataFrame, n_neighbors: int=10, method: str='mean', contamination: float=0.05) -> Detection
```

kNN: distância da conta aos seus `n_neighbors` vizinhos mais próximos.

É a ideia mais direta de "conta diferente das outras" (Ramaswamy, Rastogi e
Shim, 2000; Angiulli e Pizzuti, 2002): uma conta cercada de contas parecidas
tem vizinhos perto; uma laranja, com um perfil que quase ninguém tem, fica
longe de todos. `method="mean"` usa a média das `k` distâncias, mais
estável; `"largest"` usa só a `k`-ésima (o escore do `dbscan`). O
rótulo binário marca a fração `contamination` de maior escore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.proximity`](pixfraud.models.unsupervised.proximity.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
