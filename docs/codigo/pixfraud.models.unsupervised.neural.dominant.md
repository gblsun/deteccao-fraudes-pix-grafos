---
tags: [codigo]
---

# `pixfraud.models.unsupervised.neural.dominant`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/neural/dominant.py`](../../src/pixfraud/models/unsupervised/neural/dominant.py) · [mapa do código](mapa-do-codigo.md)

DOMINANT (Ding et al., 2019): autoencoder de grafo, uma rede neural não supervisionada.

Um codificador GCN comprime cada conta; um decodificador reconstrói os
atributos e outro reconstrói as ligações. A conta que a rede não consegue
reconstruir, nos atributos ou em quem ela conhece, é anômala. Precisa do
`torch` (extra `gnn`).

## Classes e funções

### `dominant_scores` (função)

```python
def dominant_scores(graph: nx.Graph, features: pd.DataFrame, hidden: int=64, latent: int=32, epochs: int=300, alpha: float=0.5, learning_rate: float=0.005, seed: int=42, max_nodes: int=20000) -> pd.Series
```

Escore de anomalia do DOMINANT: erro de reconstrução dos atributos e das ligações.

O escore é `alpha` × erro dos atributos + (1 - `alpha`) × erro da
estrutura, com os dois erros divididos pela própria média para ficarem na
mesma escala. A reconstrução da estrutura compara a linha inteira da
adjacência, o que custa memória proporcional ao **quadrado** do nº de
contas; acima de `max_nodes` contas, a função recusa em vez de travar a
máquina.

## Quem usa este módulo

- [`pixfraud.gnn`](pixfraud.gnn.md)
- [`pixfraud.models.unsupervised.neural`](pixfraud.models.unsupervised.neural.md)
