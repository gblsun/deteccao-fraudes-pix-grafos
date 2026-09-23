---
tags: [mapa]
---

# Mapa das leituras

Uma nota por leitura, com o nome igual à chave do
[`referencias.bib`](../referencias.bib). Cada nota aponta para o tema, para onde a
leitura entra no projeto e para as leituras vizinhas: é isso que forma o grafo do
cofre (ver [obsidian](../obsidian.md)).

Volta para o [índice da documentação](../mapa-da-pesquisa.md) e para a
[revisão bibliográfica](../revisao-bibliografica.md).

## Grafos e redes

A base teórica: como modelar transações como grafo e que métricas extrair.

| Leitura | Em uma linha | Entra em |
|---------|--------------|----------|
| [diestel2017graph](diestel2017graph.md) | Livro-texto de teoria dos grafos: definições e resultados usados na modelagem | [graph.py](../../src/pixfraud/graph.py), [estudo 01](../../estudos/01_fundamentos.ipynb) |
| [easley2010networks](easley2010networks.md) | Redes, mercados e comportamento: centralidade, comunidades e mundo pequeno | [estudo 03](../../estudos/03_metricas_de_centralidade.ipynb), [estudo 05](../../estudos/05_modelos_de_redes.ipynb) |
| [brandes2001faster](brandes2001faster.md) | Algoritmo de intermediação usado (em versão amostrada) nos atributos de grafo | [features.py](../../src/pixfraud/features.py) |
| [hagberg2008networkx](hagberg2008networkx.md) | A biblioteca NetworkX, usada para montar e medir os grafos | [graph.py](../../src/pixfraud/graph.py), [algorithms.py](../../src/pixfraud/algorithms.py) |

## Detecção de anomalias em grafos

Como a fraude aparece na estrutura da rede.

| Leitura | Em uma linha | Entra em |
|---------|--------------|----------|
| [akoglu2015graph](akoglu2015graph.md) | Survey de detecção de anomalias em grafos; origem do OddBall e da culpa por associação | [communities.py](../../src/pixfraud/communities.py), [flow.py](../../src/pixfraud/flow.py), [resultados](../resultados.md) |
| [weber2019aml](weber2019aml.md) | Elliptic (Bitcoin): compara atributos tabulares e de grafo, a mesma pergunta desta pesquisa | [resultados](../resultados.md) |

## Aprendizado de máquina e avaliação

Os detectores usados e como medir o desempenho com classes raras.

| Leitura | Em uma linha | Entra em |
|---------|--------------|----------|
| [liu2008isolation](liu2008isolation.md) | Isolation Forest: isola pontos raros com partições aleatórias | [anomaly.py](../../src/pixfraud/anomaly.py) |
| [ester1996dbscan](ester1996dbscan.md) | DBSCAN: densidade e ruído; o ruído é o que tratamos como anomalia | [anomaly.py](../../src/pixfraud/anomaly.py), [escolha do eps](../../notebooks/01_analise_exploratoria.ipynb) |
| [pedregosa2011sklearn](pedregosa2011sklearn.md) | scikit-learn: implementação dos detectores e da validação cruzada | [anomaly.py](../../src/pixfraud/anomaly.py), [experiment.py](../../src/pixfraud/experiment.py) |
| [james2021isl](james2021isl.md) | Introdução ao aprendizado estatístico: validação e comparação de modelos | [teto supervisionado](../resultados.md) |
| [bishop2006pattern](bishop2006pattern.md) | Fundamentos de reconhecimento de padrões e modelos probabilísticos | [anomaly.py](../../src/pixfraud/anomaly.py) |
| [witten2011datamining](witten2011datamining.md) | Prática de mineração de dados; avaliação com classes desbalanceadas | [evaluation.py](../../src/pixfraud/evaluation.py), [resultados](../resultados.md) |

## Dados: Pix e datasets públicos

De onde vêm os números e com que dados o método é testado.

| Leitura | Em uma linha | Entra em |
|---------|--------------|----------|
| [bcb2024pix](bcb2024pix.md) | O arranjo Pix: regras, MED e bloqueio cautelar | [bcb.py](../../src/pixfraud/bcb.py), [proposta](../proposta.md) |
| [bcb2024relatorio](bcb2024relatorio.md) | Relatório de gestão do Pix: números oficiais de uso e de fraude | [notebook 01](../../notebooks/01_analise_exploratoria.ipynb) |
| [bcb2026dadosabertos](bcb2026dadosabertos.md) | API de dados abertos do Pix: estatísticas de transações e de fraudes | [bcb.py](../../src/pixfraud/bcb.py), [notebook 01](../../notebooks/01_analise_exploratoria.ipynb), [dados](../../data/README.md) |
| [lopezrojas2016paysim](lopezrojas2016paysim.md) | PaySim: simulador de dinheiro móvel, referência para gerar dados sintéticos | [simulation.py](../../src/pixfraud/simulation.py), [external.py](../../src/pixfraud/external.py) |
| [altman2023realistic](altman2023realistic.md) | AMLworld: transações sintéticas de lavagem com tipologias em grafo | [external.py](../../src/pixfraud/external.py), [resultados, seção 8](../resultados.md) |

## Trabalhos relacionados: fraude com redes neurais em grafos

Pesquisas recentes sobre o mesmo problema com GNN (grafos neurais). Servem de comparação
com a abordagem não supervisionada adotada aqui e de base para
[ideias futuras](../futuro/ideias-futuras.md).

| Leitura | Em uma linha | Entra em |
|---------|--------------|----------|
| [guerra2025gnnfraude](guerra2025gnnfraude.md) | TCC (ICMC-USP, 2025): mesmo problema desta pesquisa, com GNN supervisionada | [GNN supervisionada](../futuro/gnn-supervisionada.md) |
| [dou2020caregnn](dou2020caregnn.md) | CARE-GNN (CIKM 2020): detector de GNN que se adapta a fraudadores camuflados | [detecção adversarial](../futuro/deteccao-adversarial.md) |
| [motie2024gnnreview](motie2024gnnreview.md) | Revisão sistemática de GNN para fraude financeira (Expert Systems with Applications, 2024) | [GNN supervisionada](../futuro/gnn-supervisionada.md) |
| [dellagarza2023aml](dellagarza2023aml.md) | Trabalho brasileiro (SBSI 2023): GCN, Skip-GCN e NENN para lavagem de dinheiro | [resultados](../resultados.md) |

## Como acrescentar uma leitura

1. Acrescente a referência ao [`referencias.bib`](../referencias.bib).
2. Crie `docs/leituras/<chave>.md` a partir do
   [modelo de fichamento](../modelos/fichamento.md), com os mesmos campos do topo
   (referência, tema, onde entra, leituras vizinhas).
3. Acrescente a linha na tabela do tema, aqui e na
   [revisão bibliográfica](../revisao-bibliografica.md).
