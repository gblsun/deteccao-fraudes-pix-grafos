---
tags: [codigo]
---

# `pixfraud.communities`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/communities.py`](../../src/pixfraud/communities.py) · [mapa do código](mapa-do-codigo.md)

Comunidades, núcleos, subgrafos densos e egonets.

Todas as funções trabalham na versão não direcionada do grafo (ida e volta
viram uma aresta só), porque aqui interessa *quem se relaciona com quem*.

* `detect_communities`: Louvain ou propagação de rótulos;
* `participation_coefficient`: quanto as ligações de uma conta se espalham
  por comunidades diferentes (contas-ponte);
* `core_numbers`: decomposição em k-núcleos;
* `densest_subgraph`: subgrafo mais denso pelo algoritmo guloso de Charikar,
  com a opção de pesos do FRAUDAR, que resistem a camuflagem;
* `fraudar_blocks` e `fraudar_scores`: blocos densos em sequência (FRAUDAR) e
  um escore por conta a partir deles, para comparar com os detectores;
* `peeling_scores`: a mesma remoção gulosa transformada em escore por conta
  (o núcleo ponderado), usada pelo detector `fraudar` de `pixfraud.graph_models`;
* `oddball_scores`: anomalias de egonet (OddBall).

## Classes e funções

### `undirected_simple` (função)

```python
def undirected_simple(graph: nx.Graph, weight: str | None=None) -> nx.Graph
```

Versão não direcionada e simples (sem laços). Com `weight`, soma os pesos de ida e volta.

### `detect_communities` (função)

```python
def detect_communities(graph: nx.Graph, method: str='louvain', seed: int=42, weight: str | None=None, resolution: float=1.0) -> pd.Series
```

Comunidade de cada conta (0 = a maior).

`method="louvain"` maximiza a modularidade (Blondel et al., 2008);
`"label_propagation"` é mais rápido: cada conta adota o rótulo mais comum
entre os vizinhos até estabilizar. Por padrão ignora os valores
(`weight=None`); com `weight="amount"`, arestas de valor alto pesam mais.

### `community_summary` (função)

```python
def community_summary(graph: nx.Graph, communities: pd.Series, labels: pd.Series | None=None) -> pd.DataFrame
```

Tamanho, arestas internas e externas de cada comunidade (e nº de fraudes, se `labels`).

### `participation_coefficient` (função)

```python
def participation_coefficient(graph: nx.Graph, communities: pd.Series) -> pd.Series
```

Coeficiente de participação (Guimerà e Amaral, 2005).

$P_i = 1 - \sum_c (k_{ic} / k_i)^2$, em que $k_{ic}$ é o nº de vizinhos de
$i$ na comunidade $c$. Vale 0 quando todos os vizinhos estão numa mesma
comunidade e se aproxima de 1 quando eles se espalham por muitas.

### `core_numbers` (função)

```python
def core_numbers(graph: nx.Graph) -> pd.Series
```

k-núcleo de cada conta: o maior k tal que ela está num subgrafo em que todos têm grau >= k.

### `densest_subgraph` (função)

```python
def densest_subgraph(graph: nx.Graph, weight: str | None=None, fraudar: bool=False) -> tuple[set, float]
```

Subgrafo de maior densidade (peso total / nº de contas), pelo algoritmo guloso de Charikar.

Remove, uma a uma, a conta de menor grau (ponderado) e guarda o melhor
momento. É uma aproximação de fator 2 do ótimo e roda em O(m log n).

Com `fraudar=True`, cada aresta `u -> v` pesa $1 / \log(d^-(v) + 5)$,
como no FRAUDAR (Hooi et al., 2016). Assim, Pix para contas muito
procuradas (comércios) valem pouco, e a camuflagem "pagar a padaria" não
ajuda uma quadrilha a se esconder.

### `fraudar_blocks` (função)

```python
def fraudar_blocks(graph: nx.Graph, max_blocks: int=10, min_size: int=3) -> list[tuple[set, float]]
```

Blocos densos um depois do outro, como no FRAUDAR (Hooi et al., 2016).

Acha o subgrafo mais denso com os pesos do FRAUDAR, tira as contas dele e
procura de novo, até `max_blocks` blocos ou até o bloco ter menos de
`min_size` contas. Os pesos são calculados uma vez, no grafo inteiro. Cada
quadrilha tende a virar um bloco; o número real de quadrilhas não é
conhecido, então `max_blocks` é um limite, não uma resposta.

