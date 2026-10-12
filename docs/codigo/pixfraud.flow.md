---
tags: [codigo]
---

# `pixfraud.flow`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/flow.py`](../../src/pixfraud/flow.py) · [mapa do código](mapa-do-codigo.md)

Fluxo de dinheiro, cortes mínimos ("onde bloquear") e propagação de risco.

* `max_money_flow`: quanto dinheiro, no máximo, pode ter ido das contas de
  origem até a conta de destino, se cada aresta só comporta o valor que de fato
  passou por ela (capacidade = `amount`).
* `blocking_cut` e `blocking_accounts`: pelo teorema do fluxo máximo e
  corte mínimo (Ford e Fulkerson), o menor conjunto de Pix (ou de contas) cujo
  bloqueio interrompe todo o fluxo vale exatamente o fluxo máximo.
* `propagate_risk`: "culpa por associação", um PageRank personalizado que
  parte de contas já sabidamente fraudulentas.
* `label_spreading`: a mesma ideia, mas com exemplos positivos e negativos
  (contas sabidamente legítimas puxam as vizinhas para baixo).

As duas últimas são modelos semi-supervisionados e moram em
`pixfraud.models.semi_supervised`; continuam importáveis daqui.

Atenção: no grafo agregado o tempo é ignorado. Para respeitar a ordem dos Pix,
aplique estas funções sobre `pixfraud.temporal.temporal_trail`.

## Classes e funções

### `max_money_flow` (função)

```python
def max_money_flow(graph: nx.DiGraph, sources, sink, capacity: str='amount') -> tuple[float, dict]
```

Fluxo máximo de `sources` (uma conta ou várias) até `sink`.

Devolve `(valor, fluxo)`, em que `fluxo[u][v]` é quanto passa pela
aresta `u -> v` numa solução ótima (só arestas com fluxo positivo).
Várias origens são tratadas com uma "superorigem" ligada a todas elas.

### `blocking_cut` (função)

```python
def blocking_cut(graph: nx.DiGraph, sources, sink, capacity: str='amount') -> tuple[float, list]
```

Corte mínimo: os Pix de menor valor total que separam `sources` de `sink`.

Devolve `(valor do corte, [(u, v, valor), ...])`. Pelo teorema do fluxo
máximo e corte mínimo, o valor do corte é igual ao fluxo máximo.

### `blocking_accounts` (função)

```python
def blocking_accounts(graph: nx.DiGraph, sources, sink) -> list | None
```

Menor conjunto de contas cujo bloqueio separa `sources` de `sink`.

Usa a técnica de *dividir vértices*: cada conta vira um par
`entrada -> saída` com capacidade 1, e as arestas originais têm
capacidade infinita. O corte mínimo nesse grafo auxiliar só pode cortar
pares, ou seja, contas (teorema de Menger). As origens e o destino nunca
são escolhidos. Devolve `None` se alguma origem pagar o destino
diretamente, pois aí nenhum bloqueio de conta intermediária resolve.

### `relevant_accounts` (função)

```python
def relevant_accounts(graph: nx.DiGraph, sources: list, sink) -> set | None
```

Contas que estão em algum caminho de uma origem até o destino.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _as_list(sources) -> list`: Uma conta ou uma coleção de contas, sempre como lista.
- `def _flow_network(graph: nx.DiGraph, sources: list, sink, capacity: str) -> nx.DiGraph | None`: Rede de fluxo só com as contas entre as origens e o destino, com uma super-origem.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`scripts/04_avaliacao/avaliar_gnn_rotulos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_propagacao.py`](scripts.04_avaliacao.md)
- [`tests/test_flow.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
