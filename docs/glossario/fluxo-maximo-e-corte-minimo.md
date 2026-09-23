---
tags: [glossario]
---

# Fluxo máximo e corte mínimo

**Fluxo máximo**: o maior valor que pode passar de uma origem a um destino, respeitando a
capacidade de cada aresta (aqui, o valor de cada Pix). **Corte mínimo**: o menor conjunto
de arestas cuja remoção desconecta a origem do destino — e, pelo teorema de Ford-Fulkerson,
seu valor é **igual** ao do fluxo máximo.

**Por que interessa.** O corte mínimo é literalmente "que Pix bloquear para impedir que o
dinheiro chegue lá": as contas desse corte são as melhores candidatas a bloqueio cautelar.

**No projeto.** [`flow.max_money_flow`](../../src/pixfraud/flow.py) e
[`flow.blocking_cut`](../../src/pixfraud/flow.py), usando `nx.maximum_flow`; exposto em
`scripts/criar_grafo.py fluxo` e na aba "Fluxo e bloqueio" do
[explorador](../../app/guia-do-explorador.md).
