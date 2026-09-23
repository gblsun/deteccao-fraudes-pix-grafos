---
tags: [glossario]
---

# Intervalo de confiança (IC 95%)

Faixa que, se o experimento fosse repetido muitas vezes, conteria o valor verdadeiro em
95% das vezes. Nos resumos por sementes usamos o IC t de Student:

$$\bar{x} \pm t_{0{,}975,\, n-1} \cdot \frac{s}{\sqrt{n}}$$

**Como ler nos resultados.** "AP 0,50 [0,45; 0,55]" quer dizer que, repetindo o
experimento com outras sementes, esperamos algo nessa faixa. Se os ICs de duas abordagens
se sobrepõem, a diferença **não** é automaticamente desprezível: o teste correto é o
[pareado](teste-de-wilcoxon-pareado.md), porque as duas viram os mesmos datasets.

**No projeto.** [`stats.summarize_runs`](../../src/pixfraud/stats.py); colunas
`ic_inferior` e `ic_superior`.
