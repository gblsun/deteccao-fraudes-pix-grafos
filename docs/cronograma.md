# Cronograma

Duração: 12 meses. Marque `[x]` quando a etapa for concluída e registre na coluna
"Entregas" onde está o resultado.

> **A preencher:** a coluna "Meses" deve seguir o cronograma aprovado na proposta.

| Status | Atividade                                                   | Meses | Entregas no repositório                                  |
|:------:|-------------------------------------------------------------|:-----:|----------------------------------------------------------|
| [ ]    | Revisão bibliográfica e fundamentação teórica               |       | `docs/revisao-bibliografica.md`, `docs/referencias.bib`  |
| [ ]    | Definição da metodologia e modelagem do problema            |       | `docs/proposta.md`, `configs/experimento.yaml`           |
| [ ]    | Construção do dataset sintético PIX / seleção de dados públicos |   | `src/pixfraud/simulation.py`, `src/pixfraud/bcb.py`      |
| [ ]    | Análise exploratória de dados e validação do dataset        |       | `notebooks/01_analise_exploratoria.ipynb`                |
| [ ]    | Modelagem das transações em grafos                          |       | `src/pixfraud/graph.py`                                  |
| [ ]    | Extração de métricas estruturais dos grafos                 |       | `src/pixfraud/features.py`                               |
| [ ]    | Aplicação de técnicas de machine learning                   |       | `src/pixfraud/anomaly.py`                                |
| [ ]    | Desenvolvimento de visualizações em grafos e heatmaps       |       | `src/pixfraud/visualization.py`, `reports/figures/`      |
| [ ]    | Análise de perfis de fraude e interpretação dos resultados  |       | notebooks                                                |
| [ ]    | Comparação entre abordagem tabular e grafos                 |       | `reports/results/metricas.csv`                           |
| [ ]    | Avaliação dos modelos e métricas de desempenho              |       | `src/pixfraud/evaluation.py`, `reports/results/`         |
| [ ]    | Escrita, revisão e finalização do relatório científico      |       | relatório final                                          |
