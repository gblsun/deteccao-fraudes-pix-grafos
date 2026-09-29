# Graph Report - deteccao-fraudes-pix-grafos  (2026-09-28)

## Corpus Check
- 174 files · ~76,125 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .csv 2, .bib 1)

## Summary
- 1359 nodes · 2740 edges · 103 communities (98 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 144 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4a11005`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- gnn.py
- pytest
- communities.py
- main
- temporal.py
- test_docs.py
- Módulos
- test_online.py
- Graph
- test_anomaly.py
- test_stats.py
- test_simulation.py
- load_experiment_config
- draw_graph
- load_scenarios
- explorer_payload
- _evaluate
- resultados.md
- average-precision.md
- save_metadata
- build_graph
- load_config
- run_detectors
- mapa-da-pesquisa.md
- plot_value_matrix
- _animacao
- mapa-das-leituras.md
- build_features
- temporal_features
- pixfraud
- tx
- experiment.py
- graph_from_edges
- compare_runs
- patterns.py
- test_scripts.py
- mapa-do-relatorio.md
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- ilustrar_grafos_de_conhecimento.py
- Resultados
- graph_from_csv
- mapa-dos-testes.md
- test_patterns.py
- _random_seconds
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- test_bcb.py
- guia-do-explorador.md
- Modelos usados na pesquisa (e outros que caberiam)
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
- test_communities.py
- Mapa das leituras
- Resultados
- propagate_risk
- Diário {{date}}
- Metodologia
- community_layout
- Instruções para agentes
- Detecção sob camuflagem adversarial
- GNN supervisionada como próximo passo
- Glossário
- Reunião {{date}}
- generate_dataset
- Ideias futuras
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- Configurações
- Diário de pesquisa
- Reuniões de orientação
- main
- main
- _fit_sage
- test_gnn.py
- oddball_scores
- prepare
- Diário 2026-09-26
- SimulationConfig
- Reunião 2026-09-24
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- test_app.py

## God Nodes (most connected - your core abstractions)
1. `Módulos` - 43 edges
2. `generate_dataset()` - 33 edges
3. `build_graph()` - 22 edges
4. `SimulationConfig` - 20 edges
5. `prepare()` - 19 edges
6. `load_experiment_config()` - 17 edges
7. `save_metadata()` - 16 edges
8. `load_config()` - 16 edges
9. `summarize_runs()` - 16 edges
10. `compare_runs()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `1. Preparação dos atributos` --references--> `prepare_matrix()`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Próximo passo` --references--> `densest_subgraph()`  [INFERRED]
  docs/diario/2026-09-22.md → src/pixfraud/communities.py
- `Graphify: o mapa do código` --references--> `graph_features()`  [INFERRED]
  README.md → src/pixfraud/features.py
- `6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)` --references--> `propagate_risk()`  [INFERRED]
  docs/modelos.md → src/pixfraud/flow.py
- `Escrevendo um teste novo` --references--> `SimulationConfig`  [INFERRED]
  tests/mapa-dos-testes.md → src/pixfraud/simulation.py

## Import Cycles
- None detected.

## Communities (103 total, 5 thin omitted)

### Community 0 - "gnn.py"
Cohesion: 0.17
Nodes (19): Redes neurais para grafos (GNN), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN), Index, sklearn_model_selection, _adjacency(), dominant_scores(), DataFrame, Graph (+11 more)

### Community 1 - "pytest"
Cohesion: 0.09
Nodes (31): heapq, itertools, networkx_algorithms, pytest, bipartite_projection(), find_pattern(), hubs_authorities(), laundering_depth() (+23 more)

### Community 2 - "communities.py"
Cohesion: 0.16
Nodes (19): Coeficiente de participação, Comunidades e modularidade (Louvain), K-núcleo (core number), core_numbers(), detect_communities(), participation_coefficient(), _power_law_score(), ndarray (+11 more)

### Community 3 - "main"
Cohesion: 0.15
Nodes (19): Fluxo máximo e corte mínimo, _attach_roles(), main(), DiGraph, Path, _as_list(), blocking_accounts(), blocking_cut() (+11 more)

### Community 4 - "temporal.py"
Cohesion: 0.16
Nodes (17): Caminho temporal, _best_hops(), _check_direction(), DiGraph, Timedelta, Timestamp, Grafos temporais: caminhos que respeitam a ordem cronológica dos Pix. No grafo…, Menor nº de saltos entre os eventos compatíveis com um Pix no instante ``t``. (+9 more)

### Community 5 - "test_docs.py"
Cohesion: 0.08
Nodes (30): ast, Decisões (e por quê), Diário 2026-09-22, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Abrir (+22 more)

### Community 6 - "Módulos"
Cohesion: 0.07
Nodes (45): Average precision (AP), Precision@k, main(), Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.…, evaluate(), DataFrame, Series, Todas as métricas do módulo para uma detecção; ``k`` padrão = nº de fraudes… (+37 more)

### Community 7 - "test_online.py"
Cohesion: 0.07
Nodes (36): DatetimeIndex, Explicabilidade para auditoria, O que existe hoje, O que falta, Onde entraria no código, Por que importa para esta pesquisa especificamente, Custo operacional, não só AP e precision@k, Grafos heterogêneos (+28 more)

### Community 8 - "Graph"
Cohesion: 0.20
Nodes (16): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), densest_subgraph(), fraudar_blocks(), fraudar_scores(), _peel(), Graph, Subgrafo de maior densidade (peso total / nº de contas), pelo algoritmo guloso… (+8 more)

### Community 9 - "test_anomaly.py"
Cohesion: 0.11
Nodes (26): DBSCAN e k-distance, Isolation Forest, Local Outlier Factor (LOF), Outros modelos que caberiam nesta pesquisa, dbscan(), Detection, isolation_forest(), local_outlier_factor() (+18 more)

### Community 10 - "test_stats.py"
Cohesion: 0.07
Nodes (31): Bootstrap, Correção de Holm, Delta de Cliff ($\delta$), Teste de Mann-Whitney, bootstrap_metric(), cliffs_delta(), compare_groups(), contingency_test() (+23 more)

### Community 11 - "test_simulation.py"
Cohesion: 0.14
Nodes (9): dataset(), fixture, parametrize, Testes de `pixfraud.simulation`: reprodutibilidade, rótulos e parâmetros de…, test_commercial_hours_also_apply_to_slow_forwards(), test_fraud_account_age_follows_parameter(), test_quiet_people_send_fewer_pix(), share_almost_inactive() (+1 more)

### Community 12 - "load_experiment_config"
Cohesion: 0.15
Nodes (20): all_metrics(), explorer_page(), load(), prepared(), DataFrame, Series, Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia. (+12 more)

### Community 13 - "draw_graph"
Cohesion: 0.10
Nodes (26): Figure, draw_graph(), explain_account(), flow_layout(), reorder(), _format_amount(), graph_html(), _layout() (+18 more)

### Community 14 - "load_scenarios"
Cohesion: 0.12
Nodes (18): main(), _plot(), DataFrame, Path, Matriz método × cenário da AP média., main(), _plot(), DataFrame (+10 more)

### Community 15 - "explorer_payload"
Cohesion: 0.20
Nodes (15): main(), explorer_payload(), _first_days(), network_explorer_html(), DataFrame, DiGraph, Path, Series (+7 more)

### Community 16 - "_evaluate"
Cohesion: 0.24
Nodes (10): _evaluate(), main(), _plot_effects(), _plot_metric(), DataFrame, Path, Series, Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,… (+2 more)

### Community 17 - "resultados.md"
Cohesion: 0.13
Nodes (4): Conta laranja (conta de passagem), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Glossário

### Community 19 - "save_metadata"
Cohesion: 0.15
Nodes (15): main(), _plot_typologies(), _pool(), DataFrame, Path, Junta as janelas: acertos somados sobre contas somadas, por tipologia,…, Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo., main() (+7 more)

### Community 20 - "build_graph"
Cohesion: 0.20
Nodes (10): Grafo direcionado ponderado, build_graph(), Monta o grafo direcionado de transações. Todas as transferências de um mesmo…, chain(), fixture, Testes de `pixfraud.features`: cada atributo conferido à mão num grafo pequeno., Cadeia A -> B -> C -> D, um pagamento extra E -> B e uma conta F sem transações., test_features() (+2 more)

### Community 21 - "load_config"
Cohesion: 0.33
Nodes (7): main(), load_config(), Path, Grava ``accounts.csv`` e ``transactions.csv`` em ``out_dir`` (criada se não…, Lê a seção ``simulacao`` do arquivo YAML de experimento., save_dataset(), test_repository_config_is_valid()

### Community 22 - "run_detectors"
Cohesion: 0.10
Nodes (24): Decisões (e por quê), Diário 2026-09-28, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Random Forest (como teto supervisionado), Validação cruzada estratificada (+16 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.09
Nodes (11): Parâmetros dos experimentos, Cronograma, Diário de pesquisa, Ideias futuras, Mapa da pesquisa, Atas de reunião, Trilha de estudos, Convenções (+3 more)

### Community 24 - "plot_value_matrix"
Cohesion: 0.19
Nodes (14): Axes, main(), _plot_ablation(), _plot_ceiling(), DataFrame, Path, Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo., Matriz conjunto × (cenário, modelo) da AP média, com o Random Forest… (+6 more)

### Community 25 - "_animacao"
Cohesion: 0.22
Nodes (13): _animacao(), quadro(), _dataset_pequeno(), _legenda(), main(), _padroes(), Path, O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora. (+5 more)

### Community 27 - "build_features"
Cohesion: 0.21
Nodes (12): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), build_features(), graph_features(), DataFrame, DiGraph (+4 more)

### Community 28 - "temporal_features"
Cohesion: 0.24
Nodes (11): Tempo de permanência (dwell time), dwell_time(), DataFrame, Series, Tempo de permanência do dinheiro, em minutos, por conta. Para cada Pix…, Grau de entrada por janela de tempo: linhas = janelas, colunas = contas. Cada…, Atributos temporais por conta: ``dwell_time_min`` e ``max_daily_in_degree``.…, temporal_features() (+3 more)

### Community 31 - "experiment.py"
Cohesion: 0.07
Nodes (62): Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório:…, argparse, collections_abc, copy, dataclasses, html, importlib_metadata, json (+54 more)

### Community 32 - "graph_from_edges"
Cohesion: 0.12
Nodes (17): Decisões (e por quê), Diário 2026-09-21, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, adjacency_matrix(), describe() (+9 more)

### Community 33 - "compare_runs"
Cohesion: 0.13
Nodes (18): Intervalo de confiança (IC 95%), Teste de Wilcoxon pareado, main(), _plot(), DataFrame, Path, Matriz método × cenário da AP média., main() (+10 more)

### Community 34 - "patterns.py"
Cohesion: 0.17
Nodes (22): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), fan_in(), fan_out(), fraud_nodes(), inject() (+14 more)

### Community 35 - "test_scripts.py"
Cohesion: 0.06
Nodes (56): csv, datetime, os, Pattern, re, como_json(), _filtros_do_cofre(), grafo_de_notas() (+48 more)

### Community 36 - "mapa-do-relatorio.md"
Cohesion: 0.12
Nodes (8): Resumo {.unnumbered}, Introdução, Fundamentação teórica, Conclusão, Como escrever, Estrutura, Relatório final, Mapa do relatório

### Community 37 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.14
Nodes (14): Atributos, Como começar, Como o dinheiro se move, Dados, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Estrutura, Grafos de conhecimento: Obsidian e Graphify, Graphify: o mapa do código (+6 more)

### Community 38 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.22
Nodes (13): collections, _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), Path (+5 more)

### Community 39 - "Resultados"
Cohesion: 0.14
Nodes (14): 10. Redes neurais para grafos (GNN), 12. Cuidados na interpretação, 13. Conclusão parcial, 14. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador, 3. O gerador comparado com o Pix real, 4. Perfis: o que distingue cada papel, e quem os detectores encontram (+6 more)

### Community 40 - "graph_from_csv"
Cohesion: 0.18
Nodes (13): MultiDiGraph, graph_from_csv(), money_trail(), DiGraph, Path, Lê uma tabela de transações em CSV e monta o grafo. ``source``, ``target`` e…, Subgrafo das contas alcançáveis a partir de ``account`` em até ``max_hops``…, A() (+5 more)

### Community 41 - "mapa-dos-testes.md"
Cohesion: 0.33
Nodes (4): Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes

### Community 42 - "test_patterns.py"
Cohesion: 0.22
Nodes (9): cycle(), Ciclo (*round-tripping*): o dinheiro passa por várias contas e volta à primeira., parametrize, Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num…, test_chain_loses_fee_at_each_hop(), test_cycle_is_strongly_connected(), test_flow_layout_and_exports(), test_mule_ring_money_reaches_collector() (+1 more)

### Community 43 - "_random_seconds"
Cohesion: 0.20
Nodes (10): _after_activity(), _fraud_ring(), _launder(), ndarray, _random_seconds(), Instantes (em segundos desde o início) seguindo o perfil horário…, Instante em que ``delay`` segundos de atividade terão passado a partir de…, Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora. (+2 more)

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "test_bcb.py"
Cohesion: 0.10
Nodes (20): io, main(), Baixa estatísticas do PIX da API de dados abertos do Banco Central. Exemplos:…, fetch(), DataFrame, Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. Os…, Baixa um recurso da API em uma única requisição. ``resource`` é um apelido de…, Detecção de fraudes em transações PIX com teoria dos grafos e machine learning. (+12 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.33
Nodes (3): Explorador interativo, O que tem, Guia do explorador

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.22
Nodes (9): 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), Como as peças se encaixam (+1 more)

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
Cohesion: 0.25
Nodes (8): Avaliação, bcb2024relatorio, Citações úteis, Dados, Limitações, Método, Problema, Relação com o projeto

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

### Community 71 - "test_communities.py"
Cohesion: 0.22
Nodes (8): community_summary(), Tamanho, arestas internas e externas de cada comunidade (e nº de fraudes, se…, fixture, parametrize, Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e…, Dois cliques de 5 contas ligados por uma única aresta a4 -> b0., test_communities_split_the_cliques(), two_cliques()

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

### Community 77 - "community_layout"
Cohesion: 0.25
Nodes (9): community_layout(), _free_spot(), _place_center(), Graph, ndarray, Primeiro ponto da espiral de girassol em que um disco de ``radius`` não encosta…, Posições que deixam as comunidades visíveis. Cada comunidade recebe um disco de…, Põe cada grupo ligado de ``sub`` (uma quadrilha, em geral) num círculo em volta… (+1 more)

### Community 78 - "Instruções para agentes"
Cohesion: 0.33
Nodes (6): Ao editar notas, Autoria, Como se orientar, Código, Instruções para agentes, Regra principal: LGPD no contexto do Pix

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

### Community 83 - "generate_dataset"
Cohesion: 0.31
Nodes (9): _accounts_table(), _camouflage_transactions(), generate_dataset(), _normal_transactions(), DataFrame, Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., Pagamentos a comércios e transferências P2P, em geral dentro do círculo de…, Movimentações comuns das contas fraudulentas, para que não sejam triviais de… (+1 more)

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

### Community 91 - "main"
Cohesion: 0.29
Nodes (8): main(), _metrics(), _plot(), DataFrame, Path, Series, Timedelta, Painéis modelo × métrica; em cada um, conjunto de atributos (e oráculo) ×…

### Community 92 - "main"
Cohesion: 0.25
Nodes (8): main(), _plot(), DataFrame, Path, Series, Escore de um detector não supervisionado (não usa as contas conhecidas)., Matriz método × (cenário, fração conhecida) da AP média., _scores()

### Community 93 - "_fit_sage"
Cohesion: 0.25
Nodes (6): _fit_sage(), _GraphSAGE, ndarray, Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos…, Treina uma GraphSAGE com os rótulos de ``train`` e devolve a probabilidade de…, Tensor

### Community 94 - "test_gnn.py"
Cohesion: 0.25
Nodes (7): fixture, Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")., 300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.…, ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_learns_the_ring_from_structure_alone()

### Community 95 - "oddball_scores"
Cohesion: 0.33
Nodes (7): Egonet e OddBall, egonet_features(), oddball_scores(), DataFrame, Medidas da egonet (a conta, seus vizinhos e as arestas entre eles). *…, Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010). Em redes reais, as…, test_oddball_flags_star()

### Community 96 - "prepare"
Cohesion: 0.33
Nodes (7): prepare(), Prepared, Tudo o que os detectores precisam, calculado uma vez por dataset (ver…, Monta o grafo e calcula todos os atributos (seção ``atributos`` da…, Repete o experimento com várias sementes, uma de cada vez. Cada semente gera um…, run_seeds(), test_run_seeds_one_dataset_per_seed()

### Community 97 - "Diário 2026-09-26"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário 2026-09-26, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 98 - "SimulationConfig"
Cohesion: 0.33
Nodes (5): Parâmetros da simulação (descritos em ``configs/experimento.yaml``)., SimulationConfig, data(), fixture, test_dataset_without_rings_has_only_legit_accounts()

### Community 99 - "Reunião 2026-09-24"
Cohesion: 0.40
Nodes (5): Desde a última reunião, Discussão e decisões, Dúvidas em aberto, Próximos passos, Reunião 2026-09-24

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 101 - "test_app.py"
Cohesion: 0.50
Nodes (3): streamlit_testing_v1, Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver…, test_app_runs_all_tabs()

## Knowledge Gaps
- **323 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Como se orientar`, `Ao editar notas` (+318 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 652 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `pytest`, `communities.py`, `main`, `temporal.py`, `test_online.py`, `test_anomaly.py`, `test_stats.py`, `draw_graph`, `load_scenarios`, `explorer_payload`, `build_graph`, `run_detectors`, `plot_value_matrix`, `build_features`, `temporal_features`, `graph_from_edges`, `compare_runs`, `patterns.py`, `graph_from_csv`, `test_bcb.py`, `propagate_risk`, `generate_dataset`, `oddball_scores`, `prepare`, `SimulationConfig`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `Módulos` to `guia-do-explorador.md`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `generate_dataset()` connect `generate_dataset` to `Módulos`, `test_online.py`, `test_simulation.py`, `load_experiment_config`, `draw_graph`, `load_scenarios`, `load_config`, `plot_value_matrix`, `_animacao`, `experiment.py`, `compare_runs`, `test_scripts.py`, `_random_seconds`, `propagate_risk`, `main`, `main`, `prepare`, `SimulationConfig`, `test_app.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Módulos` (e.g. with `find_pattern()` and `hubs_authorities()`) actually correct?**
  _`Módulos` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _323 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pytest` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `main` be split into smaller, more focused modules?**
  _Cohesion score 0.1471861471861472 - nodes in this community are weakly interconnected._