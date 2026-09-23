---
tags: [glossario]
---

# Propagação de risco (culpa por associação)

[PageRank](pagerank.md) **personalizado**: em vez de distribuir a "moeda" igualmente entre
todas as contas, ela sempre volta para um conjunto de contas-semente (fraudes já
conhecidas). O escore de cada conta mede o quão perto — e por quantos caminhos — ela está
das sementes.

**Direção.** `forward` segue o dinheiro adiante; `backward` volta à origem; `both` ignora
o sentido, o que alcança laranjas "irmãs" que repassam para o mesmo intermediário, mesmo
sem ligação direta com a semente.

**No projeto.** [`flow.propagate_risk`](../../src/pixfraud/flow.py). Combinado com um
detector (média dos percentis), levou a average precision de 0,46 para 0,95 no cenário
mais difícil, com 25% das fraudes conhecidas. É o único modelo do projeto que usa rótulos
parciais — os que um banco já tem, pelo [MED](med.md).
