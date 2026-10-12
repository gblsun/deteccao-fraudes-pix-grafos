---
tags: [codigo]
---

# `pixfraud.graph`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/graph.py`](../../src/pixfraud/graph.py) · [mapa do código](mapa-do-codigo.md)

Criação e manipulação dos grafos: contas são vértices e transferências são arestas.

## Classes e funções

### `build_graph` (função)

```python
def build_graph(transactions: pd.DataFrame, accounts: Iterable[str] | None=None) -> nx.DiGraph
```

Monta o grafo direcionado de transações.

Todas as transferências de um mesmo par (pagador, recebedor) são agregadas
em uma única aresta direcionada, com os atributos `amount` (valor total)
e `count` (número de transferências). Se `accounts` for informado,
contas sem nenhuma transação também entram no grafo, como vértices isolados.

### `graph_from_edges` (função)

```python
def graph_from_edges(edges: Iterable[tuple], directed: bool=True, multigraph: bool=False) -> nx.Graph
```

Cria um grafo a partir de uma lista de arestas; prático para exemplos e exercícios.

Cada aresta é `(origem, destino)` ou `(origem, destino, valor)`; o valor
vira o atributo `amount` (1 quando omitido). Sem `multigraph`, arestas
repetidas entre o mesmo par são somadas em uma só, e `count` guarda
quantas eram. Com `multigraph=True`, cada uma vira uma aresta paralela.

>>> G = graph_from_edges([("ana", "bia", 50), ("bia", "caio", 20), ("ana", "bia", 30)])
>>> G["ana"]["bia"]
{'amount': 80.0, 'count': 2}

### `graph_from_csv` (função)

```python
def graph_from_csv(path: str | Path, source: str='sender', target: str='receiver', amount: str='amount', aggregate: bool=True, **read_csv_kwargs) -> nx.DiGraph | nx.MultiDiGraph
```

Lê uma tabela de transações em CSV e monta o grafo.

`source`, `target` e `amount` são os nomes das colunas de origem,
destino e valor (sem coluna de valor, cada linha vale 1). Com
`aggregate=True` devolve um `DiGraph` com uma aresta por par, como
`build_graph`. Com `aggregate=False` devolve um `MultiDiGraph` com uma
aresta por linha, mantendo as demais colunas (ex.: `timestamp`) como
atributos da aresta.

### `adjacency_matrix` (função)

```python
def adjacency_matrix(graph: nx.Graph, weight: str | None=None) -> pd.DataFrame
```

Matriz de adjacência rotulada: linha = origem, coluna = destino.

Com `weight=None` cada célula vale 1 se a aresta existe (num multigrafo,
o número de arestas paralelas); com `weight="amount"`, o valor total.

### `money_trail` (função)

```python
def money_trail(graph: nx.DiGraph, account, max_hops: int=3, direction: str='forward') -> nx.DiGraph
```

Subgrafo das contas alcançáveis a partir de `account` em até `max_hops` saltos.

`direction="forward"` segue o dinheiro (para onde ele foi),
`"backward"` volta à origem (de onde ele veio) e `"both"` faz os dois.
O subgrafo é induzido: inclui todas as arestas entre as contas alcançadas.

### `describe` (função)

```python
def describe(graph: nx.Graph) -> pd.Series
```

Resumo das propriedades básicas do grafo (útil para conferir exercícios).

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.temporal`](pixfraud.temporal.md)
- [`scripts/01_dados/validar_realismo.py`](scripts.01_dados.md)
- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`scripts/ferramentas/gerar_ilustracoes.py`](scripts.ferramentas.md)
- [`tests/test_algorithms.py`](testes.md)
- [`tests/test_exploration.py`](testes.md)
- [`tests/test_explorer.py`](testes.md)
- [`tests/test_external.py`](testes.md)
- [`tests/test_features.py`](testes.md)
- [`tests/test_flow.py`](testes.md)
- [`tests/test_graph_models.py`](testes.md)
- [`tests/test_graph_tools.py`](testes.md)
- [`tests/test_network.py`](testes.md)
- [`tests/test_patterns.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
- [`tests/test_temporal.py`](testes.md)
