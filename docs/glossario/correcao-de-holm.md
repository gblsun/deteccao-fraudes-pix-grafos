---
tags: [glossario]
---

# Correção de Holm

Ajuste para **muitos testes ao mesmo tempo**. Fazendo 10 comparações, a chance de pelo
menos um "achado" por acaso é grande. Holm ordena os p-valores e multiplica cada um pelo
número de testes que ainda restam:

$$p_{(i)}^{\text{ajustado}} = \max_{j \le i} \bigl[(m - j + 1)\, p_{(j)}\bigr]$$

É mais poderoso que Bonferroni e não exige independência entre os testes.

**No projeto.** Cada métrica é uma família de testes: a correção vale dentro dela
([`stats.holm_correction`](../../src/pixfraud/stats.py)). Coluna `p Wilcoxon (Holm)`.
