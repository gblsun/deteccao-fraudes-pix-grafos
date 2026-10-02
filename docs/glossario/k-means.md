---
tags: [glossario]
---

# K-Means

Divide as contas em $K$ grupos, cada um representado pelo seu centro (a média dos
atributos das contas do grupo). O algoritmo alterna dois passos até estabilizar: cada
conta vai para o centro mais próximo, e cada centro passa a ser a média do seu grupo.

**Como detector de anomalia.** Uma conta típica fica perto do centro do seu grupo; o
escore é a distância até o centro mais próximo.

$$\text{escore}(v) = \min_{c \in \text{grupos grandes}} \lVert x_v - \mu_c \rVert$$

**O cuidado dos grupos pequenos.** Contas anômalas parecidas entre si (as laranjas de uma
quadrilha) podem formar um grupo só delas e ficar a distância quase zero do centro dele.
Por isso, grupos com menos de `min_cluster_fraction` das contas (1%) não contam como
"normais", e a distância é medida até um grupo grande. É a ideia do CBLOF (He et al.,
2003).

**Não supervisionado**, como o [Isolation Forest](isolation-forest.md) e o
[DBSCAN](dbscan-e-k-distance.md): não usa rótulos e é comparado com eles pelas mesmas
métricas de ranking.

**No projeto.** [`anomaly.kmeans`](../../src/pixfraud/anomaly.py), com $K = 8$ em
[`configs/experimento.yaml`](../../configs/experimento.yaml). Sugestão da
[reunião de 01/10](../reunioes/2026-10-01.md).
