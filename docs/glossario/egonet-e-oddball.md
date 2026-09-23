---
tags: [glossario]
---

# Egonet e OddBall

A **egonet** de uma conta é ela, seus vizinhos diretos e as arestas entre eles. Em redes
reais, o nº de arestas $E$ e o valor movimentado $W$ na egonet seguem leis de potência em
função do nº de vizinhos $N$: $E \propto N^\alpha$, $W \propto E^\beta$. O **OddBall**
(Akoglu, McGlohon e Faloutsos, 2010) mede o quanto uma conta foge dessas leis:

$$\text{escore} = \frac{\max(y, \hat y)}{\min(y, \hat y)} \cdot \log(|y - \hat y| + 1)$$

comparando o valor observado $y$ com o esperado $\hat y$ pela lei ajustada.

* `oddball_en`: vizinhança em **estrela** (vizinhos que não se conhecem, como as vítimas
  de uma laranja) ou quase-clique;
* `oddball_ew`: **dinheiro demais** para o tamanho da vizinhança.

**No projeto.** [`communities.oddball_scores`](../../src/pixfraud/communities.py). O
`oddball_ew` tem o maior efeito isolado de todos os atributos em todos os cenários
($\delta \ge 0{,}90$).
