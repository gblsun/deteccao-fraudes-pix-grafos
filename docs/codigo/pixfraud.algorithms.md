---
tags: [codigo]
---

# `pixfraud.algorithms`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/algorithms.py`](../../src/pixfraud/algorithms.py) · [mapa do código](mapa-do-codigo.md)

Algoritmos clássicos de teoria dos grafos aplicados às transações.

| Função | Algoritmo | Pergunta que responde |
|---|---|---|
| `money_backbone` | ramificação máxima (Edmonds) | qual a principal origem do dinheiro de cada conta? |
| `widest_path` | caminho gargalo (Dijkstra modificado) | qual o maior valor que passa por uma única rota? |
| `laundering_depth`, `longest_chain` | condensação + maior caminho em DAG | por quantas camadas o dinheiro passa? |
| `find_pattern` | monomorfismo de subgrafos (VF2) | onde este formato aparece na rede? |
| `hubs_authorities` | HITS | quem distribui e quem concentra? |
| `similar_accounts` | Jaccard / cosseno / SimRank | que contas se parecem com esta? |
| `cosine_similarity`, `vector_angle` | produto interno | quão alinhados estão dois vetores? |
| `bipartite_projection` | projeção de grafo bipartido | que vítimas pagaram as mesmas laranjas? |

## Classes e funções

### `money_backbone` (função)

```python
def money_backbone(graph: nx.DiGraph, weight: str='amount') -> nx.DiGraph
```

Espinha dorsal do dinheiro: a ramificação de peso máximo (algoritmo de Edmonds).

Uma *ramificação* é uma floresta de arborescências: cada conta fica com no
máximo uma aresta de entrada, sem ciclos. A de peso máximo guarda, para
cada conta, a origem que mais contribuiu para o seu dinheiro (exceto
quando isso formaria um ciclo). O resultado é uma "árvore genealógica" do
dinheiro, bem mais fácil de desenhar que a rede inteira.

### `widest_path` (função)

```python
def widest_path(graph: nx.DiGraph, source, target, weight: str='amount') -> tuple[list, float]
```

Caminho gargalo: a rota de `source` até `target` cuja menor aresta é a maior possível.

É o Dijkstra com duas trocas: em vez de somar, toma o mínimo ao longo do
caminho, e em vez de minimizar, maximiza. O valor devolvido é o maior
montante que poderia ter seguido *uma única rota*. Devolve `([], 0.0)`
se não houver caminho.

### `laundering_depth` (função)

```python
def laundering_depth(graph: nx.DiGraph) -> pd.Series
```

Por quantas camadas o dinheiro ainda pode passar depois de sair de cada conta.

As componentes fortemente conexas viram vértices (condensação, sempre um
DAG). A profundidade de uma componente é o comprimento do maior caminho
que sai dela, calculado de trás para a frente na ordem topológica
(programação dinâmica). Contas da mesma componente têm a mesma profundidade.

### `longest_chain` (função)

```python
def longest_chain(graph: nx.DiGraph) -> list
```

Maior cadeia (caminho mais longo) de um grafo acíclico, como uma trilha de lavagem.

### `find_pattern` (função)

```python
def find_pattern(graph: nx.DiGraph, pattern: nx.DiGraph, induced: bool=False, max_results: int=100, candidates: Iterable | None=None) -> list[dict]
```

Ocorrências do formato `pattern` dentro de `graph` (algoritmo VF2).

Cada ocorrência é um dicionário `{vértice do padrão: conta}`. Com
`induced=False` (monomorfismo), a rede pode ter arestas a mais entre as
contas encontradas; com `induced=True` (isomorfismo de subgrafo
induzido), não pode. A busca é exponencial no pior caso, então limite o
número de resultados (`max_results`) ou restrinja a busca a um conjunto
de contas suspeitas (`candidates`).

### `hubs_authorities` (função)

```python
def hubs_authorities(graph: nx.DiGraph, max_iter: int=1000) -> pd.DataFrame
```

HITS (Kleinberg): *hubs* apontam para boas autoridades; *autoridades* recebem de bons hubs.

Numa rede de Pix, autoridades concentram dinheiro vindo de contas que
pagam muita gente (coletores, comércios), e hubs distribuem.

### `similar_accounts` (função)

```python
def similar_accounts(graph: nx.DiGraph, account, method: str='jaccard_out', top: int=10) -> pd.Series
```

Contas mais parecidas com `account` pela vizinhança.

* `"jaccard_out"`: quem paga as mesmas contas (laranjas de uma quadrilha
  repassam para o mesmo intermediário);
* `"jaccard_in"`: quem recebe das mesmas contas;
* `"jaccard"`: vizinhos em qualquer sentido;
* `"cosine_out"` e `"cosine_in"`: como os Jaccard de mesmo sentido, mas
  cada conta vira o vetor dos **valores** pagos a (ou recebidos de) cada
  conta, e a similaridade é o cosseno do ângulo entre os vetores
  (`cosine_similarity`): pagar as mesmas contas em proporções parecidas;
* `"simrank"`: "são parecidas as contas pagas por contas parecidas"
  (recursivo, bem mais lento).

Jaccard: $|N(a) \cap N(b)| / |N(a) \cup N(b)|$.

### `cosine_similarity` (função)

```python
def cosine_similarity(a, b) -> float
```

Cosseno do ângulo entre os vetores `a` e `b`.

$$\cos\theta = \frac{a \cdot b}{\lVert a \rVert \, \lVert b \rVert}
= \frac{\sum_i a_i b_i}{\sqrt{\sum_i a_i^2}\,\sqrt{\sum_i b_i^2}}$$

Vale 1 quando os vetores apontam no mesmo sentido (ângulo 0°), 0 quando
são perpendiculares (90°) e -1 quando são opostos (180°). Só a direção
importa: `a` e `2a` têm cosseno 1. Com valores de Pix, que nunca são
negativos, o resultado fica entre 0 e 1. Com um vetor nulo, devolve 0.

### `vector_angle` (função)

```python
def vector_angle(a, b, degrees: bool=True) -> float
```

Ângulo entre `a` e `b`: $\theta = \arccos(\cos\theta)$, em graus (ou radianos).

É a mesma informação que `cosine_similarity` em outra escala: cosseno
1 ↔ 0°, cosseno 0 ↔ 90°. Por isso "similaridade de cosseno" e "ângulo
entre vetores" são a mesma medida.

### `bipartite_projection` (função)

```python
def bipartite_projection(graph: nx.DiGraph, left: Iterable, right: Iterable) -> nx.Graph
```

Projeção do grafo bipartido `left` × `right` sobre `left`.

Duas contas de `left` ficam ligadas se se relacionam (em qualquer
sentido) com alguma conta em comum de `right`; o peso da aresta é o
número de contas em comum. Ex.: com vítimas × laranjas, as componentes
da projeção revelam as quadrilhas.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _amounts(graph: nx.DiGraph, account, partners: list, method: str) -> list[float]`: Vetor dos valores entre `account` e cada conta de `partners` (0 se não houve Pix).

## Quem usa este módulo

- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`tests/test_algorithms.py`](testes.md)