### `fraudar_scores` (função)

```python
def fraudar_scores(graph: nx.Graph, max_blocks: int=10, min_size: int=3, max_share: float=0.05) -> pd.Series
```

Escore por conta a partir dos blocos do FRAUDAR, para comparar com os detectores.

O FRAUDAR devolve conjuntos de contas, não um escore. Aqui, cada conta de um
bloco recebe a densidade do bloco e as contas fora de qualquer bloco recebem
0. Assim dá para calcular average precision e precision@k como nos outros
detectores.

`max_share`: um bloco com mais que essa fração das contas não é suspeito, é
o próprio tecido da rede. No Pix sintético, os círculos de contatos são
densos, e o primeiro "bloco" costuma ser quase a rede legítima inteira; as
quadrilhas aparecem nos blocos seguintes, pequenos. Esses blocos grandes
continuam sendo retirados (para achar os próximos), mas não pontuam.

### `peeling_scores` (função)

```python
def peeling_scores(graph: nx.Graph, weight: str | None=None, fraudar: bool=True) -> pd.Series
```

Escore por conta tirado da mesma remoção gulosa do `densest_subgraph`.

O escore de uma conta é o maior grau (ponderado) que a remoção já tinha
precisado atingir quando chegou a ela: a generalização do k-núcleo para
pesos. Uma conta num bloco denso só sai quando a remoção já está "cortando
fundo", então fica com escore alto; e, ao contrário do subgrafo mais denso,
que devolve um bloco só, cada bloco denso (cada quadrilha) recebe o seu
nível. Empates são desfeitos pela ordem de remoção: quem sai depois fica
à frente. Com `fraudar=True` (padrão), usa os pesos do FRAUDAR.

### `egonet_features` (função)

```python
def egonet_features(graph: nx.Graph, weight: str='amount') -> pd.DataFrame
```

Medidas da egonet (a conta, seus vizinhos e as arestas entre eles).

* `n_neighbors` ($N$): vizinhos distintos;
* `egonet_edges` ($E$): arestas da egonet = $N$ + triângulos da conta;
* `egonet_weight` ($W$): valor total dos Pix da conta (entrada + saída).

### `oddball_scores` (função)

```python
def oddball_scores(graph: nx.Graph, weight: str='amount') -> pd.DataFrame
```

Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010).

Em redes reais, as egonets seguem leis de potência: $E \propto N^{\alpha}$
e $W \propto E^{\beta}$. Ajustamos as retas em escala log-log e medimos o
quanto cada conta se afasta delas:

$$\text{escore} = \frac{\max(y, \hat y)}{\min(y, \hat y)} \cdot \log(|y - \hat y| + 1)$$

* `oddball_en`: vizinhança "estrela" (vizinhos que não se conhecem, como
  as vítimas de uma laranja) ou "quase clique";
* `oddball_ew`: muito dinheiro para o tamanho da vizinhança.

### `structural_features` (função)

```python
def structural_features(graph: nx.Graph, communities: pd.Series | None=None, seed: int=42) -> pd.DataFrame
```

Atributos `STRUCTURAL_EXTRA` por conta, prontos para `pixfraud.features`.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _densest(simple: nx.Graph) -> tuple[set, float]`: O subgrafo mais denso de um grafo simples com peso em `"weight"` e a densidade dele.
- `def _fraudar_weighted(graph: nx.Graph) -> nx.Graph`: Grafo simples com o peso do FRAUDAR, `1 / log(grau de entrada do destino + 5)`, em cada aresta.
- `def _peel(simple: nx.Graph) -> tuple[list, np.ndarray, np.ndarray]`: Remoção gulosa de Charikar: tira sempre a conta de menor grau ponderado.
- `def _power_law_score(x: pd.Series, y: pd.Series) -> np.ndarray`: Distância de cada ponto à lei de potência ajustada em log-log (escore do OddBall).

## Quem usa este módulo

- [`pixfraud.explorer`](pixfraud.explorer.md)
- [`pixfraud.features`](pixfraud.features.md)
- [`pixfraud.models.torch_utils`](pixfraud.models.torch_utils.md)
- [`pixfraud.models.unsupervised.graph.fraudar`](pixfraud.models.unsupervised.graph.fraudar.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`scripts/04_avaliacao/avaliar_fraudar.py`](scripts.04_avaliacao.md)
- [`tests/test_communities.py`](testes.md)
- [`tests/test_explorer.py`](testes.md)
- [`tests/test_graph_models.py`](testes.md)
