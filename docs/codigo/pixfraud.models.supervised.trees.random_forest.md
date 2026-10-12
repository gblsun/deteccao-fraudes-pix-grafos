---
tags: [codigo]
---

# `pixfraud.models.supervised.trees.random_forest`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/trees/random_forest.py`](../../src/pixfraud/models/supervised/trees/random_forest.py) · [mapa do código](mapa-do-codigo.md)

Random Forest (Breiman, 2001): muitas árvores de decisão, cada uma vendo uma amostra das contas, votam.

## Classes e funções

### `make_random_forest` (função)

```python
def make_random_forest(n_estimators: int=300, max_depth: int | None=None, min_samples_leaf: int=1, max_features: float | str='sqrt', seed: int=42) -> RandomForestClassifier
```

O classificador, com as fraudes (raras) pesando mais em cada árvore (`balanced_subsample`).

### `random_forest_scores` (função)

```python
def random_forest_scores(features: pd.DataFrame, labels: pd.Series, seed: int=42, folds: int=5, **params) -> pd.Series
```

Probabilidade de fraude por Random Forest, em validação cruzada (ver `out_of_fold_scores`).

`params` vão para `make_random_forest`: `n_estimators`, `max_depth`
(profundidade máxima de cada árvore; `None` = sem limite),
`min_samples_leaf` (contas mínimas por folha) e `max_features` (atributos
sorteados a cada corte).

### `random_forest_known_fraud_scores` (função)

```python
def random_forest_known_fraud_scores(features: pd.DataFrame, known: list, seed: int=42, folds: int=5, **params) -> pd.Series
```

Random Forest treinado só com as fraudes **já conhecidas** (ver `known_fraud_out_of_fold`).

É o par tabular de `graphsage.sage_known_fraud_scores`, com a mesma divisão.

## Quem usa este módulo

- [`pixfraud.models.supervised.trees`](pixfraud.models.supervised.trees.md)
