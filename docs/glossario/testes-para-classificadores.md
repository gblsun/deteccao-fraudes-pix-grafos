---
tags: [glossario]
---

# Testes de hipótese para classificadores

Nenhum teste de hipótese *classifica* contas. O que eles fazem é **verificar** uma
classificação: se o modelo é melhor que o acaso, se um modelo é melhor que outro, ou se uma
conta específica é estranha demais para ser normal ([detecção conformal](deteccao-conformal.md)).

## O modelo é melhor que o acaso?

| Teste | Pergunta | Hipótese nula |
|---|---|---|
| Permutação da AP | a [average precision](average-precision.md) do modelo poderia sair por sorte? | o escore não tem relação com a fraude: embaralhar o gabarito não muda a AP |
| Binomial ou hipergeométrico no top-k | achar 35 fraudes nas 42 contas mais suspeitas é sorte, se só 2% são fraude? | o top-k é um sorteio das contas |
| Fisher exato (ou qui-quadrado) | a marcação do modelo tem associação com a fraude? | na tabela 2×2 marcada × fraude, as duas coisas são independentes |

O [teste de permutação](teste-de-permutacao.md) é o mais geral (`stats.permutation_test_metric`; o
hipergeométrico é `stats.topk_hypergeom`; os dois estão em `modelos_acaso.csv`): embaralha o gabarito milhares de vezes, recalcula a
métrica e conta em quantas vezes ela igualou ou superou a real. Vale para qualquer métrica.

## Um modelo é melhor que outro?

| Teste | Quando usar |
|---|---|
| DeLong | duas [ROC-AUC](roc-auc.md) nas mesmas contas |
| McNemar | dois classificadores binários nas mesmas contas: compara só onde eles discordam |
| [Wilcoxon pareado](teste-de-wilcoxon-pareado.md) entre sementes, com [Holm](correcao-de-holm.md) e [bootstrap](bootstrap.md) | a mesma comparação repetida em várias redes; é o que o projeto usa (`stats.compare_runs`, em `avaliar_modelos.py`) |
| [Friedman + Nemenyi](friedman-e-nemenyi.md) | todos os modelos de uma vez, nas mesmas sementes: algum difere? quais? (`stats.friedman_models`, em `avaliar_modelos.py`) |

## "É comércio ou não?"

O tipo de conta já é conhecido (`account_type` = PJ), então não precisa ser adivinhado. A
pergunta útil é se **o modelo confunde comércio com fraude**: um Fisher exato entre "marcada
como suspeita" e "é comércio", só nas contas legítimas. Se der significativo, o modelo gera
alarmes falsos em comércios e os atributos merecem ajuste. No projeto, esse Fisher está em
[`investigar_falsos_positivos.py`](../../scripts/05_interpretacao/investigar_falsos_positivos.py)
(`falsos_positivos_testes.csv`).

**Cuidado.** Um p-valor pequeno diz que o efeito existe, não que ele importa: reporte
sempre o tamanho (a diferença de AP e o [IC 95%](intervalo-de-confianca.md)). Ver também o
[teste de Kruskal-Wallis](kruskal-wallis.md), que compara grupos, não classifica.
