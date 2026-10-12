---
tags: [codigo]
---

# `pixfraud.temporal`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/temporal.py`](../../src/pixfraud/temporal.py) · [mapa do código](mapa-do-codigo.md)

Grafos temporais: caminhos que respeitam a ordem cronológica dos Pix.

No grafo agregado, "existe caminho de A até B" não garante que o dinheiro de A
possa ter chegado a B: os Pix do caminho precisam acontecer em ordem. Aqui as
funções trabalham direto sobre a tabela de transações (colunas `sender`,
`receiver`, `amount` e `timestamp`).

## Classes e funções

### `temporal_reachability` (função)

```python
def temporal_reachability(transactions: pd.DataFrame, account, direction: str='forward', start: pd.Timestamp | str | None=None, end: pd.Timestamp | str | None=None) -> pd.Series
```

Contas ligadas a `account` por caminhos temporais.

* `direction="forward"` (*earliest arrival*): para onde o dinheiro de
  `account`, disponível a partir de `start`, pode ter chegado. O valor
  de cada conta é o primeiro instante em que o dinheiro pode chegar a ela.
* `direction="backward"` (*latest departure*): de onde pode ter vindo o
  dinheiro que estava em `account` até `end`. O valor de cada conta é o
  último instante em que ela ainda pode enviar dinheiro que chegue a
  `account` a tempo.

Uma única passada pelos Pix em ordem cronológica (ou inversa) resolve o
problema: O(m log m) por causa da ordenação.

### `temporal_trail_transactions` (função)

```python
def temporal_trail_transactions(transactions: pd.DataFrame, account, direction: str='forward', max_hops: int | None=None, max_delay: pd.Timedelta | str | None=None, start: pd.Timestamp | str | None=None, end: pd.Timestamp | str | None=None) -> pd.DataFrame
```

Os Pix que formam caminhos temporais a partir de `account` (ou até ela).

Além da ordem cronológica, dá para limitar o número de saltos
(`max_hops`) e o tempo máximo que o dinheiro fica parado em cada conta
intermediária (`max_delay`, ex.: `"2h"`). Isso é útil para seguir
repasses rápidos, típicos de contas laranja.

### `temporal_trail` (função)

```python
def temporal_trail(transactions: pd.DataFrame, account, **kwargs) -> nx.DiGraph
```

Grafo (agregado) dos Pix de `temporal_trail_transactions`; aceita os mesmos parâmetros.

### `dwell_time` (função)

```python
def dwell_time(transactions: pd.DataFrame) -> pd.Series
```

Tempo de permanência do dinheiro, em minutos, por conta.

Para cada Pix recebido, mede quanto tempo a conta leva até fazer o próximo
Pix de saída; o resultado é a mediana dessas esperas. Contas laranja
repassam em minutos; pessoas comuns, em horas ou dias. Contas que nunca
enviam depois de receber ficam de fora do resultado.

### `windowed_in_degree` (função)

```python
def windowed_in_degree(transactions: pd.DataFrame, freq: str='1D') -> pd.DataFrame
```

Grau de entrada por janela de tempo: linhas = janelas, colunas = contas.

Cada célula é o número de pagadores distintos da conta naquela janela
(`freq` no formato do pandas: `"1D"`, `"6h"`, `"7D"`...).

### `temporal_features` (função)

```python
def temporal_features(transactions: pd.DataFrame, accounts: pd.DataFrame, freq: str='1D') -> pd.DataFrame
```

Atributos temporais por conta: `dwell_time_min` e `max_daily_in_degree`.

Contas que nunca repassam recebem como tempo de permanência a duração
total do período, o maior valor possível.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _best_hops(events, t, forward, delay, is_origin)`: Menor nº de saltos entre os eventos compatíveis com um Pix no instante `t`.
- `def _check_direction(direction: str) -> None`: Erro se `direction` não for uma das direções aceitas.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.features`](pixfraud.features.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`tests/test_temporal.py`](testes.md)
