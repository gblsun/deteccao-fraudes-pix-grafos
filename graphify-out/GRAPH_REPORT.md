# Graph Report - deteccao-fraudes-pix-grafos  (2026-09-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1218 nodes · 2372 edges · 86 communities (81 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 129 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `688b48e1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- experiment.py
- algorithms.py
- communities.py
- flow.py
- build_graph
- test_docs.py
- Módulos
- main
- mapa-das-leituras.md
- test_anomaly.py
- compare_groups
- generate_dataset
- load_experiment_config
- draw_graph
- SimulationConfig
- Diário 2026-09-21
- plot_value_matrix
- resultados.md
- average-precision.md
- main
- test_features.py
- save_dataset
- prepare
- mapa-da-pesquisa.md
- __init__.py
- pixfraud
- pandas
- visualization.py
- graph_from_edges
- compare_runs
- simulation.py
- test_scripts.py
- mapa-do-relatorio.md
- build_features
- ilustrar_grafos_de_conhecimento.py
- Resultados
- graph_from_csv
- mapa-dos-testes.md
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- trilha-de-estudos.md
- bcb.py
- guia-do-explorador.md
- stats.py
- akoglu2015graph
- altman2023realistic
- bcb2024pix
- bcb2024relatorio
- bcb2026dadosabertos
- bishop2006pattern
- brandes2001faster
- dellagarza2023aml
- diestel2017graph
- dou2020caregnn
- easley2010networks
- ester1996dbscan
- guerra2025gnnfraude
- hagberg2008networkx
- james2021isl
- liu2008isolation
- lopezrojas2016paysim
- motie2024gnnreview
- pedregosa2011sklearn
- weber2019aml
- witten2011datamining
- {{title}}
- Mapa das leituras
- Resultados
- propagate_risk
- Diário {{date}}
- Metodologia
- test_flow.py
- Instruções para agentes
- Detecção sob camuflagem adversarial
- GNN supervisionada como próximo passo
- Glossário
- Reunião {{date}}
- Ideias futuras
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- Configurações
- Diário de pesquisa
- Reuniões de orientação
- Scripts

## God Nodes (most connected - your core abstractions)
1. `Módulos` - 43 edges
2. `generate_dataset()` - 30 edges
3. `build_graph()` - 22 edges
4. `SimulationConfig` - 20 edges
5. `prepare()` - 16 edges
6. `main()` - 15 edges
7. `load_experiment_config()` - 14 edges
8. `draw_graph()` - 14 edges
9. `detect_communities()` - 14 edges
10. `main()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Escrevendo um teste novo` --references--> `SimulationConfig`  [INFERRED]
  tests/mapa-dos-testes.md → src/pixfraud/simulation.py
- `Próximo passo` --references--> `densest_subgraph()`  [INFERRED]
  docs/diario/2026-09-22.md → src/pixfraud/communities.py
- `6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)` --references--> `propagate_risk()`  [INFERRED]
  docs/modelos.md → src/pixfraud/flow.py
