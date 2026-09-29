# Graph Report - deteccao-fraudes-pix-grafos  (2026-09-29)

## Corpus Check
- 178 files · ~81,639 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .csv 2, .bib 1)

## Summary
- 1443 nodes · 2952 edges · 104 communities (100 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 153 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3a6b1798`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- gnn.py
- similar_accounts
- detect_communities
- graph_from_csv
- temporal_trail
- test_docs.py
- Módulos
- test_online.py
- Graph
- test_anomaly.py
- summarize_runs
- generate_dataset
- load_experiment_config
- draw_graph
- prepare
- explorer_payload
- network.py
- resultados.md
- main
- main
- test_features.py
- load_config
- run_detectors
- mapa-da-pesquisa.md
- plot_value_matrix
- _animacao
- mapa-das-leituras.md
- prepare_matrix
- temporal_features
- pixfraud
- evaluate
- experiment.py
- test_algorithms.py
- main
- patterns.py
- test_scripts.py
- mapa-do-relatorio.md
- build_features
- ilustrar_grafos_de_conhecimento.py
- Resultados
- ideias-futuras.md
- SimulationConfig
- test_patterns.py
- _after_activity
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
- bootstrap_metric
- Instruções para agentes
- Detecção sob camuflagem adversarial
- GNN supervisionada como próximo passo
- Glossário
- Reunião {{date}}
- DataFrame
- Ideias futuras
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- build_graph
- Diário de pesquisa
- Reuniões de orientação
- main
- Detection
- _GraphSAGE
- test_gnn.py
- oddball_scores
- run_seeds
- Diário 2026-09-26
- hubs_authorities
- Reunião 2026-09-24
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- Diário 2026-09-28
- cosine_similarity

## God Nodes (most connected - your core abstractions)
1. `Módulos` - 49 edges
2. `generate_dataset()` - 38 edges
3. `build_graph()` - 25 edges
4. `SimulationConfig` - 21 edges
5. `prepare()` - 19 edges
6. `load_experiment_config()` - 18 edges
7. `save_metadata()` - 18 edges
8. `load_config()` - 18 edges
9. `load_scenarios()` - 17 edges
10. `with_overrides()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Próximo passo` --references--> `densest_subgraph()`  [INFERRED]
  docs/diario/2026-09-22.md → src/pixfraud/communities.py
- `6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)` --references--> `propagate_risk()`  [INFERRED]
  docs/modelos.md → src/pixfraud/flow.py
- `O que foi feito (29/09)` --references--> `build_graph()`  [INFERRED]
  docs/reunioes/2026-09-24.md → src/pixfraud/graph.py
- `Outros modelos que caberiam nesta pesquisa` --references--> `Detection`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Onde entraria no código` --references--> `prepare_matrix()`  [INFERRED]
  docs/futuro/explicabilidade-para-auditoria.md → src/pixfraud/anomaly.py

## Import Cycles
- None detected.

## Communities (104 total, 4 thin omitted)

### Community 0 - "gnn.py"
Cohesion: 0.15
Nodes (21): Redes neurais para grafos (GNN), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN), Index, sklearn_model_selection, _adjacency(), dominant_scores(), _fit_sage(), DataFrame (+13 more)

### Community 1 - "similar_accounts"
Cohesion: 0.18
Nodes (14): _amounts(), laundering_depth(), longest_chain(), money_backbone(), DiGraph, Series, Contas mais parecidas com ``account`` pela vizinhança. * ``"jaccard_out"``:…, Vetor dos valores entre ``account`` e cada conta de ``partners`` (0 se não… (+6 more)

### Community 2 - "detect_communities"
Cohesion: 0.13
Nodes (22): Coeficiente de participação, Comunidades e modularidade (Louvain), K-núcleo (core number), community_summary(), core_numbers(), detect_communities(), participation_coefficient(), _power_law_score() (+14 more)

### Community 3 - "graph_from_csv"
Cohesion: 0.06
Nodes (47): Decisões (e por quê), Diário 2026-09-21, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Fluxo máximo e corte mínimo, MultiDiGraph (+39 more)

### Community 4 - "temporal_trail"
Cohesion: 0.20
Nodes (11): Caminho temporal, _best_hops(), DiGraph, Timedelta, Timestamp, Menor nº de saltos entre os eventos compatíveis com um Pix no instante ``t``., Os Pix que formam caminhos temporais a partir de ``account`` (ou até ela). Além…, Grafo (agregado) dos Pix de ``temporal_trail_transactions``; aceita os mesmos… (+3 more)

### Community 5 - "test_docs.py"
Cohesion: 0.06
Nodes (43): ast, Decisões (e por quê), Diário 2026-09-22, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Abrir (+35 more)

### Community 6 - "Módulos"
Cohesion: 0.11
Nodes (32): main(), Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.…, _account(), _account_id(), _accounts_table(), _amlworld_chunk(), load_amlworld(), load_amlworld_patterns() (+24 more)

### Community 7 - "test_online.py"
Cohesion: 0.08
Nodes (25): Explicabilidade para auditoria, O que existe hoje, O que falta, Onde entraria no código, Por que importa para esta pesquisa especificamente, Custo operacional, não só AP e precision@k, Grafos heterogêneos, Grafos heterogêneos e custo operacional (+17 more)

### Community 8 - "Graph"
Cohesion: 0.22
Nodes (15): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), densest_subgraph(), fraudar_blocks(), fraudar_scores(), _peel(), Graph, Subgrafo de maior densidade (peso total / nº de contas), pelo algoritmo guloso… (+7 more)

