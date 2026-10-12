---
tags: [glossario]
---

# Teste de permutação

Responde "**o modelo é melhor que o acaso?**" sem supor nenhuma distribuição. Se o escore do
modelo não tivesse relação com a fraude, embaralhar o gabarito não mudaria a métrica. Então:

1. calcula a métrica com o gabarito verdadeiro (por exemplo, a
   [average precision](average-precision.md));
2. embaralha o gabarito muitas vezes (200 a 1 000) e recalcula a métrica a cada vez. Essa é a
   distribuição nula;
3. o p-valor é a fração das vezes em que a métrica embaralhada igualou ou superou a real:
   p = (b + 1) / (n + 1). O "+1" conta a própria observação, e por isso o p nunca é zero.

Na AP, a média da distribuição nula fica perto da **taxa de fraude**, que é a AP de um
ranking ao acaso.

**Parente próximo: o hipergeométrico no top-k.** Se o top-k fosse um sorteio de k contas, o
número de fraudes nele seguiria a distribuição hipergeométrica. Achar 35 fraudes nas 42 contas
mais suspeitas, quando só 2% das contas são fraude, tem probabilidade quase nula.

**No projeto.** [`stats.permutation_test_metric`](../../src/pixfraud/stats.py) e
`stats.topk_hypergeom`, usados por
[`avaliar_modelos.py`](../../scripts/03_modelos/avaliar_modelos.py) (`modelos_acaso.csv`).
A figura `testes_03_modelos.png` (ver
[`ilustrar_testes.py`](../../scripts/ferramentas/ilustrar_testes.py)) mostra a distribuição
nula e a AP observada. Ver também [testes para classificadores](testes-para-classificadores.md).
