---
tags: [glossario]
---

# Validação cruzada estratificada

Divide as contas em $k$ partes (aqui, 5), treina em $k-1$ e prevê na que ficou de fora,
repetindo até toda conta ter sido prevista por um modelo que **não a viu**.
"Estratificada" = cada parte mantém a proporção de fraudes.

**Por que importa.** Sem isso, um modelo supervisionado decoraria as contas de treino e o
desempenho pareceria perfeito.

**No projeto.** Usada só no [Random Forest](random-forest.md) que serve de **teto**
comparativo ([`experiment.supervised_scores`](../../src/pixfraud/experiment.py)); os
detectores da pesquisa não usam rótulos.
