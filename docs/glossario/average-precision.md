---
tags: [glossario]
---

# Average precision (AP)

Média da precisão obtida a cada acerto, percorrendo as contas da mais suspeita para a
menos suspeita. Resume a curva precisão × revocação num número só.

$$\text{AP} = \sum_{k} \bigl(R_k - R_{k-1}\bigr)\, P_k$$

onde $P_k$ e $R_k$ são a precisão e a revocação quando olhamos as $k$ contas mais
suspeitas.

**Como ler.** Um detector que ordena as contas ao acaso tem AP igual à **taxa de fraude**
(0,019 no cenário base; 0,006 no `realista`). Então AP 0,5 com 2% de fraude é ~26 vezes o
acaso, e não "metade do ideal".

**No projeto.** É a métrica principal de todas as comparações, porque só depende da
**ordem** das contas, e não de um limiar. Calculada em
[`evaluation.evaluate`](../../src/pixfraud/evaluation.py); aparece em todos os arquivos de
[`reports/results/`](../../reports/README.md).

Veja também: [precision@k](precision-at-k.md), [ROC-AUC](roc-auc.md),
[classes raras](classes-raras.md).
