---
tags: [codigo]
---

# `pixfraud.tuning.search`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/tuning/search.py`](../../src/pixfraud/tuning/search.py) · [mapa do código](mapa-do-codigo.md)

Dar nota a cada candidato numa rede de validação e escolher o vencedor.

## Classes e funções

### `model_scores` (função)

```python
def model_scores(model: str, prepared, columns: list, params: dict, seed: int) -> pd.Series
```

Escores de `model` numa rede preparada (`experiment.Prepared`), com `params`.

### `average_precision` (função)

```python
def average_precision(labels: pd.Series, scores: pd.Series) -> float
```

AP dos escores conferidos com o gabarito (`labels`), nas contas de `scores`.

### `score_candidates` (função)

```python
def score_candidates(prepared, columns: list, todo: dict[str, list[dict]], current: dict[str, dict], seed: int) -> list[dict]
```

AP de cada candidato de `todo` (`{modelo: [hiperparâmetros, ...]}`) numa rede de validação.

`current` é a configuração atual completa de cada modelo, para marcar a
linha `padrao`.

### `choose` (função)

```python
def choose(runs: pd.DataFrame) -> pd.DataFrame
```

Resumo por (modelo, candidato), com a AP média e qual candidato foi escolhido.

`runs` tem uma linha por (rede de validação, modelo, candidato). Vence o
candidato de maior AP média; num empate, a configuração atual.

### `chosen_params` (função)

```python
def chosen_params(summary: pd.DataFrame) -> dict[str, dict]
```

`{modelo: hiperparâmetros escolhidos}` a partir de `choose`.

## Quem usa este módulo

- [`pixfraud.tuning`](pixfraud.tuning.md)
