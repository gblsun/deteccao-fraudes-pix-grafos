---
tags: [glossario]
---

# Redes neurais para grafos (GNN)

Redes neurais que aprendem uma representação de cada conta **misturando os atributos dela
com os dos vizinhos** (*message passing*). Em vez de calcular [grau](grau.md),
[PageRank](pagerank.md) ou [intermediação](intermediacao.md) à mão, a rede aprende o que
combinar. Cada camada olha um salto a mais: com duas camadas, a conta "vê" os vizinhos dos
vizinhos.

- **GCN** (Kipf e Welling, 2017): cada camada faz uma média ponderada da conta e dos
  vizinhos, $H' = \sigma(\hat A H W)$, com $\hat A = D^{-1/2}(A + I)D^{-1/2}$.
- **GraphSAGE** (Hamilton, Ying e Leskovec, 2017): junta o vetor da própria conta com a
  média dos vizinhos, $h'_v = \sigma(W[h_v \,\|\, \text{média}_{u \in N(v)} h_u])$. Separar a
  conta dos vizinhos ajuda quando fraudadores se ligam a contas normais (vítimas).
- **DOMINANT** (Ding et al., 2019): um autoencoder de grafo, **não supervisionado**. Um
  codificador GCN comprime cada conta e dois decodificadores reconstroem os atributos e as
  ligações; a conta mal reconstruída é anômala.

**Cuidado.** A versão supervisionada precisa de rótulos, e no Pix eles são poucos e
atrasados (ver [MED](med.md)). A avaliação aqui é transdutiva: o grafo inteiro é visto no
treino, só os rótulos das contas de teste ficam escondidos ([validação
cruzada](validacao-cruzada.md)). E o vetor aprendido não é interpretável como um atributo
feito à mão.

**No projeto.** [`pixfraud.gnn`](../../src/pixfraud/gnn.py) (`dominant_scores` e
`sage_supervised_scores`, com PyTorch, sem PyTorch Geometric), avaliado por
[`scripts/avaliar_gnn.py`](../../scripts/avaliar_gnn.py) contra o [Random
Forest](random-forest.md) e o [DBSCAN](dbscan-e-k-distance.md); resultados em
[resultados](../resultados.md).
