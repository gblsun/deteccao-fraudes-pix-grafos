---
tags: [codigo]
---

# `pixfraud.models.supervised.trees.gradient_boosting`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/trees/gradient_boosting.py`](../../src/pixfraud/models/supervised/trees/gradient_boosting.py) · [mapa do código](mapa-do-codigo.md)

Gradient boosting (estilo LightGBM): árvores em sequência, cada uma corrigindo o erro das anteriores.

## Classes e funções

### `make_gradient_boosting` (função)

```python
def make_gradient_boosting(max_iter: int=300, learning_rate: float=0.05, min_samples_leaf: int=5, max_leaf_nodes: int=31, l2_regularization: float=0.0, seed: int=42) -> HistGradientBoostingClassifier
```

O classificador, com as classes balanceadas.

Folhas pequenas por padrão: com ~15 fraudes no dataset, o padrão do
scikit-learn (20 contas por folha) não isola nenhuma.

### `gradient_boosting_scores` (função)

```python
def gradient_boosting_scores(features: pd.DataFrame, labels: pd.Series, seed: int=42, folds: int=5, **params) -> pd.Series
```

Probabilidade de fraude por gradient boosting, em validação cruzada (ver `out_of_fold_scores`).

`params` vão para `make_gradient_boosting`: `max_iter` (número de
árvores), `learning_rate` (quanto cada árvore corrige), `min_samples_leaf`,
`max_leaf_nodes` (tamanho de cada árvore) e `l2_regularization`.

## Quem usa este módulo

- [`pixfraud.models.supervised.trees`](pixfraud.models.supervised.trees.md)
