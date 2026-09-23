---
tags: [glossario]
---

# Intermediação (betweenness centrality)

Fração dos caminhos mais curtos entre pares de contas que passam por uma conta. Mede o
quanto ela é uma "ponte" na rede.

$$C_B(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

onde $\sigma_{st}$ é o número de caminhos mais curtos de $s$ a $t$, e $\sigma_{st}(v)$
quantos passam por $v$.

**Custo.** Exata, é $O(nm)$; o projeto usa a aproximação de Brandes (2001), amostrando
`betweenness_k` vértices de origem (padrão: 500) em vez de todos.

**No projeto.** [`features.graph_features`](../../src/pixfraud/features.py). Efeito
menor que outros atributos de grafo (em torno de $-0{,}3$ a $-0{,}4$ nos cenários base) e
some quase totalmente com pessoas inativas na rede.
