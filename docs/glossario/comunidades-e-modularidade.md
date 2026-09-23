---
tags: [glossario]
---

# Comunidades e modularidade (Louvain)

Encontrar grupos de contas mais conectadas entre si do que com o resto da rede,
maximizando a **modularidade**:

$$Q = \frac{1}{2m}\sum_{ij}\Bigl(A_{ij} - \frac{k_i k_j}{2m}\Bigr)\,\delta(c_i, c_j)$$

O algoritmo de Louvain otimiza $Q$ de forma gulosa e hierárquica, agrupando vértices e
depois agrupando os grupos.

**No projeto.** [`communities.detect_communities`](../../src/pixfraud/communities.py)
(`method="louvain"`, padrão) usa `nx.community.louvain_communities`. As comunidades
alimentam o [coeficiente de participação](coeficiente-de-participacao.md) e coloriram o
[explorador da rede](../../app/guia-do-explorador.md).
