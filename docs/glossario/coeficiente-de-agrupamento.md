---
tags: [glossario]
---

# Coeficiente de agrupamento (clustering)

Fração dos pares de vizinhos de uma conta que também são ligados entre si — "os amigos dos
meus amigos são meus amigos?".

$$C(v) = \frac{2\, \triangle(v)}{k_v (k_v - 1)}$$

onde $\triangle(v)$ é o nº de triângulos por $v$ e $k_v$ o grau (versão não direcionada).

**Como ler.** Baixo = vizinhança em estrela: os vizinhos de $v$ não se conhecem entre si.
É exatamente o formato de uma laranja recebendo de vítimas desconhecidas umas das outras.

**No projeto.** [`features.graph_features`](../../src/pixfraud/features.py); o atributo
de maior efeito **negativo** em todos os cenários ($\delta \approx -0{,}9$ a $-0{,}98$).

Veja também: [egonet e OddBall](egonet-e-oddball.md).
