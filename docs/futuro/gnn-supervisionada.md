---
tags: [ideia]
---

# GNN supervisionada como próximo passo

Volta para o [índice de ideias futuras](ideias-futuras.md).

Já citada de passagem em [`docs/modelos.md`](../modelos.md#outros-modelos-que-caberiam-nesta-pesquisa)
("é o passo natural depois de mostrar que os atributos de grafo ajudam, mas exige rótulos
e muda o caráter da pesquisa"). Esta nota aprofunda o porquê e o como.

## Por que faz sentido depois desta pesquisa, não antes

A pesquisa mostra, de forma não supervisionada, que atributos de grafo (PageRank,
intermediação, coeficiente de participação, OddBall) ajudam a separar fraude de
comportamento normal (ver [`docs/resultados.md`](../resultados.md)). Uma GNN
supervisionada é a forma natural de ir além: em vez de atributos escolhidos à mão, a rede
aprende a própria representação da vizinhança. Isso só compensa **depois** de já saber
que a estrutura da rede importa — do contrário, seria trocar um problema não resolvido
(quais atributos usar) por outro (qual arquitetura de GNN usar), sem saber se a estrutura
ajuda mesmo.

## Comparação direta: o TCC de Guerra

[guerra2025gnnfraude](../leituras/guerra2025gnnfraude.md) ataca o mesmo problema (fraude
em transações financeiras, grafo de contas) com uma GNN supervisionada. É a comparação
mais próxima disponível: mesma origem (ICMC-USP), tema quase idêntico, mas caminho
metodológico diferente (supervisionado vs. não supervisionado). Vale a leitura completa
antes de decidir a arquitetura.
[motie2024gnnreview](../leituras/motie2024gnnreview.md) dá o panorama mais amplo do que
já foi tentado (GCN, GraphSAGE, GAT, arquiteturas heterogêneas).

## O que mudaria no código

- Novo módulo (`pixfraud.gnn` ou similar), fora do ciclo `anomaly.py` → `DETECTORS`, já
  que uma GNN supervisionada precisa de treino com validação cruzada, não só de
  `fit_predict`.
- Split de treino/teste que **não vaze** informação de grafo entre as duas partes (uma
  conta do teste não pode ter uma aresta vista no treino sem cuidado) — é o erro mais
  comum apontado na literatura de GNN para fraude.
- Entra na mesma comparação de `docs/modelos.md` §7 (Random Forest como teto), como um
  segundo teto: agora não só "que distância há entre não supervisionado e supervisionado
  com atributos tabulares", mas também "e com a estrutura aprendida direto do grafo".

## Custo

Alto: precisa de PyTorch Geometric (ou DGL), GPU para treinar em tempo razoável, e mais
cuidado experimental do que os detectores atuais. Por isso a sugestão em
`docs/modelos.md` é deixar como trabalho futuro do relatório, não como próximo
experimento imediato.