### Community 9 - "test_anomaly.py"
Cohesion: 0.16
Nodes (14): DBSCAN e k-distance, Isolation Forest, dbscan(), isolation_forest(), Isolation Forest: contas isoladas com poucas partições aleatórias são anômalas., DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.…, blob_with_outlier(), fixture (+6 more)

### Community 10 - "summarize_runs"
Cohesion: 0.08
Nodes (31): Correção de Holm, Delta de Cliff ($\delta$), Intervalo de confiança (IC 95%), Teste de Mann-Whitney, Teste de Wilcoxon pareado, _evaluate(), main(), Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,… (+23 more)

### Community 11 - "generate_dataset"
Cohesion: 0.14
Nodes (15): generate_dataset(), Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., dataset(), fixture, parametrize, Testes de `pixfraud.simulation`: reprodutibilidade, rótulos e parâmetros de…, test_collector_cashout_empties_the_collector(), test_collector_cashout_off_by_default_keeps_dataset() (+7 more)

### Community 12 - "load_experiment_config"
Cohesion: 0.16
Nodes (18): all_metrics(), explorer_page(), prepared(), DataFrame, Series, Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Grafo, atributos e rótulos, calculados uma vez e guardados entre as interações., Escore de risco de cada conta para o detector e o conjunto escolhidos na barra… (+10 more)

### Community 13 - "draw_graph"
Cohesion: 0.09
Nodes (30): Axes, Figure, draw_graph(), explain_account(), flow_layout(), reorder(), _format_amount(), graph_html() (+22 more)

### Community 14 - "prepare"
Cohesion: 0.09
Nodes (29): main(), _plot(), DataFrame, Path, Matriz método × cenário da AP média., main(), _plot(), DataFrame (+21 more)

### Community 15 - "explorer_payload"
Cohesion: 0.12
Nodes (24): main(), community_layout(), explorer_payload(), _first_days(), _free_spot(), network_explorer_html(), _place_center(), DataFrame (+16 more)

### Community 16 - "network.py"
Cohesion: 0.07
Nodes (41): _ccdf(), _degree_graphs(), main(), _measure(), _plot_degrees(), DataFrame, DiGraph, Graph (+33 more)

### Community 17 - "resultados.md"
Cohesion: 0.13
Nodes (6): Classes raras (desbalanceamento), Conta laranja (conta de passagem), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Glossário, ROC-AUC

### Community 18 - "main"
Cohesion: 0.17
Nodes (14): _convergence(), _draws(), main(), _one_seed(), _plot(), DataFrame, Path, Roda uma semente (em outro processo, com ``--processos`` > 1). (+6 more)

### Community 19 - "main"
Cohesion: 0.33
Nodes (7): main(), _plot_typologies(), _pool(), DataFrame, Path, Junta as janelas: acertos somados sobre contas somadas, por tipologia,…, Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo.

### Community 20 - "test_features.py"
Cohesion: 0.29
Nodes (6): chain(), fixture, Testes de `pixfraud.features`: cada atributo conferido à mão num grafo pequeno., Cadeia A -> B -> C -> D, um pagamento extra E -> B e uma conta F sem transações., test_features(), test_graph_aggregates_repeated_pairs()

