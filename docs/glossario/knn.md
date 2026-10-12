---
tags: [glossario]
---

# KNN (k vizinhos mais próximos)

Olha para as $k$ contas mais parecidas com a conta $v$ (menor distância entre os
atributos, depois de `log1p` e padronização). Tem duas versões no projeto, e elas
respondem a perguntas diferentes:

- **Não supervisionada** (detector de anomalia): o escore é a distância média até as $k$
  vizinhas. Quanto mais longe até as contas mais parecidas, mais anômala.

$$\text{escore}(v) = \frac{1}{k}\sum_{u \in N_k(v)} \lVert x_v - x_u \rVert$$

- **Supervisionada** (classificador): a probabilidade de fraude é a fração de fraudes
  entre as $k$ vizinhas, pesadas pela distância. Precisa dos rótulos, então entra ao lado
  da [Random Forest](random-forest.md) como teto, em
  [validação cruzada](validacao-cruzada.md).

**Diferença para o DBSCAN.** O [DBSCAN](dbscan-e-k-distance.md) usa só a distância à
$k$-ésima vizinha; a média de todas as $k$ é menos sensível a uma única vizinha
coincidente.

**Como comparar com os outros.** As duas versões dão um escore por conta, então entram nas
mesmas métricas de ranking ([average precision](average-precision.md),
[precision@k](precision-at-k.md), [ROC-AUC](roc-auc.md)) e nas mesmas contas de
`scripts/03_modelos/avaliar_modelos.py`. A supervisionada só não é comparável "de igual para
igual": ela viu rótulos que um banco raramente tem.

**No projeto.** [`anomaly.knn`](../../src/pixfraud/anomaly.py) e
`experiment.supervised_scores(model="knn_supervisionado")`
([experiment.py](../../src/pixfraud/experiment.py)). Sugestão da
[reunião de 01/10](../reunioes/2026-10-01.md).
