---
tags: [ideia]
---

# Explicabilidade para auditoria

Volta para o [índice de ideias futuras](ideias-futuras.md).

## O que existe hoje

Cada conta suspeita já tem uma explicação visual: o heatmap de risco
(`heatmap_risco_<modelo>_<atributos>.png`, gerado por
[`rodar_experimento.py`](../../scripts/mapa-dos-scripts.md), ver
[Figura 11](../../reports/mapa-dos-resultados.md)) mostra quais atributos mais pesaram
para aquela conta específica. É uma explicação **visual**, útil para quem já entende os
atributos.

## O que falta

Um banco que bloqueia uma conta pelo MED precisa justificar a decisão, conta a conta, de
um jeito que sirva de registro — não só um gráfico, mas uma frase auditável: "esta conta
foi sinalizada porque recebeu de 6 contas que nunca se conectaram entre si (padrão de
estrela) e repassou 95% do valor em menos de 1 hora". Isso é o papel de métodos de
explicabilidade por instância:

- **SHAP** (Shapley values): decompõe o escore de uma conta na contribuição de cada
  atributo, com uma base teórica de teoria dos jogos — provavelmente a escolha mais
  direta, porque já existe implementação madura (`shap`) que funciona sobre Isolation
  Forest e Random Forest sem mudar o modelo.
- **LIME**: aproxima o modelo localmente por um modelo simples (interpretável) ao redor
  de cada instância; mais barato, explicação um pouco menos estável.

## Onde entraria no código

Uma função em `pixfraud.explain` (novo módulo) que recebe o modelo já treinado
(`anomaly.DETECTORS`) e a matriz de atributos preparada
(`anomaly.prepare_matrix`), e devolve, por conta, a contribuição de cada atributo — em
vez de só o heatmap agregado por execução, uma explicação individual, exportável para
texto. Encaixaria bem depois de `checkpoint_flags` em
[`pixfraud.online`](../../src/pixfraud/online.py): a explicação corre só nas contas já
sinalizadas em cada corte, o mesmo ponto onde a
[ideia de agente de IA em tempo real](ia-agentica-tempo-real.md) entraria para verbalizar
o resultado.

## Por que importa para esta pesquisa especificamente

A proposta já defende a detecção não supervisionada em parte **porque** é mais
interpretável que uma caixa-preta (ver [`docs/modelos.md`](../modelos.md), "não
supervisionado... interpretável"). SHAP/LIME levam essa vantagem até o fim: hoje a
interpretabilidade é por execução (o heatmap agregado); com explicabilidade por
instância, vira por conta, que é o nível em que uma decisão real de bloqueio é tomada.
