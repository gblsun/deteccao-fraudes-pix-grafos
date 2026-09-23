---
tags: [ideia]
---

# Detecção sob camuflagem adversarial

Volta para o [índice de ideias futuras](ideias-futuras.md).

## O problema

Todos os detectores desta pesquisa (Isolation Forest, DBSCAN, LOF) e os atributos de
grafo (OddBall, PageRank, comunidades) foram avaliados contra um simulador cujas
quadrilhas **não se adaptam** ao detector — geram padrões realistas, mas fixos (ver
[`src/pixfraud/simulation.py`](../../src/pixfraud/simulation.py) e as correções de
atalhos fáceis documentadas em [`docs/resultados.md`](../resultados.md)). Na prática, uma
quadrilha que soubesse como o banco detecta fraude ajustaria o comportamento para passar
despercebida: espalhar o valor por mais contas, imitar o tempo de permanência de uma
conta legítima, evitar o padrão de estrela que o OddBall pega.

## O que a literatura já mostra

[dou2020caregnn](../leituras/dou2020caregnn.md) (CARE-GNN, CIKM 2020) é a referência
central: mostra que detectores baseados em GNN perdem desempenho contra fraudadores que
camuflam o comportamento, e propõe um mecanismo de reforço para escolher vizinhos
confiáveis em vez de usar toda a vizinhança. O achado relevante mesmo para um contexto
não supervisionado: **camuflagem ataca justamente os atributos de vizinhança** — os
mesmos que esta pesquisa mostrou serem os mais importantes (a ablação de atributos em
`docs/resultados.md` já aponta o OddBall como o de maior efeito em todos os cenários, o
que o torna também o mais visado por um adversário informado).

## Como isso poderia ser avaliado aqui

Sem entrar em GNN, dá para testar a robustez adversarial com o que já existe:

1. Gerar um cenário novo em [`configs/cenarios.yaml`](../../configs/parametros-dos-experimentos.md)
   em que o gerador simula uma quadrilha "informada" — por exemplo, aumentando o número
   de intermediários (dilui o grau e a intermediação) ou variando o tempo de repasse para
   se aproximar da distribuição de contas legítimas (ataca o tempo de permanência).
2. Rodar a mesma bateria de `avaliar_cenarios.py` e `avaliar_atributos.py` nesse cenário e
   comparar a queda de average precision com os cenários atuais (fácil, base, difícil,
   realista) — um "cenário adversarial" a mais na tabela já existente.
3. Ver se a queda é maior nos atributos de grafo (estrutura, mais fácil de camuflar) do
   que nos temporais, ou o oposto — isso já seria um resultado publicável por si.

## Relação com o resto do projeto

Complementa a [ideia de GNN supervisionada](gnn-supervisionada.md): se um dia a pesquisa
migrar para GNN, o mecanismo do CARE-GNN (escolher vizinhos confiáveis) é a resposta
natural ao mesmo problema. Mas o ponto 1-3 acima não depende de GNN — é uma extensão
direta do que a pesquisa já faz.
