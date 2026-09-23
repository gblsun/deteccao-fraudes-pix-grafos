---
tags: [glossario]
---

# DBSCAN e k-distance

**DBSCAN**: agrupa pontos em regiões densas. Uma conta é **núcleo** se tem pelo menos
`min_samples` vizinhos dentro do raio `eps`; quem não é núcleo nem está perto de um é
**ruído** — a nossa anomalia (Ester et al., 1996).

**k-distance**: a distância de uma conta ao seu `min_samples`-ésimo vizinho mais próximo.
É exatamente o que decide se ela é núcleo (núcleo $\iff$ k-distance $\le$ `eps`), então
usamos essa distância como **escore contínuo**, já que o DBSCAN só dá rótulos.

**Memória.** Com `eps` no quantil 95%, cada conta tem ~20% das outras como vizinhas: o
DBSCAN guarda essa lista por conta, e a memória cresce com o **quadrado** do número de
contas (~16 GB com 100 mil contas). Acima de `modelos.dbscan.max_exact`, o rótulo vira uma
aproximação ("k-distance > eps") que não muda o escore nem a average precision.

**No projeto.** [`anomaly.dbscan`](../../src/pixfraud/anomaly.py). Ver também
[`configs/parametros-dos-experimentos.md`](../../configs/parametros-dos-experimentos.md).
