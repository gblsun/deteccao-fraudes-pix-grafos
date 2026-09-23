---
tags: [mapa]
---

# Revisão bibliográfica

Índice das leituras. Cada leitura tem o seu fichamento em `docs/leituras/<chave-bibtex>.md`,
com o nome igual à chave do [`referencias.bib`](referencias.bib), o que facilita citar depois
no relatório.

## Como fichar uma leitura

1. Acrescente a referência ao `referencias.bib` (o Zotero com Better BibTeX exporta pronto).
2. Crie `docs/leituras/<chave-bibtex>.md` a partir do modelo
   [`docs/modelos/fichamento.md`](modelos/fichamento.md). No Obsidian: nova nota na pasta
   `leituras` com a chave como nome e depois *Inserir modelo* (ver [obsidian.md](obsidian.md)).
3. Acrescente uma linha na tabela "Fichamentos" abaixo.

## Sugestões de leitura

Não constam na proposta original, mas são próximas do tema. Todas já estão no
`referencias.bib`.

| Chave                  | Por que ler                                                                          |
|------------------------|---------------------------------------------------------------------------------------|
| `akoglu2015graph`      | Survey clássico de detecção de anomalias em grafos: dá o mapa do estado da arte        |
| `lopezrojas2016paysim` | Simulador de transações de dinheiro móvel para fraude: referência para dataset sintético |
| `altman2023realistic`  | Dataset sintético de lavagem de dinheiro (AMLworld) com padrões em grafo (fan-in, fan-out, ciclos, cadeias) |
| `weber2019aml`         | Dataset Elliptic: grafo de transações Bitcoin rotulado, com comparação entre atributos tabulares e de grafo |
| `brandes2001faster`    | Algoritmo usado pelo NetworkX para calcular a intermediação (*betweenness*)            |
| `guerra2025gnnfraude`  | TCC (ICMC-USP, 2025): mesmo problema desta pesquisa, com GNN supervisionada            |
| `dou2020caregnn`       | CARE-GNN (CIKM 2020): detector de GNN que se adapta a fraudadores camuflados           |
| `motie2024gnnreview`   | Revisão sistemática de GNN para fraude financeira (2024)                              |
| `dellagarza2023aml`    | Trabalho brasileiro (SBSI 2023): GNN para detecção de lavagem de dinheiro              |

## Fichamentos

Todas as leituras já têm uma nota de esqueleto em
[`docs/leituras/`](leituras/mapa-das-leituras.md), agrupadas por tema, com o status de cada uma.

| Chave | Assunto em uma linha | Entra em |
|-------|----------------------|----------|
| [diestel2017graph](leituras/diestel2017graph.md) | Livro-texto de teoria dos grafos: definições e resultados usados na modelagem | [graph.py](../src/pixfraud/graph.py), [estudo 01](../estudos/01_fundamentos.ipynb) |
| [easley2010networks](leituras/easley2010networks.md) | Redes, mercados e comportamento: centralidade, comunidades e mundo pequeno | [estudo 03](../estudos/03_metricas_de_centralidade.ipynb), [estudo 05](../estudos/05_modelos_de_redes.ipynb) |
| [brandes2001faster](leituras/brandes2001faster.md) | Algoritmo de intermediação usado (em versão amostrada) nos atributos de grafo | [features.py](../src/pixfraud/features.py) |
| [hagberg2008networkx](leituras/hagberg2008networkx.md) | A biblioteca NetworkX, usada para montar e medir os grafos | [graph.py](../src/pixfraud/graph.py), [algorithms.py](../src/pixfraud/algorithms.py) |
| [akoglu2015graph](leituras/akoglu2015graph.md) | Survey de detecção de anomalias em grafos; origem do OddBall e da culpa por associação | [communities.py](../src/pixfraud/communities.py), [flow.py](../src/pixfraud/flow.py), [resultados](resultados.md) |
| [weber2019aml](leituras/weber2019aml.md) | Elliptic (Bitcoin): compara atributos tabulares e de grafo, a mesma pergunta desta pesquisa | [resultados](resultados.md) |
| [liu2008isolation](leituras/liu2008isolation.md) | Isolation Forest: isola pontos raros com partições aleatórias | [anomaly.py](../src/pixfraud/anomaly.py) |
| [ester1996dbscan](leituras/ester1996dbscan.md) | DBSCAN: densidade e ruído; o ruído é o que tratamos como anomalia | [anomaly.py](../src/pixfraud/anomaly.py), [escolha do eps](../notebooks/01_analise_exploratoria.ipynb) |
| [pedregosa2011sklearn](leituras/pedregosa2011sklearn.md) | scikit-learn: implementação dos detectores e da validação cruzada | [anomaly.py](../src/pixfraud/anomaly.py), [experiment.py](../src/pixfraud/experiment.py) |
| [james2021isl](leituras/james2021isl.md) | Introdução ao aprendizado estatístico: validação e comparação de modelos | [teto supervisionado](resultados.md) |
| [bishop2006pattern](leituras/bishop2006pattern.md) | Fundamentos de reconhecimento de padrões e modelos probabilísticos | [anomaly.py](../src/pixfraud/anomaly.py) |
| [witten2011datamining](leituras/witten2011datamining.md) | Prática de mineração de dados; avaliação com classes desbalanceadas | [evaluation.py](../src/pixfraud/evaluation.py), [resultados](resultados.md) |
| [bcb2024pix](leituras/bcb2024pix.md) | O arranjo Pix: regras, MED e bloqueio cautelar | [bcb.py](../src/pixfraud/bcb.py), [proposta](proposta.md) |
| [bcb2024relatorio](leituras/bcb2024relatorio.md) | Relatório de gestão do Pix: números oficiais de uso e de fraude | [notebook 01](../notebooks/01_analise_exploratoria.ipynb) |
| [bcb2026dadosabertos](leituras/bcb2026dadosabertos.md) | API de dados abertos do Pix: estatísticas de transações e de fraudes | [bcb.py](../src/pixfraud/bcb.py), [notebook 01](../notebooks/01_analise_exploratoria.ipynb), [dados](../data/README.md) |
| [lopezrojas2016paysim](leituras/lopezrojas2016paysim.md) | PaySim: simulador de dinheiro móvel, referência para gerar dados sintéticos | [simulation.py](../src/pixfraud/simulation.py), [external.py](../src/pixfraud/external.py) |
| [altman2023realistic](leituras/altman2023realistic.md) | AMLworld: transações sintéticas de lavagem com tipologias em grafo | [external.py](../src/pixfraud/external.py), [resultados, seção 8](resultados.md) |
| [guerra2025gnnfraude](leituras/guerra2025gnnfraude.md) | TCC (ICMC-USP, 2025): mesmo problema desta pesquisa, com GNN supervisionada | [ideias futuras](futuro/ideias-futuras.md) |
| [dou2020caregnn](leituras/dou2020caregnn.md) | CARE-GNN (CIKM 2020): GNN contra fraudadores camuflados | [ideias futuras](futuro/ideias-futuras.md) |
| [motie2024gnnreview](leituras/motie2024gnnreview.md) | Revisão sistemática de GNN para fraude financeira (2024) | [ideias futuras](futuro/ideias-futuras.md) |
| [dellagarza2023aml](leituras/dellagarza2023aml.md) | Trabalho brasileiro (SBSI 2023): GNN para lavagem de dinheiro | [resultados](resultados.md) |
