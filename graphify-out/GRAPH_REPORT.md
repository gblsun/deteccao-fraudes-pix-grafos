# Graph Report - deteccao-fraudes-pix-grafos  (2026-10-01)

## Corpus Check
- 184 files · ~95,384 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .csv 2, .bib 1)

## Summary
- 1617 nodes · 3366 edges · 121 communities (115 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef7d4cc8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- sage_supervised_scores
- algorithms.py
- communities.py
- flow.py
- pandas
- test_docs.py
- external.py
- test_online.py
- Detection
- test_anomaly.py
- test_stats.py
- generate_dataset
- load
- draw_graph
- load_experiment_config
- explorer.py
- network.py
- resultados.md
- main
- test_graph_tools.py
- graph_from_csv
- plot_model_intervals
- prepare
- mapa-da-pesquisa.md
- plot_value_matrix
- test_temporal.py
- mapa-das-leituras.md
- graph_models.py
- experiment.py
- pixfraud
- test_scripts.py
- visualization.py
- pytest
- Graph
- patterns.py
- reproduzir_tudo.py
- Relatório final
- build_features
- _animacao
- Resultados
- anomaly.py
- mapa-dos-testes.md
- test_patterns.py
- simulation.py
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- ilustrar_grafos_de_conhecimento.py
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
- exportar_grafo_de_notas.py
- Instruções para agentes
- Detecção sob camuflagem adversarial
- GNN supervisionada como próximo passo
- Glossário
- Reunião {{date}}
- save_dataset
- Ideias futuras
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- _mean_percentile
- diario-de-pesquisa.md
- Módulos
- Notas da pesquisa no Obsidian
- gerar_relatorio.py
- _fit_sage
- test_gnn.py
- oddball_scores
- test_experiment.py
- Diário 2026-09-26
- Diário 2026-09-29
- known_fraud_scores
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- test_gnn_direcionada.py
- cosine_similarity
- peeling_scores
- Próximos passos
- Diário 2026-09-22
- Reproduzir os resultados
- sage_known_fraud_scores
- Reunião 2026-09-24
- explain_account
- _plot_models
- Diário 2026-09-21
- Reunião 2026-10-01
- IA agêntica para reconhecimento de fraude em tempo real
- _plot
- _DirectedSAGE
- flow_layout
- Configurações
- Reuniões de orientação
- available

## God Nodes (most connected - your core abstractions)
1. `Módulos` - 55 edges
2. `generate_dataset()` - 52 edges
3. `build_graph()` - 27 edges
4. `SimulationConfig` - 27 edges
5. `prepare()` - 21 edges
6. `Detection` - 19 edges
7. `load_experiment_config()` - 19 edges
8. `save_metadata()` - 19 edges
9. `load_config()` - 19 edges
10. `with_overrides()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Outros modelos que caberiam nesta pesquisa` --references--> `Detection`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `1. Preparação dos atributos` --references--> `prepare_matrix()`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Próximo passo` --references--> `densest_subgraph()`  [INFERRED]
  docs/diario/2026-09-22.md → src/pixfraud/communities.py
- `Average precision (AP)` --references--> `evaluate()`  [INFERRED]
  docs/glossario/average-precision.md → src/pixfraud/evaluation.py
- `Pesquisa` --references--> `propagate_risk()`  [INFERRED]
  docs/proximos-passos.md → src/pixfraud/flow.py

## Import Cycles
- None detected.

## Communities (121 total, 6 thin omitted)

### Community 0 - "sage_supervised_scores"
Cohesion: 0.25
Nodes (10): Redes neurais para grafos (GNN), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN), Index, _adjacency(), dominant_scores(), Graph, Escore de anomalia do DOMINANT: erro de reconstrução dos atributos e das…, Probabilidade de fraude fora da amostra, por uma GraphSAGE em validação… (+2 more)

### Community 1 - "algorithms.py"
Cohesion: 0.11
Nodes (25): heapq, itertools, networkx_algorithms, _amounts(), bipartite_projection(), hubs_authorities(), laundering_depth(), longest_chain() (+17 more)

### Community 2 - "communities.py"
Cohesion: 0.15
Nodes (22): Coeficiente de participação, Comunidades e modularidade (Louvain), K-núcleo (core number), community_summary(), core_numbers(), detect_communities(), participation_coefficient(), _power_law_score() (+14 more)

### Community 3 - "flow.py"
Cohesion: 0.17
Nodes (18): Fluxo máximo e corte mínimo, scipy_sparse, _as_list(), blocking_accounts(), blocking_cut(), _flow_network(), max_money_flow(), DiGraph (+10 more)

### Community 4 - "pandas"
Cohesion: 0.23
Nodes (10): Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório:…, matplotlib_animation, networkx, pandas, Cria, resume e salva grafos sem precisar escrever código. O formato de saída…, Gera as ilustrações do README: os padrões de fraude e a animação de uma…, Criação e manipulação dos grafos: contas são vértices e transferências são…, Grafos temporais: caminhos que respeitam a ordem cronológica dos Pix. No grafo… (+2 more)

### Community 5 - "test_docs.py"
Cohesion: 0.15
Nodes (16): ast, O que fiz, Cores do grafo, por tipo de nota, importlib_util, re, parametrize, Testes da documentação: links que funcionam, docstrings, README e mapa em cada…, As pastas do cofre de pesquisa têm uma nota-mapa com nome próprio (não… (+8 more)

### Community 6 - "external.py"
Cohesion: 0.12
Nodes (30): main(), _account(), _account_id(), _accounts_table(), _amlworld_chunk(), load_amlworld(), load_amlworld_patterns(), load_paysim() (+22 more)

### Community 7 - "test_online.py"
Cohesion: 0.08
Nodes (30): DatetimeIndex, Custo operacional, não só AP e precision@k, Grafos heterogêneos, Grafos heterogêneos e custo operacional, Horizonte mais distante: aprendizado federado, _metrics(), _plot(), DataFrame (+22 more)

### Community 8 - "Detection"
Cohesion: 0.16
Nodes (16): Precision@k, Detection, Resultado de um detector: um escore contínuo e um rótulo binário por conta. Os…, evaluate(), DataFrame, Series, ranking_metrics(), Métricas de desempenho dos detectores, calculadas por conta. * ``precision``,… (+8 more)

### Community 9 - "test_anomaly.py"
Cohesion: 0.08
Nodes (39): Explicabilidade para auditoria, O que existe hoje, O que falta, Onde entraria no código, Por que importa para esta pesquisa especificamente, DBSCAN e k-distance, Isolation Forest, Local Outlier Factor (LOF) (+31 more)

### Community 10 - "test_stats.py"
Cohesion: 0.07
Nodes (34): Bootstrap, Correção de Holm, Delta de Cliff ($\delta$), Teste de Mann-Whitney, Teste de Wilcoxon pareado, bootstrap_metric(), cliffs_delta(), compare_groups() (+26 more)

### Community 11 - "generate_dataset"
Cohesion: 0.08
Nodes (25): hashlib, generate_dataset(), _has_look_alikes(), Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., calibrated(), dataset(), fixture, parametrize (+17 more)

### Community 12 - "load"
Cohesion: 0.16
Nodes (18): all_metrics(), explorer_page(), load(), prepared(), DataFrame, Series, Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia. (+10 more)

### Community 13 - "draw_graph"
Cohesion: 0.21
Nodes (15): draw_graph(), _format_amount(), graph_html(), _layout(), _node_colors(), Graph, Path, Cor (hex) de cada vértice e itens de legenda ``{categoria: cor}``. ``color_by``… (+7 more)

### Community 14 - "load_experiment_config"
Cohesion: 0.18
Nodes (32): main(), main(), _evaluate(), main(), Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,…, main(), main(), main() (+24 more)

### Community 15 - "explorer.py"
Cohesion: 0.11
Nodes (27): html, math, community_layout(), explorer_payload(), _first_days(), _free_spot(), network_explorer_html(), _place_center() (+19 more)

### Community 16 - "network.py"
Cohesion: 0.08
Nodes (40): _ccdf(), _degree_graphs(), _measure(), _plot_degrees(), DataFrame, DiGraph, Graph, ndarray (+32 more)

### Community 17 - "resultados.md"
Cohesion: 0.11
Nodes (9): Average precision (AP), Classes raras (desbalanceamento), Conta laranja (conta de passagem), Grafo direcionado ponderado, Intervalo de confiança (IC 95%), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Glossário (+1 more)

### Community 18 - "main"
Cohesion: 0.13
Nodes (18): _convergence(), _draws(), main(), _one_seed(), _paired_needs(), _plot(), DataFrame, Path (+10 more)

### Community 19 - "test_graph_tools.py"
Cohesion: 0.16
Nodes (13): O que fiz, adjacency_matrix(), describe(), DataFrame, Graph, Series, Resumo das propriedades básicas do grafo (útil para conferir exercícios)., Matriz de adjacência rotulada: linha = origem, coluna = destino. Com… (+5 more)

### Community 20 - "graph_from_csv"
Cohesion: 0.16
Nodes (14): MultiDiGraph, _attach_roles(), main(), DiGraph, Path, graph_from_csv(), money_trail(), DiGraph (+6 more)

### Community 21 - "plot_model_intervals"
Cohesion: 0.22
Nodes (13): Axes, format_ci(), format_number(), model_label(), plot_differences(), plot_model_intervals(), Número com vírgula decimal, como no resto da documentação (``0,58``)., Média e intervalo de confiança no formato único dos resultados: ``0,58 [0,52;… (+5 more)

### Community 22 - "prepare"
Cohesion: 0.11
Nodes (21): Random Forest (como teto supervisionado), Validação cruzada estratificada, _evaluate(), _evaluate_star(), Todas as famílias numa semente, avaliadas nas mesmas contas (as que ninguém…, feature_ablation(), prepare(), DataFrame (+13 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.07
Nodes (15): Parâmetros dos experimentos, Cronograma, Ideias futuras, Mapa da pesquisa, Atas de reunião, Trilha de estudos, Convenções, Notebooks da pesquisa (+7 more)

### Community 24 - "plot_value_matrix"
Cohesion: 0.05
Nodes (41): _plot_ablation(), _plot_ceiling(), DataFrame, Path, Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo., Um painel por cenário: conjunto de atributos × modelo, da AP média (tetos…, _plot_effects(), _plot_metric() (+33 more)

### Community 25 - "test_temporal.py"
Cohesion: 0.09
Nodes (30): Caminho temporal, Tempo de permanência (dwell time), _best_hops(), _check_direction(), dwell_time(), DataFrame, DiGraph, Series (+22 more)

### Community 27 - "graph_models.py"
Cohesion: 0.12
Nodes (22): sklearn_decomposition, sklearn_ensemble, sklearn_preprocessing, Rótulo binário dos detectores que só dão escore: a fração ``fraction`` de maior…, _top_fraction(), fraudar(), node2vec_embedding(), node2vec_isolation_forest() (+14 more)

### Community 28 - "experiment.py"
Cohesion: 0.20
Nodes (9): collections_abc, concurrent_futures, importlib_metadata, inspect, platform, scipy, Quantas sementes bastam? Convergência da average precision média. Pedido da…, sklearn_model_selection (+1 more)

### Community 30 - "test_scripts.py"
Cohesion: 0.21
Nodes (20): _check_metadata(), Testes de fumaça dos scripts de avaliação, num dataset minúsculo., O *_meta.json existe e tem o que é preciso para refazer o resultado., _run(), test_avaliar_atributos(), test_avaliar_cenarios(), test_avaliar_deteccao_online(), test_avaliar_externo() (+12 more)

### Community 31 - "visualization.py"
Cohesion: 0.16
Nodes (28): argparse, copy, dataclasses, matplotlib, matplotlib_colors, matplotlib_lines, matplotlib_pyplot, numpy (+20 more)

### Community 32 - "pytest"
Cohesion: 0.15
Nodes (13): pytest, find_pattern(), Ocorrências do formato ``pattern`` dentro de ``graph`` (algoritmo VF2). Cada…, Caminho gargalo: a rota de ``source`` até ``target`` cuja menor aresta é a…, widest_path(), graph_from_edges(), Cria um grafo a partir de uma lista de arestas; prático para exemplos e…, streamlit_testing_v1 (+5 more)

### Community 33 - "Graph"
Cohesion: 0.18
Nodes (17): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), _densest(), densest_subgraph(), fraudar_blocks(), fraudar_scores(), _fraudar_weighted(), Graph (+9 more)

### Community 34 - "patterns.py"
Cohesion: 0.23
Nodes (16): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), fan_in(), fan_out(), inject(), _merge_edge() (+8 more)

### Community 35 - "reproduzir_tudo.py"
Cohesion: 0.12
Nodes (21): csv, datetime, os, abrir(), anotar(), formatar(), graphify(), main() (+13 more)

### Community 36 - "Relatório final"
Cohesion: 0.67
Nodes (3): Como escrever, Estrutura, Relatório final

### Community 37 - "build_features"
Cohesion: 0.07
Nodes (32): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+24 more)

### Community 38 - "_animacao"
Cohesion: 0.25
Nodes (11): _animacao(), quadro(), _legenda(), main(), _padroes(), Path, O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora., Itens de legenda só dos papéis que aparecem no desenho, na ordem de ROLE_COLORS. (+3 more)

### Community 39 - "Resultados"
Cohesion: 0.12
Nodes (16): 10. Redes neurais para grafos (GNN), 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial, 16. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador (+8 more)

### Community 40 - "anomaly.py"
Cohesion: 0.12
Nodes (13): scipy_stats, Gera o explorador interativo da rede inteira (HTML). A página mostra todas as…, sklearn_cluster, sklearn_exceptions, sklearn_kernel_approximation, sklearn_linear_model, sklearn_neighbors, sklearn_neural_network (+5 more)

### Community 41 - "mapa-dos-testes.md"
Cohesion: 0.33
Nodes (4): Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes

### Community 42 - "test_patterns.py"
Cohesion: 0.15
Nodes (15): cycle(), fraud_nodes(), mule_ring(), Graph, Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor)., Ciclo (*round-tripping*): o dinheiro passa por várias contas e volta à primeira., Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.…, parametrize (+7 more)

### Community 43 - "simulation.py"
Cohesion: 0.16
Nodes (15): Gera o dataset sintético de transações PIX. Cada execução sorteia uma semente…, Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.…, secrets, _fraud_ring(), _hops(), _later(), _launder(), _pick_person() (+7 more)

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.07
Nodes (33): collections, io, json, main(), Baixa estatísticas do PIX da API de dados abertos do Banco Central. Exemplos:…, _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo() (+25 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.20
Nodes (6): Explorador interativo, O que tem, Guia do explorador, Como as peças se encaixam, `pixfraud`: o código da pesquisa, Referência completa da API

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.22
Nodes (9): 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), Como as peças se encaixam, Modelos usados na pesquisa (e outros que caberiam) (+1 more)

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
Cohesion: 0.40
Nodes (4): fixture, Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e…, Dois cliques de 5 contas ligados por uma única aresta a4 -> b0., two_cliques()

### Community 72 - "Mapa das leituras"
Cohesion: 0.29
Nodes (7): Aprendizado de máquina e avaliação, Como acrescentar uma leitura, Dados: Pix e datasets públicos, Detecção de anomalias em grafos, Grafos e redes, Mapa das leituras, Trabalhos relacionados: fraude com redes neurais em grafos

### Community 73 - "Resultados"
Cohesion: 0.29
Nodes (7): A comparação entre atributos tabulares e de grafo depende do gerador, Detectar a tempo de bloquear o dinheiro, Perfis de fraude, Poucos rótulos rendem muito, Resultados, Validação do dataset sintético, Validação externa

### Community 74 - "propagate_risk"
Cohesion: 0.22
Nodes (9): Propagação de risco (culpa por associação), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 6. Culpa por associação: usar as contestações que já existem, label_spreading(), propagate_risk(), Series, Culpa por associação: PageRank personalizado a partir das contas ``seeds``. A…, Propagação de rótulos com exemplos positivos **e negativos** (Zhou et al.,… (+1 more)

### Community 75 - "Diário {{date}}"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário {{date}}, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 76 - "Metodologia"
Cohesion: 0.33
Nodes (6): Atributos, Avaliação, Dados, Detectores, Metodologia, Modelagem em grafo

### Community 77 - "exportar_grafo_de_notas.py"
Cohesion: 0.23
Nodes (12): Pattern, como_json(), _filtros_do_cofre(), grafo_de_notas(), main(), notas_do_cofre(), Path, Exporta o grafo de notas do cofre do Obsidian para JSON, para agentes de IA… (+4 more)

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

### Community 83 - "save_dataset"
Cohesion: 0.07
Nodes (35): main(), main(), _accounts_table(), _after_activity(), _amounts(), _camouflage_transactions(), _collector_payouts(), _contestations() (+27 more)

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

### Community 88 - "_mean_percentile"
Cohesion: 0.40
Nodes (5): _mean_percentile(), Series, Combinação de métodos: média dos percentis de cada um, nas contas avaliadas., Escore de um detector não supervisionado (não usa as contas conhecidas)., _scores()

### Community 89 - "diario-de-pesquisa.md"
Cohesion: 0.22
Nodes (4): Diário de pesquisa, Notas, Para que serve, Diário de pesquisa

### Community 90 - "Módulos"
Cohesion: 0.13
Nodes (21): _dataset_pequeno(), Dataset com uma única quadrilha, pequeno o bastante para desenhar., main(), build_graph(), Monta o grafo direcionado de transações. Todas as transferências de um mesmo…, checkpoint_flags(), As ``k`` contas mais suspeitas em cada ponto de corte, para cada conjunto de…, Módulos (+13 more)

### Community 91 - "Notas da pesquisa no Obsidian"
Cohesion: 0.20
Nodes (10): Abrir, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais), Por que nenhuma nota se chama "README", Regras, Rotina (+2 more)

### Community 93 - "_fit_sage"
Cohesion: 0.29
Nodes (6): _fit_sage(), _GraphSAGE, ndarray, Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos…, Treina uma GraphSAGE com os rótulos de ``train`` e devolve a probabilidade de…, Tensor

### Community 94 - "test_gnn.py"
Cohesion: 0.22
Nodes (8): fixture, Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")., 300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.…, ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known(), test_sage_learns_the_ring_from_structure_alone()

### Community 95 - "oddball_scores"
Cohesion: 0.33
Nodes (7): Egonet e OddBall, egonet_features(), oddball_scores(), DataFrame, Medidas da egonet (a conta, seus vizinhos e as arestas entre eles). *…, Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010). Em redes reais, as…, test_oddball_flags_star()

### Community 96 - "test_experiment.py"
Cohesion: 0.13
Nodes (18): Prepared, Repete o experimento com várias sementes. Cada semente gera um dataset…, Tudo o que os detectores precisam, calculado uma vez por dataset (ver…, run_seeds(), _planted(), parametrize, Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários., Contas em que só ``sinal`` separa fraude de normal; ``ruido_*`` não informam… (+10 more)

### Community 97 - "Diário 2026-09-26"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário 2026-09-26, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 98 - "Diário 2026-09-29"
Cohesion: 0.25
Nodes (8): Decisões (e por quê), Diário 2026-09-29, Dúvidas e bloqueios, Integração do branch `local-2026-09-24`, O que fiz, Próximo passo, Quantas sementes usar (conversa de 29/09), Resultados e observações

### Community 99 - "known_fraud_scores"
Cohesion: 0.22
Nodes (9): Decisões (e por quê), Diário 2026-09-28, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive, known_fraud_scores() (+1 more)

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 103 - "cosine_similarity"
Cohesion: 0.50
Nodes (5): cosine_similarity(), Cosseno do ângulo entre os vetores ``a`` e ``b``. $$\\cos\\theta = \\frac{a…, Ângulo entre ``a`` e ``b``: $\\theta = \\arccos(\\cos\\theta)$, em graus (ou…, vector_angle(), test_cosine_similarity_is_the_angle_between_vectors()

### Community 104 - "peeling_scores"
Cohesion: 0.25
Nodes (8): 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), _peel(), peeling_scores(), ndarray, Escore por conta tirado da mesma remoção gulosa do ``densest_subgraph``. O…, Remoção gulosa de Charikar: tira sempre a conta de menor grau ponderado.…, test_peeling_scores_give_each_block_its_own_level(), test_peeling_scores_put_the_dense_block_on_top()

### Community 105 - "Próximos passos"
Cohesion: 0.33
Nodes (6): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório

### Community 106 - "Diário 2026-09-22"
Cohesion: 0.40
Nodes (5): Decisões (e por quê), Diário 2026-09-22, Dúvidas e bloqueios, Próximo passo, Resultados e observações

### Community 107 - "Reproduzir os resultados"
Cohesion: 0.67
Nodes (3): Mapa, Reproduzir os resultados, Scripts

### Community 108 - "sage_known_fraud_scores"
Cohesion: 0.29
Nodes (8): graphsage_scores(), DataFrame, DiGraph, Series, GraphSAGE treinada só com as fraudes **já conhecidas**, como no Pix real. Numa…, Probabilidade de fraude de cada conta dada por uma GraphSAGE treinada com os…, _require_torch(), sage_known_fraud_scores()

### Community 109 - "Reunião 2026-09-24"
Cohesion: 0.29
Nodes (7): Anotações feitas à mão na reunião, Desde a última reunião, Discussão e decisões, Dúvidas em aberto, O que foi feito (29/09), Próximos passos, Reunião 2026-09-24

### Community 110 - "explain_account"
Cohesion: 0.33
Nodes (7): Figure, explain_account(), plot_risk_heatmap(), DataFrame, Series, Heatmap de risco: por que cada conta foi considerada suspeita. As linhas são as…, Ficha da conta: por que ela foi considerada suspeita? * à esquerda, a…

### Community 111 - "_plot_models"
Cohesion: 0.33
Nodes (7): _plot_comparisons(), _plot_models(), DataFrame, Path, Series, Um painel por cenário: cada modelo com a AP média e o IC 95%, agrupados por…, Um painel por cenário: as diferenças pareadas de AP entre modelos.

### Community 112 - "Diário 2026-09-21"
Cohesion: 0.33
Nodes (5): Decisões (e por quê), Diário 2026-09-21, Dúvidas e bloqueios, Próximo passo, Resultados e observações

### Community 113 - "Reunião 2026-10-01"
Cohesion: 0.33
Nodes (6): Desde a última reunião, Discussão e decisões, Dúvidas em aberto, Pendências da reunião anterior, Próximos passos, Reunião 2026-10-01

### Community 114 - "IA agêntica para reconhecimento de fraude em tempo real"
Cohesion: 0.40
Nodes (5): Arquitetura, em linhas gerais, Desafios em aberto, IA agêntica para reconhecimento de fraude em tempo real, O que a ideia acrescentaria, O que existe hoje

### Community 115 - "_plot"
Cohesion: 0.40
Nodes (5): _plot(), DataFrame, Path, model_color(), Cor fixa de um modelo nas figuras (cinza-médio para um modelo sem cor definida).

### Community 116 - "_DirectedSAGE"
Cohesion: 0.40
Nodes (3): _DirectedSAGE(), __init__(), GraphSAGE de 2 camadas com uma convolução para cada sentido do Pix.

### Community 117 - "flow_layout"
Cohesion: 0.40
Nodes (4): flow_layout(), reorder(), DiGraph, Posiciona os vértices da esquerda para a direita, no sentido do dinheiro. Só…

### Community 118 - "Configurações"
Cohesion: 0.67
Nodes (3): Configurações, Criar um cenário, Mudar um parâmetro

### Community 119 - "Reuniões de orientação"
Cohesion: 0.67
Nodes (3): Atas, Como escrever uma ata que ajuda o grafo, Reuniões de orientação

## Knowledge Gaps
- **338 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Como se orientar`, `Ao editar notas` (+333 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 754 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `sage_supervised_scores`, `algorithms.py`, `communities.py`, `flow.py`, `external.py`, `test_online.py`, `Detection`, `test_anomaly.py`, `test_stats.py`, `generate_dataset`, `draw_graph`, `load_experiment_config`, `explorer.py`, `network.py`, `test_graph_tools.py`, `graph_from_csv`, `prepare`, `plot_value_matrix`, `test_temporal.py`, `graph_models.py`, `pytest`, `patterns.py`, `build_features`, `ilustrar_grafos_de_conhecimento.py`, `guia-do-explorador.md`, `propagate_risk`, `oddball_scores`, `test_experiment.py`, `cosine_similarity`, `sage_known_fraud_scores`, `explain_account`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `guia-do-explorador.md` to `Detection`, `Módulos`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `generate_dataset()` connect `generate_dataset` to `simulation.py`, `load`, `load_experiment_config`, `save_dataset`, `prepare`, `Módulos`, `experiment.py`, `test_scripts.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 54 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _338 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `algorithms.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11076923076923077 - nodes in this community are weakly interconnected._
- **Should `communities.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._