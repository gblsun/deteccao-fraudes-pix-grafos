---
tags: [codigo]
---

# `pixfraud.models.supervised.neural.graphsage`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/neural/graphsage.py`](../../src/pixfraud/models/supervised/neural/graphsage.py) · [mapa do código](mapa-do-codigo.md)

GraphSAGE (Hamilton, Ying e Leskovec, 2017), implementação própria: rede neural para grafos supervisionada.

Cada conta mistura os seus atributos com a média dos vizinhos, em duas
camadas, e a rede aprende o que combinar. Escrita sem PyTorch Geometric: o
grafo do Pix sintético cabe numa matriz esparsa. Precisa do `torch` (extra
`gnn`). Duas formas de usar:

* `sage_supervised_scores`: treinada com os rótulos, em validação cruzada
  (um teto, como o Random Forest);
* `sage_known_fraud_scores`: só com uma parte das fraudes conhecida e o
  resto das contas sem rótulo, como na culpa por associação.

## Classes e funções

### `GraphSAGE` (classe)

```python
class GraphSAGE(nn.Module if nn is not None else object)
```

Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos vizinhos].

- `def __init__(self, n_features: int, hidden: int, dropout: float)`: Duas camadas GraphSAGE (média dos vizinhos) e a saída de um escore por conta.
- `def forward(self, X, mean)`: Escore de cada conta a partir dos atributos dela e da média dos vizinhos, em duas camadas.

### `sage_supervised_scores` (função)

```python
def sage_supervised_scores(graph: nx.Graph, features: pd.DataFrame, labels: pd.Series, folds: int=5, hidden: int=64, epochs: int=200, dropout: float=0.3, learning_rate: float=0.01, seed: int=42) -> pd.Series
```

Probabilidade de fraude fora da amostra, por uma GraphSAGE em validação cruzada.

Transdutivo, como é comum em GNN: o grafo inteiro (e os atributos de todas
as contas) é visto no treino, mas a perda usa só os rótulos das contas de
treino da dobra, e cada conta recebe a previsão do modelo em que ela ficou
de fora. As fraudes, raras, pesam mais na perda (`pos_weight`).

### `sage_known_fraud_scores` (função)

```python
def sage_known_fraud_scores(graph: nx.Graph, features: pd.DataFrame, known: list, folds: int=5, hidden: int=64, epochs: int=200, dropout: float=0.3, learning_rate: float=0.01, seed: int=42) -> pd.Series
```

GraphSAGE treinada só com as fraudes **já conhecidas**, como no Pix real.

Numa instituição, só parte das contas fraudulentas vira conhecida (quando as
vítimas contestam pelo MED); todas as outras aparecem como "não fraude",
inclusive as fraudes ainda não descobertas. É um problema *positivo e não
rotulado* (PU): aqui tratado do jeito mais simples, com as contas não
rotuladas como negativas.

Para a rede não decorar o "não fraude" das próprias contas que vai avaliar,
as contas não rotuladas são divididas em `folds` dobras: cada dobra recebe
a previsão de um modelo treinado com as fraudes conhecidas e as **outras**
dobras. As contas de `known` recebem 1.0; avalie só nas demais.

### `fit_sage` (função)

```python
def fit_sage(X, mean, y_np: np.ndarray, train: np.ndarray, hidden: int, epochs: int, dropout: float, learning_rate: float, seed: int) -> np.ndarray
```

Treina uma GraphSAGE com os rótulos de `train` e devolve a probabilidade de todas as contas.

As fraudes, raras, pesam mais na perda (`pos_weight`).

## Quem usa este módulo

- [`pixfraud.gnn`](pixfraud.gnn.md)
- [`pixfraud.models.supervised.neural`](pixfraud.models.supervised.neural.md)
