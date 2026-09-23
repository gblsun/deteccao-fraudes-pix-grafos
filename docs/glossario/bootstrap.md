---
tags: [glossario]
---

# Bootstrap

Estimar a incerteza reamostrando os próprios dados, com reposição, muitas vezes. O
intervalo de confiança sai dos quantis das réplicas (método percentil).

**Estratificado.** Reamostramos separadamente fraudes e contas normais, para toda réplica
manter a mesma taxa de fraude do dado original — sem isso, réplicas sem nenhuma fraude
tornariam a métrica indefinida.

**No projeto.** [`stats.bootstrap_metric`](../../src/pixfraud/stats.py), usado para
colocar intervalo de confiança numa métrica de um único dataset (quando não há sementes
repetidas).

Veja também: [intervalo de confiança](intervalo-de-confianca.md).
