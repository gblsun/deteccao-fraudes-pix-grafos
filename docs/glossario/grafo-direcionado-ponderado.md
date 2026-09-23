---
tags: [glossario]
---

# Grafo direcionado ponderado

Estrutura de vértices (contas) e arestas com sentido e peso (Pix, com o valor). Se A paga
B, a aresta vai de A para B; se B também paga A, é outra aresta, no sentido oposto.

**No projeto.** [`graph.build_graph`](../../src/pixfraud/graph.py) agrega todos os Pix de
um par (pagador, recebedor) numa única aresta, com `amount` (soma) e `count` (quantas
transferências). O grafo é a base de todos os [atributos de grafo](grau.md).

Veja também: [grau](grau.md), [caminho temporal](caminho-temporal.md).