### Community 21 - "load_config"
Cohesion: 0.21
Nodes (12): load(), Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia., main(), main(), load_config(), load_dataset(), Path, Grava ``accounts.csv`` e ``transactions.csv`` em ``out_dir`` (criada se não… (+4 more)

### Community 22 - "run_detectors"
Cohesion: 0.13
Nodes (19): O que fiz, Random Forest (como teto supervisionado), Validação cruzada estratificada, 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive, feature_ablation(), known_fraud_scores(), DataFrame, Series (+11 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.09
Nodes (13): Configurações, Criar um cenário, Mudar um parâmetro, Parâmetros dos experimentos, Cronograma, Diário de pesquisa, Mapa da pesquisa, Atas de reunião (+5 more)

### Community 24 - "plot_value_matrix"
Cohesion: 0.12
Nodes (21): main(), _plot_ablation(), _plot_ceiling(), DataFrame, Path, Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo., Matriz conjunto × (cenário, modelo) da AP média, com o Random Forest…, _plot_effects() (+13 more)

### Community 25 - "_animacao"
Cohesion: 0.22
Nodes (13): _animacao(), quadro(), _dataset_pequeno(), _legenda(), main(), _padroes(), Path, O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora. (+5 more)

### Community 27 - "prepare_matrix"
Cohesion: 0.22
Nodes (10): Local Outlier Factor (LOF), 1. Preparação dos atributos, local_outlier_factor(), prepare_matrix(), DataFrame, ndarray, Local Outlier Factor: compara a densidade da conta com a dos seus vizinhos.…, Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza… (+2 more)

### Community 28 - "temporal_features"
Cohesion: 0.24
Nodes (11): Tempo de permanência (dwell time), dwell_time(), DataFrame, Series, Tempo de permanência do dinheiro, em minutos, por conta. Para cada Pix…, Grau de entrada por janela de tempo: linhas = janelas, colunas = contas. Cada…, Atributos temporais por conta: ``dwell_time_min`` e ``max_daily_in_degree``.…, temporal_features() (+3 more)

### Community 30 - "evaluate"
Cohesion: 0.25
Nodes (9): Average precision (AP), Precision@k, evaluate(), DataFrame, Series, Todas as métricas do módulo para uma detecção; ``k`` padrão = nº de fraudes…, Fração das contas de cada grupo que está entre as ``k`` de maior escore.…, recall_by_group() (+1 more)

### Community 31 - "experiment.py"
Cohesion: 0.05
Nodes (84): Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório:…, argparse, collections_abc, concurrent_futures, copy, dataclasses, heapq, html (+76 more)

### Community 32 - "test_algorithms.py"
Cohesion: 0.20
Nodes (11): math, find_pattern(), Ocorrências do formato ``pattern`` dentro de ``graph`` (algoritmo VF2). Cada…, Caminho gargalo: a rota de ``source`` até ``target`` cuja menor aresta é a…, widest_path(), graph_from_edges(), Cria um grafo a partir de uma lista de arestas; prático para exemplos e…, Testes de `pixfraud.algorithms`: caminho gargalo, ramificação máxima, VF2, HITS… (+3 more)

### Community 33 - "main"
Cohesion: 0.40
Nodes (5): main(), _plot(), DataFrame, Path, Matriz método × cenário da AP média.

### Community 34 - "patterns.py"
Cohesion: 0.19
Nodes (19): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), cycle(), fan_in(), fan_out(), inject() (+11 more)

### Community 35 - "test_scripts.py"
Cohesion: 0.08
Nodes (43): csv, datetime, os, Mapa, Reproduzir os resultados, Scripts, abrir(), anotar() (+35 more)

### Community 36 - "mapa-do-relatorio.md"
Cohesion: 0.14
Nodes (7): Resumo {.unnumbered}, Introdução, Fundamentação teórica, Como escrever, Estrutura, Relatório final, Mapa do relatório

### Community 37 - "build_features"
Cohesion: 0.09
Nodes (26): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+18 more)

### Community 38 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.22
Nodes (13): collections, _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), Path (+5 more)

### Community 39 - "Resultados"
Cohesion: 0.14
Nodes (14): 10. Redes neurais para grafos (GNN), 12. Cuidados na interpretação, 13. Conclusão parcial, 14. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador, 3. O gerador comparado com o Pix real, 4. Perfis: o que distingue cada papel, e quem os detectores encontram (+6 more)

### Community 41 - "SimulationConfig"
Cohesion: 0.13
Nodes (11): Parâmetros da simulação (descritos em ``configs/experimento.yaml``)., SimulationConfig, streamlit_testing_v1, Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes, Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver… (+3 more)

