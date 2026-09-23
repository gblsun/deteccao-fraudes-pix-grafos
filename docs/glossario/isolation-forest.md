---
tags: [glossario]
---

# Isolation Forest

Detector de anomalia por **isolamento**: sorteia um atributo e um ponto de corte ao acaso,
repetidamente, montando uma árvore. Uma conta anômala fica isolada num galho curto, porque
está longe de todas as outras; o escore é o inverso do comprimento médio de isolamento em
muitas árvores (Liu, Ting e Zhou, 2008).

**Por que funciona sem supor formato de grupo.** Não precisa que as anomalias formem um
aglomerado nem estejam fora de um raio fixo — só precisa que sejam "fáceis de separar".

**No projeto.** [`anomaly.isolation_forest`](../../src/pixfraud/anomaly.py), 300 árvores.
Veja a comparação com os outros detectores em [modelos.md](../modelos.md).
