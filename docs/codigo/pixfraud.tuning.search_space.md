---
tags: [codigo]
---

# `pixfraud.tuning.search_space`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/tuning/search_space.py`](../../src/pixfraud/tuning/search_space.py) · [mapa do código](mapa-do-codigo.md)

O espaço de busca: quais valores de cada hiperparâmetro testar, e como ampliá-lo.

As grades ficam em `configs/busca_hiperparametros.yaml`. Cada hiperparâmetro
é um `Param`: a lista de valores testados e, se numérico, os limites. Quando
o vencedor cai numa ponta da lista, `expand` acrescenta um valor além dela
(ver `Param.beyond`).

## Classes e funções

### `Param` (classe)

```python
class Param
```

Os valores testados de um hiperparâmetro e, se ele puder crescer, os limites.

- `def expandable(self) -> bool`: A grade pode ser ampliada (há limites inferior e superior definidos)?
- `def numeric(self) -> list[float]`: Os valores numéricos testados, em ordem (`None`, textos e booleanos ficam de fora).
- `def beyond(self, value) -> object | None`: Um valor além de `value`, se ele for a ponta da lista; `None` se não houver para onde ir.
- `def with_value(self, value) -> Param`: Cópia do parâmetro com mais um valor na grade.

### `load_search_spaces` (função)

```python
def load_search_spaces(path: str | Path=DEFAULT_PATH) -> dict[str, dict[str, Param]]
```

Lê as grades do YAML: `{modelo: {hiperparâmetro: Param}}`.

### `model_function` (função)

```python
def model_function(model: str)
```

A função de `model` num dos registros de `pixfraud.models`.

### `full_params` (função)

```python
def full_params(model: str, current: dict, space: dict | None=None) -> dict
```

`current` completado com o valor padrão de cada hiperparâmetro de `space`.

Assim a configuração atual é reconhecida quando a grade testa o mesmo valor
(ex.: `method="mean"` do kNN, que a configuração não escreve). Os
supervisionados recebem os hiperparâmetros pela fábrica do classificador.

### `grid` (função)

```python
def grid(space: dict) -> list[dict]
```

Todas as combinações de `space` (`{hiperparâmetro: Param ou lista de valores}`).

### `candidates` (função)

```python
def candidates(model: str, current: dict, space: dict) -> list[dict]
```

A configuração atual (primeiro) e cada combinação da grade aplicada sobre ela, sem repetir.

### `params_key` (função)

```python
def params_key(params: dict) -> str
```

Texto estável de um conjunto de hiperparâmetros (para agrupar e gravar em CSV).

### `expand` (função)

```python
def expand(space: dict[str, Param], chosen: dict) -> tuple[dict[str, Param], list[str]]
```

Amplia `space` onde o vencedor `chosen` caiu numa ponta da lista.

Devolve o espaço novo e a descrição do que mudou (vazia se nada mudou, e aí
a busca daquele modelo terminou).

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _tidy(value)`: Arredonda floats a 4 algarismos significativos, para os valores gravados ficarem legíveis.

## Quem usa este módulo

- [`pixfraud.tuning.search`](pixfraud.tuning.search.md)
- [`pixfraud.tuning`](pixfraud.tuning.md)
