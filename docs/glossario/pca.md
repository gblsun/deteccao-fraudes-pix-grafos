---
tags: [glossario]
---

# PCA (análise de componentes principais)

Encontra as direções em que as contas mais variam. São combinações de atributos que andam
juntos, como [grau](grau.md) de entrada e volume recebido. Com poucas direções (os
componentes principais), dá para resumir a maior parte da variação.

**Como detector de anomalia.** Reconstrói cada conta usando só os componentes que
explicam 90% da variância. O escore é o que sobra:

$$\text{escore}(v) = \frac{1}{d}\lVert x_v - \hat{x}_v \rVert^2$$

Uma conta típica é bem resumida e tem erro baixo. Uma conta que quebra a relação usual
entre os atributos tem erro alto, mesmo sem ser extrema em nenhum deles. Um exemplo é
receber de muita gente e não pagar ninguém.

**Cuidado.** Uma conta extrema **ao longo** da direção principal (muito grande em tudo ao
mesmo tempo) é bem reconstruída e passa despercebida. É o oposto do
[Isolation Forest](isolation-forest.md), que acha justamente essas.

É o "autoencoder linear": sem treino iterativo e sem semente. O autoencoder de
`anomaly.autoencoder` é a versão não linear.

**No projeto.** [`anomaly.pca`](../../src/pixfraud/anomaly.py). Sugestão da
[reunião de 01/10](../reunioes/2026-10-01.md).
