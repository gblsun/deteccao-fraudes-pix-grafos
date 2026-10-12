---
tags: [codigo]
---

# `pixfraud.evaluation`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/evaluation.py`](../../src/pixfraud/evaluation.py) · [mapa do código](mapa-do-codigo.md)

Métricas de desempenho dos detectores, calculadas por conta.

* `precision`, `recall` e `f1` avaliam o rótulo binário do modelo;
* `roc_auc` e `average_precision` avaliam a ordenação pelo escore, sem
  depender de um limiar (a segunda é mais informativa quando as fraudes são
  raras);
* `precision_at_k`: se um analista revisar as `k` contas mais suspeitas,
  que fração delas é fraude? Por padrão, `k` é o número de fraudes reais.

`recall_by_group` separa o acerto por grupo de contas (por exemplo, a
tipologia de lavagem do AMLworld): quais formatos cada abordagem encontra?

## Classes e funções

### `evaluate` (função)

```python
def evaluate(y_true: pd.Series, detection: Detection, k: int | None=None) -> dict[str, float]
```

Todas as métricas do módulo para uma detecção; `k` padrão = nº de fraudes reais.

### `ranking_metrics` (função)

```python
def ranking_metrics(y_true: pd.Series, scores: pd.Series, k: int | None=None) -> dict[str, float]
```

As métricas que só dependem da ordenação: AP, ROC-AUC e precision@k.

Para abordagens que dão um escore mas não um rótulo binário (propagação de
risco, tetos supervisionados). Contas sem escore contam como escore 0.

### `recall_by_group` (função)

```python
def recall_by_group(members: pd.DataFrame, scores: pd.Series, k: int, by: str='typology') -> pd.DataFrame
```

Fração das contas de cada grupo que está entre as `k` de maior escore.

`members` tem as colunas `account_id` e `by`; uma conta pode estar
em mais de um grupo. Contas fora de `scores` são ignoradas.

## Quem usa este módulo

- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`scripts/04_avaliacao/avaliar_externo.py`](scripts.04_avaliacao.md)
- [`tests/test_anomaly.py`](testes.md)
- [`tests/test_evaluation.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
