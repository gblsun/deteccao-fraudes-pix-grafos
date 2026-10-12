---
tags: [codigo]
---

# `pixfraud.models.unsupervised.proximity.kmeans`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/proximity/kmeans.py`](../../src/pixfraud/models/unsupervised/proximity/kmeans.py) · [mapa do código](mapa-do-codigo.md)

k-means com a regra do CBLOF (He, Xu e Deng, 2003): a conta está longe dos grupos grandes.

## Classes e funções

### `kmeans` (função)

```python
def kmeans(features: pd.DataFrame, n_clusters: int=8, large_fraction: float=0.9, contamination: float=0.05, seed: int=42) -> Detection
```

k-means: distância da conta ao centro do grupo grande mais próximo.

O k-means divide as contas em `n_clusters` grupos de perfis parecidos
(pessoas que usam pouco o Pix, comércios, quem paga muito...). Uma conta
longe de todos os centros é anômala. Só que um grupo pequeno de contas
estranhas pode ganhar um centro só para ele, e aí ficaria com distância
zero; por isso, como no CBLOF (He, Xu e Deng, 2003), os grupos são
separados em grandes (os maiores, que juntos somam `large_fraction` das
contas) e pequenos, e o escore é a distância ao centro **grande** mais
próximo. O rótulo binário marca a fração `contamination` de maior escore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.proximity`](pixfraud.models.unsupervised.proximity.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
