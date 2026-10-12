---
tags: [codigo]
---

# `pixfraud.models.unsupervised.graph.node2vec`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/graph/node2vec.py`](../../src/pixfraud/models/unsupervised/graph/node2vec.py) · [mapa do código](mapa-do-codigo.md)

node2vec + Isolation Forest: cada conta vira um vetor aprendido da sua vizinhança.

O vetor vem de passeios aleatórios (como no DeepWalk/node2vec com p = q = 1),
e o Isolation Forest procura as contas em posições raras desse espaço. Olha
só para a estrutura do grafo, sem a tabela de atributos.

## Classes e funções

### `node2vec_embedding` (função)

```python
def node2vec_embedding(graph: nx.Graph, dimensions: int=32, walks_per_node: int=10, walk_length: int=20, window: int=5, seed: int=42) -> pd.DataFrame
```

Um vetor por conta, aprendido dos passeios aleatórios que passam por ela.

Faz `walks_per_node` passeios uniformes de `walk_length` passos a partir
de cada conta (no grafo não direcionado), conta quantas vezes duas contas
aparecem a até `window` passos uma da outra, transforma as contagens em
PPMI (informação mútua pontual positiva) e reduz a `dimensions` colunas
com SVD truncado. É a formulação do skip-gram (word2vec) como fatoração de
matriz (Levy e Goldberg, 2014), o mesmo objetivo do DeepWalk e do node2vec
com p = q = 1, sem precisar de uma biblioteca de redes neurais.

### `node2vec_isolation_forest` (função)

```python
def node2vec_isolation_forest(graph: nx.Graph, dimensions: int=32, walks_per_node: int=10, walk_length: int=20, window: int=5, n_estimators: int=300, contamination: float=0.05, seed: int=42) -> Detection
```

Isolation Forest sobre o vetor de `node2vec_embedding`.

O vetor pode ter valores negativos, então não passa por
`base.prepare_matrix` (que aplica log1p): é só padronizado. O rótulo
binário marca a fração `contamination` de maior escore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.graph`](pixfraud.models.unsupervised.graph.md)
