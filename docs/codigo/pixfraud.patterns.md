---
tags: [codigo]
---

# `pixfraud.patterns`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/patterns.py`](../../src/pixfraud/patterns.py) · [mapa do código](mapa-do-codigo.md)

Padrões de fraude como pequenos grafos, para estudo e para injetar em redes maiores.

Cada função devolve um `nx.DiGraph` em que as arestas têm `amount` (valor)
e `count` (nº de Pix) e os vértices têm `role`: `vitima` para contas
honestas que pagaram um golpe, ou um dos papéis de fraude (`laranja`,
`intermediario`, `coletor`). Os formatos seguem os padrões clássicos de
lavagem de dinheiro (fan-in, fan-out, cadeia, ciclo, scatter-gather; ver
`altman2023realistic` em `docs/referencias.bib`).

## Classes e funções

### `fan_in` (função)

```python
def fan_in(n_sources: int=5, amount: float=500.0) -> nx.DiGraph
```

Várias vítimas pagam a mesma conta laranja (muitos -> um).

### `fan_out` (função)

```python
def fan_out(n_targets: int=5, amount: float=2500.0) -> nx.DiGraph
```

Pulverização: a laranja divide o valor entre várias contas (um -> muitos).

### `chain` (função)

```python
def chain(length: int=4, amount: float=1000.0, fee: float=0.03) -> nx.DiGraph
```

Lavagem em cadeia: laranja -> intermediários -> coletor, com comissão `fee` a cada salto.

`length` é o número de contas na cadeia (no mínimo 2).

### `cycle` (função)

```python
def cycle(length: int=4, amount: float=1000.0, fee: float=0.0) -> nx.DiGraph
```

Ciclo (*round-tripping*): o dinheiro passa por várias contas e volta à primeira.

### `scatter_gather` (função)

```python
def scatter_gather(n_middle: int=4, amount: float=1000.0, fee: float=0.02) -> nx.DiGraph
```

Espalha e junta: laranja -> vários intermediários -> coletor.

### `mule_ring` (função)

```python
def mule_ring(n_victims: int=6, n_mules: int=2, chain_length: int=2, amount: float=800.0, fee: float=0.03) -> nx.DiGraph
```

Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.

É o mesmo formato usado pelo gerador do dataset sintético. As vítimas são
distribuídas entre as laranjas em rodízio.

### `inject` (função)

```python
def inject(graph: nx.DiGraph, pattern: nx.DiGraph, prefix: str='padrao', camouflage: int=2, seed: int | None=None) -> nx.DiGraph
```

Copia `pattern` para dentro de `graph` e devolve o novo grafo (o original não muda).

* vértices com papel `vitima` são associados a contas já existentes,
  sorteadas, que passam a ter `role="vitima"`;
* os demais viram contas novas, chamadas `{prefix}_{nome no padrão}`;
* cada conta nova faz `camouflage` Pix pequenos para contas existentes
  sorteadas, para não ficar isolada do resto da rede;
* vértices do grafo original sem papel recebem `role="normal"`.

### `fraud_nodes` (função)

```python
def fraud_nodes(graph: nx.Graph) -> list
```

Vértices cujo `role` é um papel de fraude (laranja, intermediário ou coletor).

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _add(graph: nx.DiGraph, u: str, v: str, amount: float) -> None`: Acrescenta um Pix ao padrão, com o valor arredondado em centavos.
- `def _merge_edge(graph: nx.DiGraph, u, v, amount: float, count: int) -> None`: Soma valor e contagem numa ligação que já existe, ou cria a ligação.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`scripts/ferramentas/gerar_ilustracoes.py`](scripts.ferramentas.md)
- [`tests/test_algorithms.py`](testes.md)
- [`tests/test_patterns.py`](testes.md)
