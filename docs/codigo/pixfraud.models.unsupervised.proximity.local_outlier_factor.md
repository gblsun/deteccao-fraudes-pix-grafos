---
tags: [codigo]
---

# `pixfraud.models.unsupervised.proximity.local_outlier_factor`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/proximity/local_outlier_factor.py`](../../src/pixfraud/models/unsupervised/proximity/local_outlier_factor.py) · [mapa do código](mapa-do-codigo.md)

Local Outlier Factor (Breunig et al., 2000): a vizinhança da conta é menos densa que a dos vizinhos.

## Classes e funções

### `local_outlier_factor` (função)

```python
def local_outlier_factor(features: pd.DataFrame, n_neighbors: int=20) -> Detection
```

Local Outlier Factor: compara a densidade da conta com a dos seus vizinhos.

Enquanto o DBSCAN usa o mesmo raio para toda a base, o LOF olha para cada
conta em relação à sua vizinhança: uma conta em região esparsa não é
anômala se os vizinhos também estão espalhados. O escore é o fator de
outlier (1 = igual aos vizinhos; quanto maior, mais isolada), e o rótulo
binário é o do próprio LOF.

Gasta memória proporcional a `n_neighbors` por conta, e não ao quadrado
do número de contas como o rótulo exato do DBSCAN.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.proximity`](pixfraud.models.unsupervised.proximity.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