### Community 42 - "test_patterns.py"
Cohesion: 0.18
Nodes (12): fraud_nodes(), mule_ring(), Graph, Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor)., Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.…, parametrize, Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num…, test_chain_loses_fee_at_each_hop() (+4 more)

### Community 43 - "_after_activity"
Cohesion: 0.22
Nodes (9): _after_activity(), _collector_cashout(), _fraud_ring(), _launder(), Instante em que ``delay`` segundos de atividade terão passado a partir de…, Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora., Repassa o valor ao longo de ``path``, retendo uma pequena comissão a cada salto., A coletora esvazia o que recebeu: vários Pix de saída para pessoas e comércios.… (+1 more)

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "test_bcb.py"
Cohesion: 0.11
Nodes (19): io, main(), fetch(), DataFrame, Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. Os…, Baixa um recurso da API em uma única requisição. ``resource`` é um apelido de…, Detecção de fraudes em transações PIX com teoria dos grafos e machine learning., _http() (+11 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.29
Nodes (3): Explorador interativo, O que tem, Guia do explorador

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.25
Nodes (8): 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), Como as peças se encaixam, Modelos usados na pesquisa (e outros que caberiam)

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
Cohesion: 0.33
Nodes (5): fixture, Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e…, Dois cliques de 5 contas ligados por uma única aresta a4 -> b0., test_densest_subgraph_finds_planted_clique(), two_cliques()

### Community 72 - "Mapa das leituras"
Cohesion: 0.29
Nodes (7): Aprendizado de máquina e avaliação, Como acrescentar uma leitura, Dados: Pix e datasets públicos, Detecção de anomalias em grafos, Grafos e redes, Mapa das leituras, Trabalhos relacionados: fraude com redes neurais em grafos

### Community 73 - "Resultados"
Cohesion: 0.29
Nodes (7): A comparação entre atributos tabulares e de grafo depende do gerador, Detectar a tempo de bloquear o dinheiro, Perfis de fraude, Poucos rótulos rendem muito, Resultados, Validação do dataset sintético, Validação externa

### Community 74 - "propagate_risk"
Cohesion: 0.18
Nodes (11): Propagação de risco (culpa por associação), Dados, Para a próxima reunião, Pesquisa, Próximos passos, Repositório, 6. Culpa por associação: usar as contestações que já existem, propagate_risk() (+3 more)

### Community 75 - "Diário {{date}}"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário {{date}}, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 76 - "Metodologia"
Cohesion: 0.33
Nodes (6): Atributos, Avaliação, Dados, Detectores, Metodologia, Modelagem em grafo

### Community 77 - "bootstrap_metric"
Cohesion: 0.25
Nodes (8): Bootstrap, bootstrap_metric(), contingency_test(), Series, Estimativa pontual e IC por bootstrap percentil de uma métrica de desempenho.…, Teste qui-quadrado de independência entre duas variáveis categóricas, com o V…, test_bootstrap_metric_perfect_ranking(), test_contingency_test()

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

### Community 83 - "DataFrame"
Cohesion: 0.25
Nodes (9): _accounts_table(), _camouflage_transactions(), _normal_transactions(), DataFrame, ndarray, _random_seconds(), Instantes (em segundos desde o início) seguindo o perfil horário…, Pagamentos a comércios e transferências P2P, em geral dentro do círculo de… (+1 more)

### Community 84 - "Ideias futuras"
Cohesion: 0.50
Nodes (4): Como acrescentar uma ideia, Do autor da pesquisa, Ideias futuras, Outras ideias

### Community 85 - "Documentação da pesquisa"
Cohesion: 0.50
Nodes (4): A pesquisa, Anotações, Documentação da pesquisa, Documentação do código e dos dados

### Community 86 - "A rede Pix dentro do cofre"
Cohesion: 0.50
Nodes (4): A rede Pix dentro do cofre, Como gerar outros recortes, Figuras estáticas, Rede inteira, interativa

### Community 87 - "Revisão bibliográfica"
Cohesion: 0.50
Nodes (4): Como fichar uma leitura, Fichamentos, Revisão bibliográfica, Sugestões de leitura

### Community 88 - "build_graph"
Cohesion: 0.29
Nodes (8): Grafo direcionado ponderado, build_graph(), Monta o grafo direcionado de transações. Todas as transferências de um mesmo…, _check_direction(), Contas ligadas a ``account`` por caminhos temporais. * ``direction="forward"``…, temporal_reachability(), test_backward_reachability_respects_time(), test_forward_reachability_gives_earliest_arrival()

