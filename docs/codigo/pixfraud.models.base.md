---
tags: [codigo]
---

# `pixfraud.models.base`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/base.py`](../../src/pixfraud/models/base.py) · [mapa do código](mapa-do-codigo.md)

O que todos os modelos compartilham: o formato da saída e a preparação dos atributos.

## Classes e funções

### `Detection` (classe)

```python
class Detection
```

Resultado de um detector: um escore contínuo e um rótulo binário por conta.

Os escores servem para ordenar as contas (AP, precision@k, grafo de calor); a
escala depende do modelo, então só a ordem é comparável entre detectores.

### `prepare_matrix` (função)

```python
def prepare_matrix(features: pd.DataFrame) -> np.ndarray
```

Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza cada coluna.

### `top_fraction` (função)

```python
def top_fraction(scores: np.ndarray, fraction: float) -> np.ndarray
```

Rótulo binário dos detectores que só dão escore: a fração `fraction` de maior escore.

### `detection` (função)

```python
def detection(scores, is_anomaly, index) -> Detection
```

Monta um `Detection` a partir de arrays alinhados com `index`.

## Quem usa este módulo

- [`pixfraud.anomaly`](pixfraud.anomaly.md)
- [`pixfraud.models.supervised.neural.graphsage_directed`](pixfraud.models.supervised.neural.graphsage_directed.md)
- [`pixfraud.models.supervised.neural.graphsage`](pixfraud.models.supervised.neural.graphsage.md)
- [`pixfraud.models.unsupervised.boundary.one_class_svm`](pixfraud.models.unsupervised.boundary.one_class_svm.md)
- [`pixfraud.models.unsupervised.graph.fraudar`](pixfraud.models.unsupervised.graph.fraudar.md)
- [`pixfraud.models.unsupervised.graph.node2vec`](pixfraud.models.unsupervised.graph.node2vec.md)
- [`pixfraud.models.unsupervised.isolation.isolation_forest`](pixfraud.models.unsupervised.isolation.isolation_forest.md)
- [`pixfraud.models.unsupervised.neural.autoencoder`](pixfraud.models.unsupervised.neural.autoencoder.md)
- [`pixfraud.models.unsupervised.neural.dominant`](pixfraud.models.unsupervised.neural.dominant.md)
- [`pixfraud.models.unsupervised.proximity.dbscan`](pixfraud.models.unsupervised.proximity.dbscan.md)
- [`pixfraud.models.unsupervised.proximity.kmeans`](pixfraud.models.unsupervised.proximity.kmeans.md)
- [`pixfraud.models.unsupervised.proximity.knn`](pixfraud.models.unsupervised.proximity.knn.md)
- [`pixfraud.models.unsupervised.proximity.local_outlier_factor`](pixfraud.models.unsupervised.proximity.local_outlier_factor.md)
- [`pixfraud.models.unsupervised.statistical.ecod`](pixfraud.models.unsupervised.statistical.ecod.md)
- [`pixfraud.models.unsupervised.statistical.pca`](pixfraud.models.unsupervised.statistical.pca.md)
- [`pixfraud.models`](pixfraud.models.md)
