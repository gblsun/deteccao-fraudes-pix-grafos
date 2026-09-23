---
tags: [glossario]
---

# PageRank (ponderado pelo valor)

Centralidade por "voto por chegada": cada conta distribui sua importância entre quem
recebeu dela, e a importância de uma conta é a soma do que recebeu de suas conectadas,
recursivamente. No projeto, cada Pix "vota" proporcionalmente ao valor.

$$\text{PR}(v) = \frac{1-\alpha}{N} + \alpha \sum_{u \to v} \text{PR}(u) \cdot \frac{\text{amount}(u,v)}{\sum_w \text{amount}(u,w)}$$

**No projeto.** [`features.graph_features`](../../src/pixfraud/features.py) usa
`nx.pagerank(graph, weight="amount")`. É o atributo com maior efeito isolado em
laranjas e coletoras ($\delta \approx 0{,}74$ a $0{,}97$), porque elas recebem valores
grandes e concentrados — mas a mesma versão personalizada, partindo de fraudes já
conhecidas, também é a base da [propagação de risco](propagacao-de-risco.md). Na
[ablação](../resultados.md), tirar o PageRank **melhora** o DBSCAN (até 0,15 de AP): ele
tem cauda muito pesada e distorce as distâncias do detector.
