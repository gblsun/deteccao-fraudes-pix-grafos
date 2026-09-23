---
tags: [glossario]
---

# Classes raras (desbalanceamento)

Quando a classe de interesse é muito menor que a outra — no Pix real, cerca de **5
contestações aceitas a cada 100 mil** transações.

**Consequências práticas:**

* a acurácia é inútil: dizer "nenhuma fraude" acerta 99,99%;
* a [ROC-AUC](roc-auc.md) fica otimista;
* a [average precision](average-precision.md) e a [precision@k](precision-at-k.md) são as
  métricas adequadas, e precisam sempre ser lidas contra a taxa de fraude (o valor do
  acaso).

**No projeto.** O gerador usa uma taxa muito acima da real (~530 golpes a cada 100 mil
Pix) para haver exemplos suficientes; o cenário `realista` reduz isso 3 vezes. A
comparação com os números do Banco Central está no
[notebook 01](../../notebooks/01_analise_exploratoria.ipynb).
