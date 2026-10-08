---
tags: [mapa]
---

# Ideias futuras

Direções de pesquisa que ainda não foram exploradas nesta iniciação científica — não são
tarefas do cronograma atual, e sim material para a seção "trabalhos futuros" do relatório
final ou para uma continuação da pesquisa. Cada nota descreve o que a ideia faria, como
se encaixaria no que já existe e o que falta para viabilizá-la.

Volta para o [índice da documentação](../mapa-da-pesquisa.md).

## Do autor da pesquisa

| Ideia | Em uma linha |
|-------|--------------|
| [IA agêntica para reconhecimento em tempo real](ia-agentica-tempo-real.md) | um agente com LLM como camada de explicação e triagem sobre o pipeline de detecção em tempo já existente, não em vez dele |

## Outras ideias

| Ideia | Em uma linha |
|-------|--------------|
| [GNN supervisionada como próximo passo](gnn-supervisionada.md) | aprender a representação da vizinhança em vez de atributos escolhidos à mão, com o TCC de Guerra como comparação direta |
| [Explicabilidade para auditoria](explicabilidade-para-auditoria.md) | SHAP/LIME por conta sinalizada, para justificar um bloqueio cautelar de verdade |
| [Detecção sob camuflagem adversarial](deteccao-adversarial.md) | o que acontece quando a quadrilha se adapta para escapar dos detectores, com o CARE-GNN como referência |
| [Detecção conformal com controle de alarmes falsos](deteccao-conformal-com-fdr.md) | um p-valor por conta a partir do escore de qualquer modelo e Benjamini-Hochberg para garantir "no máximo q% de alarmes falsos" |
| [Grafos heterogêneos e custo operacional](grafos-heterogeneos-e-custo-operacional.md) | identidades sintéticas (dispositivo, CPF) que o grafo conta-a-conta não vê, e avaliar por custo de investigação, não só por AP |

## Como acrescentar uma ideia

1. Nova nota em `docs/futuro/`, tag `ideia`, com um link de volta para esta.
2. Uma linha na tabela acima.
3. Se a ideia se apoiar numa leitura específica, linkar o fichamento em
   [`docs/leituras/`](../leituras/mapa-das-leituras.md) (crie a referência lá primeiro, se
   ainda não existir).