### Community 89 - "Diário de pesquisa"
Cohesion: 0.67
Nodes (3): Diário de pesquisa, Notas, Para que serve

### Community 90 - "Reuniões de orientação"
Cohesion: 0.67
Nodes (3): Atas, Como escrever uma ata que ajuda o grafo, Reuniões de orientação

### Community 91 - "main"
Cohesion: 0.13
Nodes (19): DatetimeIndex, main(), _metrics(), _plot(), DataFrame, Path, Series, Timedelta (+11 more)

### Community 92 - "Detection"
Cohesion: 0.29
Nodes (7): Outros modelos que caberiam nesta pesquisa, Detection, Resultado de um detector: um escore contínuo e um rótulo binário por conta. Os…, Como as peças se encaixam, Onde mexer para..., `pixfraud`: o código da pesquisa, Referência completa da API

### Community 93 - "_GraphSAGE"
Cohesion: 0.40
Nodes (3): _GraphSAGE, Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos…, Tensor

### Community 94 - "test_gnn.py"
Cohesion: 0.22
Nodes (8): fixture, Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")., 300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.…, ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known(), test_sage_learns_the_ring_from_structure_alone()

### Community 95 - "oddball_scores"
Cohesion: 0.33
Nodes (7): Egonet e OddBall, egonet_features(), oddball_scores(), DataFrame, Medidas da egonet (a conta, seus vizinhos e as arestas entre eles). *…, Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010). Em redes reais, as…, test_oddball_flags_star()

### Community 96 - "run_seeds"
Cohesion: 0.40
Nodes (5): Prepared, Tudo o que os detectores precisam, calculado uma vez por dataset (ver…, Repete o experimento com várias sementes, uma de cada vez. Cada semente gera um…, run_seeds(), test_run_seeds_one_dataset_per_seed()

### Community 97 - "Diário 2026-09-26"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário 2026-09-26, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 98 - "hubs_authorities"
Cohesion: 0.29
Nodes (7): bipartite_projection(), hubs_authorities(), DataFrame, Graph, HITS (Kleinberg): *hubs* apontam para boas autoridades; *autoridades* recebem…, Projeção do grafo bipartido ``left`` × ``right`` sobre ``left``. Duas contas de…, test_hits_similarity_and_projection()

### Community 99 - "Reunião 2026-09-24"
Cohesion: 0.29
Nodes (7): Anotações feitas à mão na reunião, Desde a última reunião, Discussão e decisões, Dúvidas em aberto, O que foi feito (29/09), Próximos passos, Reunião 2026-09-24

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 101 - "Diário 2026-09-28"
Cohesion: 0.40
Nodes (5): Decisões (e por quê), Diário 2026-09-28, Dúvidas e bloqueios, Próximo passo, Resultados e observações

### Community 103 - "cosine_similarity"
Cohesion: 0.50
Nodes (5): cosine_similarity(), Cosseno do ângulo entre os vetores ``a`` e ``b``. $$\\cos\\theta = \\frac{a…, Ângulo entre ``a`` e ``b``: $\\theta = \\arccos(\\cos\\theta)$, em graus (ou…, vector_angle(), test_cosine_similarity_is_the_angle_between_vectors()

## Knowledge Gaps
- **326 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Como se orientar`, `Ao editar notas` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 684 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `similar_accounts`, `detect_communities`, `graph_from_csv`, `temporal_trail`, `test_online.py`, `test_anomaly.py`, `summarize_runs`, `generate_dataset`, `draw_graph`, `prepare`, `explorer_payload`, `network.py`, `run_detectors`, `plot_value_matrix`, `temporal_features`, `evaluate`, `test_algorithms.py`, `patterns.py`, `build_features`, `SimulationConfig`, `test_bcb.py`, `propagate_risk`, `build_graph`, `Detection`, `oddball_scores`, `run_seeds`, `hubs_authorities`, `cosine_similarity`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `Detection` to `Módulos`, `guia-do-explorador.md`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `build_graph()` connect `build_graph` to `Reunião 2026-09-24`, `graph_from_csv`, `temporal_trail`, `Módulos`, `SimulationConfig`, `propagate_risk`, `draw_graph`, `prepare`, `network.py`, `test_features.py`, `_animacao`, `experiment.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 48 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `detect_communities` be split into smaller, more focused modules?**
  _Cohesion score 0.12987012987012986 - nodes in this community are weakly interconnected._
- **Should `graph_from_csv` be split into smaller, more focused modules?**
  _Cohesion score 0.05647058823529412 - nodes in this community are weakly interconnected._