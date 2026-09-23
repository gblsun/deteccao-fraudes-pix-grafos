---
tags: [glossario]
---

# Caminho temporal

Num [grafo direcionado ponderado](grafo-direcionado-ponderado.md) agregado, "existe um
caminho de A até B" não garante que o dinheiro de A **possa ter chegado** a B: os Pix do
caminho precisam acontecer em **ordem crescente de tempo**. Um caminho temporal respeita
essa ordem.

**No projeto.** [`temporal.temporal_trail`](../../src/pixfraud/temporal.py) segue só os
Pix que acontecem depois do dinheiro chegar à conta anterior, com um limite opcional de
tempo parado em cada conta (`max_delay`). É a base do
[tempo de permanência](tempo-de-permanencia.md) e da avaliação de
[detecção a tempo](../resultados.md).
