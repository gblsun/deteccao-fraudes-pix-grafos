---
tags: [glossario]
---

# Random Forest (como teto supervisionado)

Conjunto de árvores de decisão treinadas em amostras (e atributos) diferentes, cuja
votação dá a previsão final. Ao contrário dos outros modelos do projeto, **usa os
rótulos** de fraude durante o treino.

**Papel no projeto.** Não é um detector da pesquisa (que é não supervisionada por
desenho): serve de **teto de referência**, avaliado com
[validação cruzada](validacao-cruzada.md) estratificada de 5 partes, para medir o quanto
se perde por não ter rótulos. Chega a AP 0,99, contra 0,53 do melhor detector não
supervisionado no mesmo cenário.

**No projeto.** [`experiment.supervised_scores`](../../src/pixfraud/experiment.py).
