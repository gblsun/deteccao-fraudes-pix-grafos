---
tags: [codigo]
---

# `pixfraud.models.supervised.neural.graphsage_directed`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/neural/graphsage_directed.py`](../../src/pixfraud/models/supervised/neural/graphsage_directed.py) · [mapa do código](mapa-do-codigo.md)

GraphSAGE direcionada, com PyTorch Geometric: uma convolução para quem pagou a conta e outra para quem recebeu.

Supervisionada, com parada antecipada pela average precision. É a usada por
`avaliar_atributos.py` e `avaliar_modelos.py`; precisa do
`torch_geometric` (`torch_utils.available()` diz se ele está instalado).
`graphsage.sage_supervised_scores` e esta são duas implementações do mesmo
teto, feitas em paralelo (a primeira sustenta as seções 10 e 11 de
`docs/resultados.md`); a comparação entre elas ainda não foi feita.

## Classes e funções

### `graphsage_scores` (função)

```python
def graphsage_scores(graph: nx.DiGraph, features: pd.DataFrame, labels: pd.Series, seed: int=42, folds: int=5, hidden: int=64, epochs: int=200, learning_rate: float=0.01, dropout: float=0.3, patience: int=20) -> pd.Series
```

Probabilidade de fraude de cada conta dada por uma GraphSAGE treinada com os rótulos.

Validação cruzada **transdutiva** de `folds` partes: a rede vê o grafo
inteiro (quem pagou quem é conhecido também para as contas de teste), mas
a perda só usa os rótulos das contas de treino, e cada conta recebe a
previsão do modelo que não viu o rótulo dela. A perda pesa as fraudes pela
raridade, e o treino para quando a average precision numa parte separada
do treino deixa de melhorar por `patience` épocas.

Os atributos de cada conta passam pela mesma preparação dos detectores
(log1p e padronização). O grafo é direcionado: em cada camada, uma
convolução junta quem pagou a conta e outra, quem recebeu dela.

### `directed_sage` (função)

```python
def directed_sage(in_dim: int, hidden: int, dropout: float)
```

GraphSAGE de 2 camadas com uma convolução para cada sentido do Pix.

## Quem usa este módulo

- [`pixfraud.gnn`](pixfraud.gnn.md)
- [`pixfraud.models.supervised.neural`](pixfraud.models.supervised.neural.md)
