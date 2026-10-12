---
tags: [glossario]
---

# Teste de Dunn

O [Kruskal-Wallis](kruskal-wallis.md) diz se **algum** grupo difere dos outros, mas não diz
qual. O teste de Dunn (1964) responde isso, par a par, depois de um Kruskal-Wallis
significativo.

Ele reaproveita a mesma ordenação de todas as observações. Para cada par de grupos (a, b),
compara os postos médios:

$$z = \frac{\bar R_a - \bar R_b}{\sqrt{\left(\frac{n(n+1)}{12} - C\right)\left(\frac{1}{n_a} + \frac{1}{n_b}\right)}}$$

em que C corrige os empates. Como são muitos pares (15, com 6 papéis), os p-valores são
ajustados pela [correção de Holm](correcao-de-holm.md).

**Exemplo.** Se o tempo de permanência difere entre os papéis (Kruskal-Wallis significativo), o
Dunn diz, por exemplo, se laranja e intermediário diferem das contas normais e se diferem entre
si. Os números de cada cenário ficam em `inferencia_dunn.csv`.

**No projeto.** [`stats.dunn_posthoc`](../../src/pixfraud/stats.py), usado por
[`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py)
(`inferencia_dunn.csv`) e por
[`investigar_falsos_positivos.py`](../../scripts/05_interpretacao/investigar_falsos_positivos.py)
(que papéis o escore de risco separa).
