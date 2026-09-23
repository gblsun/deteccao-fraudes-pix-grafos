---
tags: [glossario]
---

# Teste de Mann-Whitney

Teste não paramétrico que compara dois grupos pela **ordem** dos valores, sem supor
distribuição normal. A estatística $U$ conta quantos pares (a, b) têm $a > b$.

**Por que aqui.** Os atributos das contas têm cauda muito pesada (valores, graus,
PageRank), então a média e o desvio enganam. O teste de Mann-Whitney não depende disso.

**Cuidado.** Com milhares de contas, diferenças minúsculas dão p-valores minúsculos. Por
isso sempre acompanhamos do [delta de Cliff](delta-de-cliff.md), que mede o tamanho do
efeito, e da [correção de Holm](correcao-de-holm.md), que ajusta os vários testes.

**No projeto.** [`stats.compare_groups`](../../src/pixfraud/stats.py).