- `Outros modelos que caberiam nesta pesquisa` --references--> `Detection`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Bootstrap` --references--> `bootstrap_metric()`  [INFERRED]
  docs/glossario/bootstrap.md → src/pixfraud/stats.py

## Import Cycles
- None detected.

## Communities (86 total, 5 thin omitted)

### Community 0 - "experiment.py"
Cohesion: 0.13
Nodes (19): copy, dataclasses, datetime, importlib_metadata, platform, Quanto cada atributo contribui, e quão longe estamos de um modelo que viu os…, Culpa por associação: com algumas fraudes já conhecidas, quanto se acha do…, sklearn_cluster (+11 more)

### Community 1 - "algorithms.py"
Cohesion: 0.05
Nodes (59): 8. Validação externa: AMLworld, Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Ferramentas para criar grafos, Roteiro, heapq, itertools (+51 more)

### Community 2 - "communities.py"
Cohesion: 0.06
Nodes (60): Coeficiente de participação, Comunidades e modularidade (Louvain), Egonet e OddBall, K-núcleo (core number), Outros modelos que caberiam nesta pesquisa, main(), community_summary(), core_numbers() (+52 more)

### Community 3 - "flow.py"
Cohesion: 0.26
Nodes (13): Fluxo máximo e corte mínimo, _as_list(), blocking_cut(), _flow_network(), max_money_flow(), DiGraph, Fluxo de dinheiro, cortes mínimos ("onde bloquear") e propagação de risco. *…, Contas que estão em algum caminho de uma origem até o destino. (+5 more)

### Community 4 - "build_graph"
Cohesion: 0.07
Nodes (43): Caminho temporal, Grafo direcionado ponderado, Tempo de permanência (dwell time), _animacao(), quadro(), _dataset_pequeno(), _legenda(), main() (+35 more)

### Community 5 - "test_docs.py"
Cohesion: 0.05
Nodes (44): ast, Decisões (e por quê), Diário 2026-09-22, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Abrir (+36 more)

### Community 6 - "Módulos"
Cohesion: 0.07
Nodes (45): Average precision (AP), Precision@k, main(), Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.…, evaluate(), DataFrame, Series, Todas as métricas do módulo para uma detecção; ``k`` padrão = nº de fraudes… (+37 more)

### Community 7 - "main"
Cohesion: 0.06
Nodes (44): DatetimeIndex, Explicabilidade para auditoria, O que existe hoje, O que falta, Onde entraria no código, Por que importa para esta pesquisa especificamente, Custo operacional, não só AP e precision@k, Grafos heterogêneos (+36 more)

### Community 8 - "mapa-das-leituras.md"
Cohesion: 0.26
Nodes (3): Ideias futuras, Mapa das leituras, Conclusão

### Community 9 - "test_anomaly.py"
Cohesion: 0.08
Nodes (32): DBSCAN e k-distance, Isolation Forest, Local Outlier Factor (LOF), 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos) (+24 more)

### Community 10 - "compare_groups"
Cohesion: 0.08
Nodes (24): Bootstrap, Correção de Holm, Delta de Cliff ($\delta$), Teste de Mann-Whitney, bootstrap_metric(), cliffs_delta(), compare_groups(), contingency_test() (+16 more)

### Community 11 - "generate_dataset"
Cohesion: 0.07
Nodes (31): _accounts_table(), _after_activity(), _camouflage_transactions(), _fraud_ring(), generate_dataset(), _launder(), _normal_transactions(), DataFrame (+23 more)

### Community 12 - "load_experiment_config"
Cohesion: 0.15
Nodes (20): all_metrics(), explorer_page(), load(), prepared(), DataFrame, Series, Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia. (+12 more)

### Community 13 - "draw_graph"
Cohesion: 0.09
Nodes (31): Axes, Figure, draw_graph(), explain_account(), flow_layout(), reorder(), _format_amount(), graph_html() (+23 more)

### Community 14 - "SimulationConfig"
Cohesion: 0.14
Nodes (17): main(), Series, Escore de um detector não supervisionado (não usa as contas conhecidas)., _scores(), load_scenarios(), Path, Lê os cenários de ``configs/cenarios.yaml``: nome -> parâmetros da simulação a…, load_config() (+9 more)

### Community 15 - "Diário 2026-09-21"
Cohesion: 0.33
Nodes (5): Decisões (e por quê), Diário 2026-09-21, Dúvidas e bloqueios, Próximo passo, Resultados e observações

### Community 16 - "plot_value_matrix"
Cohesion: 0.16
Nodes (15): main(), _plot_effects(), _plot_metric(), DataFrame, Path, Series, Matriz conjunto de atributos × cenário da média da métrica, um painel por…, Matriz atributo × cenário do delta de Cliff médio (> 0: maior nas contas… (+7 more)

### Community 17 - "resultados.md"
Cohesion: 0.15
Nodes (4): Conta laranja (conta de passagem), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Glossário

### Community 19 - "main"
Cohesion: 0.15
Nodes (15): main(), _plot_typologies(), _pool(), DataFrame, Path, Junta as janelas: acertos somados sobre contas somadas, por tipologia,…, Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo., main() (+7 more)

### Community 20 - "test_features.py"
Cohesion: 0.29
Nodes (6): chain(), fixture, Testes de `pixfraud.features`: cada atributo conferido à mão num grafo pequeno., Cadeia A -> B -> C -> D, um pagamento extra E -> B e uma conta F sem transações., test_features(), test_graph_aggregates_repeated_pairs()

### Community 21 - "save_dataset"
Cohesion: 0.20
Nodes (8): main(), Gera o dataset sintético de transações PIX. Uso: python…, Path, Grava ``accounts.csv`` e ``transactions.csv`` em ``out_dir`` (criada se não…, save_dataset(), streamlit_testing_v1, Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver…, test_app_runs_all_tabs()

### Community 22 - "prepare"
Cohesion: 0.10
Nodes (28): Random Forest (como teto supervisionado), Validação cruzada estratificada, main(), _plot_ablation(), _plot_ceiling(), DataFrame, Path, Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo. (+20 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.15
Nodes (6): Parâmetros dos experimentos, Cronograma, Diário de pesquisa, Mapa da pesquisa, Atas de reunião, Mapa dos scripts

### Community 30 - "pandas"
Cohesion: 0.14
Nodes (18): Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório:…, networkx, pandas, pathlib, pytest, Avalia a detecção ao longo do tempo: a quadrilha é sinalizada a tempo de…, Cria, resume e salva grafos sem precisar escrever código. O formato de saída…, Atributos por conta usados pelos detectores de anomalia. Os atributos são… (+10 more)

### Community 31 - "visualization.py"
Cohesion: 0.11
Nodes (20): argparse, matplotlib, matplotlib_animation, matplotlib_colors, matplotlib_lines, matplotlib_pyplot, pypandoc, Avalia os detectores em cenários de dificuldade (configs/cenarios.yaml). O… (+12 more)

### Community 32 - "graph_from_edges"
Cohesion: 0.18
Nodes (13): O que fiz, adjacency_matrix(), describe(), graph_from_edges(), DataFrame, Graph, Series, Resumo das propriedades básicas do grafo (útil para conferir exercícios). (+5 more)

### Community 33 - "compare_runs"
Cohesion: 0.15
Nodes (17): Intervalo de confiança (IC 95%), Teste de Wilcoxon pareado, _evaluate(), Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,…, main(), _plot(), DataFrame, Path (+9 more)

### Community 34 - "simulation.py"
Cohesion: 0.17
Nodes (10): html, json, math, numpy, Gera o explorador interativo da rede inteira (HTML). A página mostra todas as…, Explorador interativo da rede inteira: uma página HTML com sigma.js (WebGL).…, Padrões de fraude como pequenos grafos, para estudo e para injetar em redes…, Gerador de um dataset sintético de transações PIX com cenários de fraude. A… (+2 more)

### Community 35 - "test_scripts.py"
Cohesion: 0.29
Nodes (13): os, subprocess, _check_metadata(), Testes de fumaça dos scripts de avaliação, num dataset minúsculo., O *_meta.json existe e tem o que é preciso para refazer o resultado., _run(), test_avaliar_atributos(), test_avaliar_cenarios() (+5 more)

### Community 36 - "mapa-do-relatorio.md"
Cohesion: 0.20
Nodes (5): Resumo {.unnumbered}, Como escrever, Estrutura, Relatório final, Mapa do relatório

### Community 37 - "build_features"
Cohesion: 0.08
Nodes (26): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+18 more)

### Community 38 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.22
Nodes (13): collections, _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), Path (+5 more)

### Community 39 - "Resultados"
Cohesion: 0.17
Nodes (12): 10. Conclusão parcial, 11. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador, 3. O gerador comparado com o Pix real, 4. Perfis: o que distingue cada papel, e quem os detectores encontram, 5. Detecção a tempo: o dinheiro ainda estava lá?, 7. Contribuição de cada atributo e o teto supervisionado (+4 more)

### Community 40 - "graph_from_csv"
Cohesion: 0.18
Nodes (13): MultiDiGraph, _attach_roles(), main(), DiGraph, Path, graph_from_csv(), money_trail(), DiGraph (+5 more)

### Community 41 - "mapa-dos-testes.md"
Cohesion: 0.33
Nodes (4): Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "trilha-de-estudos.md"
Cohesion: 0.13
Nodes (9): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário, Trilha de estudos, Convenções, Notebooks da pesquisa, Mapa dos notebooks (+1 more)

### Community 46 - "bcb.py"
Cohesion: 0.22
Nodes (8): main(), Baixa estatísticas do PIX da API de dados abertos do Banco Central. Exemplos:…, fetch(), DataFrame, Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. Os…, Baixa um recurso da API em uma única requisição. ``resource`` é um apelido de…, urllib_parse, urllib_request

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.22
Nodes (3): Explorador interativo, O que tem, Guia do explorador

### Community 48 - "stats.py"
Cohesion: 0.22
Nodes (8): collections_abc, scipy, null_model_test(), DiGraph, Inferência estatística para a pesquisa. * ``compare_groups``: cada atributo…, Compara ``statistic(graph)`` com grafos aleatórios de mesmos graus de entrada e…, Testes de `pixfraud.stats`: tamanho de efeito, correções, bootstrap, testes…, test_null_model_detects_excess_reciprocity()

### Community 49 - "akoglu2015graph"
Cohesion: 0.25
Nodes (8): akoglu2015graph, Avaliação, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 50 - "altman2023realistic"
Cohesion: 0.25
Nodes (8): altman2023realistic, Avaliação, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 51 - "bcb2024pix"
Cohesion: 0.25
Nodes (8): Avaliação, bcb2024pix, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 52 - "bcb2024relatorio"
Cohesion: 0.15
Nodes (9): Avaliação, bcb2024relatorio, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto (+1 more)

### Community 53 - "bcb2026dadosabertos"
Cohesion: 0.25
Nodes (8): Avaliação, bcb2026dadosabertos, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 54 - "bishop2006pattern"
Cohesion: 0.25
Nodes (8): Avaliação, bishop2006pattern, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 55 - "brandes2001faster"
Cohesion: 0.25
Nodes (8): Avaliação, brandes2001faster, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

### Community 56 - "dellagarza2023aml"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, dellagarza2023aml, Limitações, Método, Problema, Relação com o projeto

### Community 57 - "diestel2017graph"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, diestel2017graph, Limitações, Método, Problema, Relação com o projeto

### Community 58 - "dou2020caregnn"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, dou2020caregnn, Limitações, Método, Problema, Relação com o projeto

### Community 59 - "easley2010networks"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, easley2010networks, Limitações, Método, Problema, Relação com o projeto

### Community 60 - "ester1996dbscan"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, ester1996dbscan, Limitações, Método, Problema, Relação com o projeto

### Community 61 - "guerra2025gnnfraude"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, guerra2025gnnfraude, Limitações, Método, Problema, Relação com o projeto

### Community 62 - "hagberg2008networkx"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, hagberg2008networkx, Limitações, Método, Problema, Relação com o projeto

### Community 63 - "james2021isl"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, james2021isl, Limitações, Método, Problema, Relação com o projeto

### Community 64 - "liu2008isolation"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, liu2008isolation, Método, Problema, Relação com o projeto

### Community 65 - "lopezrojas2016paysim"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, lopezrojas2016paysim, Método, Problema, Relação com o projeto

### Community 66 - "motie2024gnnreview"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, motie2024gnnreview, Método, Problema, Relação com o projeto

### Community 67 - "pedregosa2011sklearn"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, Método, pedregosa2011sklearn, Problema, Relação com o projeto

### Community 68 - "weber2019aml"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto, weber2019aml

### Community 69 - "witten2011datamining"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto, witten2011datamining

### Community 70 - "{{title}}"
Cohesion: 0.25
Nodes (8): Avaliação, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto, {{title}}

### Community 72 - "Mapa das leituras"
Cohesion: 0.29
Nodes (7): Aprendizado de máquina e avaliação, Como acrescentar uma leitura, Dados: Pix e datasets públicos, Detecção de anomalias em grafos, Grafos e redes, Mapa das leituras, Trabalhos relacionados: fraude com redes neurais em grafos

### Community 73 - "Resultados"
Cohesion: 0.29
Nodes (7): A comparação entre atributos tabulares e de grafo depende do gerador, Detectar a tempo de bloquear o dinheiro, Perfis de fraude, Poucos rótulos rendem muito, Resultados, Validação do dataset sintético, Validação externa

### Community 74 - "propagate_risk"
Cohesion: 0.33
Nodes (6): Propagação de risco (culpa por associação), 6. Culpa por associação: usar as contestações que já existem, propagate_risk(), Series, Culpa por associação: PageRank personalizado a partir das contas ``seeds``. A…, test_propagate_risk_reaches_ring_members()

### Community 75 - "Diário {{date}}"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário {{date}}, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 76 - "Metodologia"
Cohesion: 0.33
Nodes (6): Atributos, Avaliação, Dados, Detectores, Metodologia, Modelagem em grafo

### Community 77 - "test_flow.py"
Cohesion: 0.22
Nodes (6): blocking_accounts(), Menor conjunto de contas cujo bloqueio separa ``sources`` de ``sink``. Usa a…, A(), fixture, Testes de `pixfraud.flow`: fluxo máximo, corte mínimo, contas a bloquear e…, test_blocking_accounts()

### Community 78 - "Instruções para agentes"
Cohesion: 0.40
Nodes (5): Ao editar notas, Como se orientar, Código, Instruções para agentes, Regra principal

### Community 79 - "Detecção sob camuflagem adversarial"
Cohesion: 0.40
Nodes (5): Como isso poderia ser avaliado aqui, Detecção sob camuflagem adversarial, O problema, O que a literatura já mostra, Relação com o resto do projeto

### Community 80 - "GNN supervisionada como próximo passo"
Cohesion: 0.40
Nodes (5): Comparação direta: o TCC de Guerra, Custo, GNN supervisionada como próximo passo, O que mudaria no código, Por que faz sentido depois desta pesquisa, não antes

### Community 81 - "Glossário"
Cohesion: 0.40
Nodes (5): Avaliação e estatística, Detecção, Glossário, Pix e dados, Teoria dos grafos

### Community 82 - "Reunião {{date}}"
Cohesion: 0.40
Nodes (5): Desde a última reunião, Discussão e decisões, Dúvidas em aberto, Próximos passos, Reunião {{date}}

### Community 84 - "Ideias futuras"
Cohesion: 0.50
Nodes (4): Como acrescentar uma ideia, Do autor da pesquisa, Ideias futuras, Outras ideias

### Community 85 - "Documentação da pesquisa"
Cohesion: 0.50
Nodes (4): A pesquisa, Anotações, Documentação da pesquisa, Documentação do código e dos dados

### Community 86 - "A rede Pix dentro do cofre"
Cohesion: 0.40
Nodes (4): A rede Pix dentro do cofre, Como gerar outros recortes, Figuras estáticas, Rede inteira, interativa

### Community 87 - "Revisão bibliográfica"
Cohesion: 0.50
Nodes (4): Como fichar uma leitura, Fichamentos, Revisão bibliográfica, Sugestões de leitura

### Community 88 - "Configurações"
Cohesion: 0.67
Nodes (3): Configurações, Criar um cenário, Mudar um parâmetro

### Community 89 - "Diário de pesquisa"
Cohesion: 0.67
Nodes (3): Diário de pesquisa, Notas, Para que serve

### Community 90 - "Reuniões de orientação"
Cohesion: 0.67
Nodes (3): Atas, Como escrever uma ata que ajuda o grafo, Reuniões de orientação

### Community 91 - "Scripts"
Cohesion: 0.67
Nodes (3): Mapa, Reproduzir os resultados, Scripts

## Knowledge Gaps
- **308 isolated node(s):** `Como usar`, `Dados de exemplo`, `Roteiro`, `Decisões (e por quê)`, `Dúvidas e bloqueios` (+303 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 596 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `algorithms.py`, `communities.py`, `flow.py`, `build_graph`, `main`, `test_anomaly.py`, `compare_groups`, `generate_dataset`, `draw_graph`, `SimulationConfig`, `plot_value_matrix`, `prepare`, `graph_from_edges`, `compare_runs`, `build_features`, `graph_from_csv`, `bcb.py`, `propagate_risk`, `test_flow.py`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `Módulos` to `guia-do-explorador.md`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Resultados` connect `Resultados` to `resultados.md`, `propagate_risk`, `algorithms.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Módulos` (e.g. with `find_pattern()` and `hubs_authorities()`) actually correct?**
  _`Módulos` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `build_graph()` (e.g. with `Grafo direcionado ponderado` and `Módulos`) actually correct?**
  _`build_graph()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Como usar`, `Dados de exemplo`, `Roteiro` to the rest of the system?**
  _308 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `experiment.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13043478260869565 - nodes in this community are weakly interconnected._