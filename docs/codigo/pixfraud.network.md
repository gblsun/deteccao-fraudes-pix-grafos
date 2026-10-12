---
tags: [codigo]
---

# `pixfraud.network`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/network.py`](../../src/pixfraud/network.py) · [mapa do código](mapa-do-codigo.md)

Que tipo de rede é a do Pix? Lei de potência, componente gigante e passeios aleatórios.

Ferramentas para caracterizar a rede de transações e compará-la com os modelos
clássicos (`estudos/05_modelos_de_redes.ipynb` e `06_tipo_de_rede.ipynb`):

* `degree_sequence` e `fit_power_law`: a distribuição de graus segue uma
  lei de potência $P(k) \propto k^{-\alpha}$ na cauda? O expoente é estimado
  por máxima verossimilhança, como em Clauset, Shalizi e Newman (2009);
* `component_summary` e `giant_component`: quanto da rede está numa só
  componente (fraca: ignorando o sentido; forte: seguindo o sentido do dinheiro);
* `compare_network_models`: a rede ao lado de um Erdős–Rényi e de um
  Barabási–Albert do mesmo tamanho;
* `random_walk` e `random_walk_visits`: passeios que seguem o dinheiro,
  escolhendo cada próximo Pix com probabilidade proporcional ao valor. Partindo
  das vítimas, onde o dinheiro termina? (O PageRank é o mesmo passeio com
  "teletransporte"; ver `pixfraud.flow.propagate_risk`.)

A similaridade de cosseno entre contas está em `pixfraud.algorithms`.

## Classes e funções

### `degree_sequence` (função)

```python
def degree_sequence(graph: nx.Graph, kind: str='total') -> np.ndarray
```

Graus dos vértices: nº de contas distintas com que cada conta transaciona.

`kind`: `"in"` (de quantas recebe), `"out"` (para quantas paga) ou
`"total"` (parceiros em qualquer sentido; um par que paga nos dois
sentidos conta uma vez só).

### `fit_power_law` (função)

```python
def fit_power_law(degrees: Iterable[int], k_min: int | None=None, min_tail: int=20) -> dict[str, float]
```

Ajusta uma lei de potência à cauda `k >= k_min` da distribuição de graus.

O expoente vem do estimador de máxima verossimilhança para dados discretos
(aproximação de Clauset et al., 2009, eq. 3.7):

$$\hat\alpha = 1 + n \Big/ \sum_i \ln \frac{k_i}{k_{\min} - 1/2}$$

Sem `k_min`, testa cada grau observado (com pelo menos `min_tail`
vértices na cauda) e fica com o que minimiza a distância de
Kolmogorov–Smirnov `ks` entre a cauda observada e a ajustada. `ks`
pequeno (digamos < 0,05) é compatível com lei de potência; não é um teste
formal, que exigiria o bootstrap de Clauset et al.

### `giant_component` (função)

```python
def giant_component(graph: nx.Graph, strong: bool=False) -> set
```

Vértices da maior componente: fraca (ignora o sentido) ou forte (segue o sentido).

### `component_summary` (função)

```python
def component_summary(graph: nx.DiGraph) -> pd.Series
```

Componentes fracas e fortes e o tamanho relativo da componente gigante de cada tipo.

Numa rede de Pix a componente gigante **fraca** costuma ter quase todas as
contas; a **forte** (dá para ir e voltar seguindo o dinheiro) é menor, porque
muitas contas só pagam (vítimas) ou só recebem (comércios, coletoras).

### `compare_network_models` (função)

```python
def compare_network_models(graph: nx.Graph, seed: int=0, distance_sample: int=200) -> pd.DataFrame
```

A rede ao lado de um Erdős–Rényi e de um Barabási–Albert com o mesmo nº de vértices e arestas.

Todas as redes são tratadas como não direcionadas e simples (os modelos
clássicos são assim). Colunas: grau médio e máximo, expoente e `ks` da
lei de potência, agrupamento médio, fração na componente gigante e
distância média (estimada a partir de `distance_sample` origens).

### `random_walk` (função)

```python
def random_walk(graph: nx.DiGraph, start, max_steps: int=20, weight: str | None='amount', rng: np.random.Generator | int | None=None) -> list
```

Um passeio aleatório que segue o dinheiro a partir de `start`.

A cada passo, sai por um dos Pix enviados pela conta atual, com
probabilidade proporcional a `weight` (`None`: todos iguais). Para ao
chegar numa conta que não pagou ninguém (um sorvedouro) ou depois de
`max_steps` passos. Devolve a lista de contas visitadas, com `start`.

### `random_walk_visits` (função)

```python
def random_walk_visits(graph: nx.DiGraph, starts: Iterable, walks_per_start: int=20, max_steps: int=20, weight: str | None='amount', seed: int=0) -> pd.DataFrame
```

Faz `walks_per_start` passeios a partir de cada conta de `starts`.

Devolve, por conta, a fração dos passeios que passou por ela (`visitas`,
sem contar o ponto de partida) e a fração que terminou nela (`destino`).
Partindo das vítimas, as coletoras aparecem no topo de `destino`: é
para onde o dinheiro do golpe escorre.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _mean_distance(graph: nx.Graph, sample: int, seed: int) -> float`: Distância média na componente gigante, a partir de `sample` origens sorteadas.

## Quem usa este módulo

- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`tests/test_network.py`](testes.md)
