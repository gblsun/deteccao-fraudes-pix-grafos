---
tags: [codigo]
---

# `pixfraud.models.supervised.cross_validation`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/cross_validation.py`](../../src/pixfraud/models/supervised/cross_validation.py) · [mapa do código](mapa-do-codigo.md)

Validação cruzada dos modelos supervisionados: nenhuma conta recebe a nota de um modelo que viu o rótulo dela.

## Classes e funções

### `out_of_fold_scores` (função)

```python
def out_of_fold_scores(model: ClassifierMixin, features: pd.DataFrame, labels: pd.Series, seed: int=42, folds: int=5) -> pd.Series
```

Probabilidade de fraude de cada conta, dada pelo modelo treinado sem ela.

Validação cruzada estratificada: as contas são divididas em `folds`
partes com a mesma proporção de fraudes, e cada parte recebe a previsão do
modelo treinado com as outras.

### `known_fraud_out_of_fold` (função)

```python
def known_fraud_out_of_fold(make_model, features: pd.DataFrame, known: list, seed: int=42, folds: int=5) -> pd.Series
```

Treino só com as fraudes **já conhecidas**; o resto conta como "não fraude".

As contas não rotuladas são separadas em `folds` dobras, e cada uma
recebe a previsão de um modelo (`make_model()`) treinado com as fraudes
conhecidas e as outras dobras. As contas de `known` recebem 1.0; avalie
só nas demais.

## Quem usa este módulo

- [`pixfraud.models.supervised.trees.gradient_boosting`](pixfraud.models.supervised.trees.gradient_boosting.md)
- [`pixfraud.models.supervised.trees.random_forest`](pixfraud.models.supervised.trees.random_forest.md)
