---
tags: [glossario]
---

# Precision@k

Das $k$ contas mais suspeitas, que fração é realmente fraude.

$$\text{precision@}k = \frac{\text{fraudes entre as } k \text{ primeiras}}{k}$$

**Como ler.** Responde à pergunta prática do analista: "se eu revisar 40 contas hoje,
quantas serão fraude?". No projeto, $k$ é sempre o **número de fraudes reais** do dataset,
o que torna a métrica comparável entre cenários.

**No projeto.** Sai junto com a [average precision](average-precision.md) em
[`evaluation.evaluate`](../../src/pixfraud/evaluation.py) e é a métrica usada na avaliação
por tipologia no AMLworld ([`recall_by_group`](../../src/pixfraud/evaluation.py)).
