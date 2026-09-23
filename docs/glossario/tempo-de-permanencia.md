---
tags: [glossario]
---

# Tempo de permanência (dwell time)

Quanto tempo o dinheiro fica parado na conta: para cada Pix recebido, o tempo até o
próximo Pix enviado; o atributo é a **mediana** dessas esperas.

**Por que separa tão bem.** Uma pessoa comum leva horas ou dias para repassar; uma
[conta laranja](conta-laranja.md), minutos. É o atributo com maior efeito isolado nas
laranjas ($\delta = -1{,}00$) e o que mais faz falta quando é removido (a AP cai até
0,11 na ablação).

**Cuidado.** O gerador supõe repasse em ~30 min. O cenário `repasse_lento` testa o que
acontece quando as laranjas esperam ~6 h: o atributo continua separando, mas o desempenho
cai.

**No projeto.** [`temporal.dwell_time`](../../src/pixfraud/temporal.py).
