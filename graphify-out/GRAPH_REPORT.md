# Graph Report - deteccao-fraudes-pix-grafos  (2026-10-12)

## Corpus Check
- 274 files · ~154,540 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .bib 1)

## Summary
- 2330 nodes · 5440 edges · 132 communities (129 shown, 3 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 841 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9fa5497d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- audit_roles
- algorithms.py
- test_scripts.py
- flow.py
- recovered_amount
- test_explorer.py
- external.py
- test_docs.py
- _plot_models
- one_class_svm
- permutation_test_metric
- generate_dataset
- rank_models
- draw_graph
- with_overrides
- autoencoder
- test_network.py
- glossario.md
- _run
- describe
- buscar.py
- random_forest_known_fraud_scores
- Classes e funções
- mapa-da-pesquisa.md
- _plot_roles
- temporal.py
- communities.py
- models/README.md
- fraudar_scores
- pixfraud
- plot_heat_graph
- simulation.py
- Testes
- tuning/__init__.py
- cycle
- contingency_test
- label_spreading
- build_features
- graph_from_csv
- test_experiment.py
- fluxo-da-pesquisa.md
- build_graph
- test_patterns.py
- test_algorithms.py
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- test_bcb.py
- guia-do-explorador.md
- Modelos usados na pesquisa (e outros que caberiam)
- plot_test_statistic
- Detection
- mapa-do-codigo.md
- holm_correction
- gnn.py
- Fluxo da pesquisa
- test_stats.py
- documentar_codigo.py
- unsupervised/__init__.py
- main
- _mean_percentile
- ecod
- _plot
- `pixfraud.algorithms`
- Modelos
- `pixfraud.stats`
- pandas
- _profile
- _plot_share
- visualization.py
- null_model_test
- reproduzir_tudo.py
- average-precision.md
- _attach_roles
- evaluate
- explorador.py
- experiment.py
- Param
- gradient_boosting_scores
- Instruções para agentes
- Resultados
- ilustrar_grafos_de_conhecimento.py
- Glossário
- compare_groups
- _look_alike_transactions
- exportar_grafo_de_notas.py
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- test_graph_models.py
- `scripts/04_avaliacao/`
- fit_sage
- isolation_forest
- candidates
- exploration.py
- prepare_matrix
- out_of_fold_scores
- Módulos
- dominant_scores
- choose
- test_flow.py
- adjacency
- SimulationConfig
- test_anomaly.py
- test_buscar.py
- test_gnn.py
- test_online.py
- test_tuning.py
- bcb.py
- Mapa
- fetch
- fraudar
- plot_value_matrix
- friedman_models
- test_features.py
- _metrics
- features.py
- load_search_spaces
- _plot_metric
- Próximos passos
- main
- _plot_typologies
- _plot
- Classes e funções
- bootstrap_metric
- [`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py)
- _plot
- _plot
- _plot
- cross_validation.py
- Configurações
- `pixfraud.patterns`

## God Nodes (most connected - your core abstractions)
1. `generate_dataset()` - 68 edges
2. `Módulos` - 57 edges
3. `Detection` - 39 edges
4. `prepare_matrix()` - 35 edges
5. `SimulationConfig` - 34 edges
6. `[`test_simulation.py`](../../tests/test_simulation.py)` - 31 edges
7. `prepare()` - 30 edges
8. `build_graph()` - 30 edges
9. `with_overrides()` - 29 edges
10. `Testes` - 28 edges

## Surprising Connections (you probably didn't know these)
- ``fraudar_blocks` (função)` --references--> `fraudar_blocks()`  [INFERRED]
  docs/codigo/pixfraud.communities.md → src/pixfraud/communities.py
- ``fraudar_scores` (função)` --references--> `fraudar_scores()`  [INFERRED]
  docs/codigo/pixfraud.communities.md → src/pixfraud/communities.py
- ``model_scores` (função)` --references--> `Prepared`  [INFERRED]
  docs/codigo/pixfraud.tuning.search.md → src/pixfraud/experiment.py
- ``load_experiment_config` (função)` --references--> `load_experiment_config()`  [INFERRED]
  docs/codigo/pixfraud.experiment.md → src/pixfraud/experiment.py
- ``load_scenarios` (função)` --references--> `load_scenarios()`  [INFERRED]
  docs/codigo/pixfraud.experiment.md → src/pixfraud/experiment.py

## Import Cycles
- 4-file cycle: `src/pixfraud/models/__init__.py -> src/pixfraud/models/unsupervised/__init__.py -> src/pixfraud/models/unsupervised/neural/__init__.py -> src/pixfraud/models/unsupervised/neural/dominant.py -> src/pixfraud/models/__init__.py`

## Communities (132 total, 3 thin omitted)

### Community 0 - "audit_roles"
Cohesion: 0.06
Nodes (40): `audit_roles` (função), Classes e funções, `draw_structure` (função), Funções internas, `generate_dataset` (função), `load_config` (função), `load_dataset` (função), `pixfraud.simulation` (+32 more)

### Community 1 - "algorithms.py"
Cohesion: 0.15
Nodes (17): `laundering_depth` (função), `longest_chain` (função), heapq, itertools, networkx_algorithms, _amounts(), laundering_depth(), longest_chain() (+9 more)

### Community 2 - "test_scripts.py"
Cohesion: 0.21
Nodes (28): [`test_scripts.py`](../../tests/test_scripts.py), _check_metadata(), Testes de fumaça dos scripts de avaliação, num dataset minúsculo., O *_meta.json existe e tem o que é preciso para refazer o resultado., _require_torch(), _run(), test_auditar_papeis(), test_avaliar_atributos() (+20 more)

### Community 3 - "flow.py"
Cohesion: 0.13
Nodes (25): `blocking_accounts` (função), `blocking_cut` (função), Classes e funções, Funções internas, `max_money_flow` (função), `pixfraud.flow`, Quem usa este módulo, `relevant_accounts` (função) (+17 more)

### Community 4 - "recovered_amount"
Cohesion: 0.14
Nodes (19): DatetimeIndex, `checkpoint_flags` (função), Classes e funções, `exposure_times` (função), `first_flags` (função), `pixfraud.online`, Quem usa este módulo, `recovered_amount` (função) (+11 more)

### Community 5 - "test_explorer.py"
Cohesion: 0.09
Nodes (34): Classes e funções, `community_layout` (função), `explorer_payload` (função), Funções internas, `network_explorer_html` (função), `pixfraud.explorer`, Quem usa este módulo, `save_network_explorer` (função) (+26 more)

### Community 6 - "external.py"
Cohesion: 0.08
Nodes (43): Classes e funções, `load_amlworld` (função), `load_paysim` (função), `pattern_accounts` (função), `pixfraud.external`, Quem usa este módulo, `time_windows` (função), [`test_external.py`](../../tests/test_external.py) (+35 more)

### Community 7 - "test_docs.py"
Cohesion: 0.10
Nodes (29): [`test_docs.py`](../../tests/test_docs.py), Abrir, Busca única nos dois grafos, Cores do grafo, por tipo de nota, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais) (+21 more)

### Community 8 - "_plot_models"
Cohesion: 0.22
Nodes (11): _chance_table(), _plot_comparisons(), _plot_critical_difference(), _plot_models(), DataFrame, Path, Series, Por (cenário, modelo): em quantas sementes o modelo foi melhor que o acaso, e a… (+3 more)

### Community 9 - "one_class_svm"
Cohesion: 0.14
Nodes (14): Classes e funções, `one_class_svm` (função), `pixfraud.models.unsupervised.boundary.one_class_svm`, Quem usa este módulo, `pixfraud.models.unsupervised.boundary`, Quem usa este módulo, sklearn_kernel_approximation, sklearn_linear_model (+6 more)

### Community 10 - "permutation_test_metric"
Cohesion: 0.19
Nodes (13): `permutation_test_metric` (função), `topk_hypergeom` (função), Teste de permutação, O modelo é melhor que o acaso?, Testes de hipótese para classificadores, Um modelo é melhor que outro?, "É comércio ou não?", permutation_test_metric() (+5 more)

### Community 11 - "generate_dataset"
Cohesion: 0.10
Nodes (42): [`test_simulation.py`](../../tests/test_simulation.py), hashlib, generate_dataset(), _has_look_alikes(), Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., O cenário tem contas legítimas parecidas com fraude (salários, vaquinhas,…, calibrated(), dataset() (+34 more)

### Community 12 - "rank_models"
Cohesion: 0.08
Nodes (36): explorer_page(), network_title(), Legenda da rede escolhida: o dataset salvo ou semente, cenário e…, HTML da aba "Rede inteira", com todos os modelos no seletor e o escolhido já…, cache_data, `all_model_scores` (função), Classes e funções, `generate_network` (função) (+28 more)

### Community 13 - "draw_graph"
Cohesion: 0.13
Nodes (24): Funções internas, `graph_html` (função), `pixfraud.visualization`, Quem usa este módulo, `save_graph` (função), `to_html` (função), draw_graph(), _format_amount() (+16 more)

### Community 14 - "with_overrides"
Cohesion: 0.07
Nodes (66): model_scores(), network(), Contas, Pix e a rede preparada: gerada (semente + cenário) ou lida do dataset…, Escores de todos os modelos e a tabela com a nota de cada um., cache_resource, `epsilon_squared_label` (função), main(), Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a… (+58 more)

### Community 15 - "autoencoder"
Cohesion: 0.25
Nodes (9): `autoencoder` (função), Classes e funções, `pixfraud.models.unsupervised.neural.autoencoder`, Quem usa este módulo, `pixfraud.models.unsupervised.neural`, Quem usa este módulo, autoencoder(), DataFrame (+1 more)

### Community 16 - "test_network.py"
Cohesion: 0.06
Nodes (57): Classes e funções, `compare_network_models` (função), `component_summary` (função), `degree_sequence` (função), `fit_power_law` (função), Funções internas, `giant_component` (função), `pixfraud.network` (+49 more)

### Community 17 - "glossario.md"
Cohesion: 0.14
Nodes (10): Conta laranja (conta de passagem), DBSCAN e k-distance, Isolation Forest, K-Means, Local Outlier Factor (LOF), MED (Mecanismo Especial de Devolução), PCA (análise de componentes principais), Propagação de risco (culpa por associação) (+2 more)

### Community 18 - "_run"
Cohesion: 0.14
Nodes (14): _draws(), _one_seed(), _paired_needs(), _plot(), DataFrame, Path, Diferença pareada média de cada comparação e o nº de sementes para detectá-la.…, Menor nº de sementes para um teste t pareado detectar o efeito padronizado… (+6 more)

### Community 19 - "describe"
Cohesion: 0.14
Nodes (15): `adjacency_matrix` (função), `build_graph` (função), Classes e funções, `describe` (função), `graph_from_csv` (função), `graph_from_edges` (função), `pixfraud.graph`, Quem usa este módulo (+7 more)

### Community 20 - "buscar.py"
Cohesion: 0.11
Nodes (25): importlib_util, buscar_codigo(), buscar_notas(), _carregar_exportador(), _casa(), codigo_citado(), grafo_velho(), _lista() (+17 more)

### Community 21 - "random_forest_known_fraud_scores"
Cohesion: 0.16
Nodes (18): Classes e funções, `make_random_forest` (função), `pixfraud.models.supervised.trees.random_forest`, Quem usa este módulo, `random_forest_known_fraud_scores` (função), `random_forest_scores` (função), RandomForestClassifier, known_fraud_out_of_fold() (+10 more)

### Community 22 - "Classes e funções"
Cohesion: 0.15
Nodes (19): Classes e funções, `draw_graph` (função), `format_ci` (função), `format_number` (função), `model_label` (função), `plot_differences` (função), `plot_model_intervals` (função), `plot_value_matrix` (função) (+11 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.08
Nodes (15): Parâmetros dos experimentos, Diretórios, Cronograma, Mapa da pesquisa, Trilha de estudos, Convenções, Notebooks da pesquisa, Mapa dos notebooks (+7 more)

### Community 24 - "_plot_roles"
Cohesion: 0.22
Nodes (9): categorical_variables(), _plot_roles(), DataFrame, Path, Series, Variáveis sim/não de cada conta, para cruzar com o gabarito., Por (cenário, atributo): efeito médio, IC 95% t entre as sementes e em quantas…, Matriz atributo × cenário do ε² médio do Kruskal-Wallis entre os papéis. (+1 more)

### Community 25 - "temporal.py"
Cohesion: 0.07
Nodes (44): Funções internas, Classes e funções, `dwell_time` (função), Funções internas, `pixfraud.temporal`, Quem usa este módulo, `temporal_features` (função), `temporal_reachability` (função) (+36 more)

### Community 26 - "communities.py"
Cohesion: 0.07
Nodes (55): Classes e funções, `community_summary` (função), `core_numbers` (função), `densest_subgraph` (função), `detect_communities` (função), `egonet_features` (função), `fraudar_blocks` (função), `fraudar_scores` (função) (+47 more)

### Community 28 - "fraudar_scores"
Cohesion: 0.14
Nodes (21): [`avaliar_fraudar.py`](../../scripts/04_avaliacao/avaliar_fraudar.py), [`test_communities.py`](../../tests/test_communities.py), FRAUDAR, 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), fraudar_blocks(), fraudar_scores(), Blocos densos um depois do outro, como no FRAUDAR (Hooi et al., 2016). Acha o… (+13 more)

### Community 30 - "plot_heat_graph"
Cohesion: 0.12
Nodes (19): `explain_account` (função), `flow_layout` (função), `plot_heat_graph` (função), `plot_risk_heatmap` (função), [`test_pipeline.py`](../../tests/test_pipeline.py), Figure, explain_account(), flow_layout() (+11 more)

### Community 31 - "simulation.py"
Cohesion: 0.15
Nodes (18): argparse, copy, dataclasses, pathlib, O papel de cada conta corresponde ao que ela fez? (reunião de 01/10) Confere,…, Baixa estatísticas do PIX da API de dados abertos do Banco Central. Exemplos:…, Gera o dataset sintético de transações PIX. Cada execução sorteia uma semente…, Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.… (+10 more)

### Community 32 - "Testes"
Cohesion: 0.29
Nodes (7): [`test_app.py`](../../tests/test_app.py), Testes, pytest, streamlit_testing_v1, Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver…, test_app_runs_all_tabs_with_the_saved_dataset(), test_typed_seed_generates_a_new_network()

### Community 33 - "tuning/__init__.py"
Cohesion: 0.19
Nodes (13): `average_precision` (função), `score_candidates` (função), `params_key` (função), Otimização de hiperparâmetros: busca em grade que se amplia sozinha, escolhida…, average_precision(), model_scores(), Series, Escores de ``model`` numa rede preparada (``experiment.Prepared``), com… (+5 more)

### Community 34 - "cycle"
Cohesion: 0.11
Nodes (29): `load_amlworld_patterns` (função), `chain` (função), Classes e funções, `cycle` (função), `fan_in` (função), `fan_out` (função), `inject` (função), `scatter_gather` (função) (+21 more)

### Community 35 - "contingency_test"
Cohesion: 0.15
Nodes (14): `contingency_test` (função), Como os testes aparecem nas figuras, Documentação, Funções em [`stats.py`](../src/pixfraud/stats.py), Implementação, Kruskal-Wallis ou Friedman?, Plano de testes estatísticos, Referências (+6 more)

### Community 36 - "label_spreading"
Cohesion: 0.12
Nodes (18): Classes e funções, `label_spreading` (função), `pixfraud.models.semi_supervised.label_spreading`, Quem usa este módulo, Classes e funções, `pixfraud.models.semi_supervised.personalized_pagerank`, `propagate_risk` (função), Quem usa este módulo (+10 more)

### Community 37 - "build_features"
Cohesion: 0.07
Nodes (32): `build_features` (função), Classes e funções, `graph_features` (função), `pixfraud.features`, Quem usa este módulo, `tabular_features` (função), Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree) (+24 more)

### Community 38 - "graph_from_csv"
Cohesion: 0.18
Nodes (15): `money_trail` (função), [`test_graph_tools.py`](../../tests/test_graph_tools.py), MultiDiGraph, graph_from_csv(), money_trail(), DiGraph, Path, Lê uma tabela de transações em CSV e monta o grafo. ``source``, ``target`` e… (+7 more)

### Community 39 - "test_experiment.py"
Cohesion: 0.21
Nodes (17): [`test_experiment.py`](../../tests/test_experiment.py), _planted(), parametrize, Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários., Contas em que só ``sinal`` separa fraude de normal; ``ruido_*`` não informam…, test_comparisons_use_known_feature_sets(), test_feature_ablation_finds_the_informative_feature(), test_known_fraud_scores_learn_from_a_few_known() (+9 more)

### Community 40 - "fluxo-da-pesquisa.md"
Cohesion: 0.25
Nodes (4): Detecção conformal (p-valor por conta), Intervalo de confiança (IC 95%), Otimização de hiperparâmetros, Semente (aleatória)

### Community 41 - "build_graph"
Cohesion: 0.19
Nodes (15): Grafo direcionado ponderado, _animacao(), quadro(), _legenda(), main(), _padroes(), Path, O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora. (+7 more)

### Community 42 - "test_patterns.py"
Cohesion: 0.15
Nodes (18): `fraud_nodes` (função), `mule_ring` (função), [`test_patterns.py`](../../tests/test_patterns.py), chain(), fraud_nodes(), mule_ring(), Graph, Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor). (+10 more)

### Community 43 - "test_algorithms.py"
Cohesion: 0.15
Nodes (16): `money_backbone` (função), `widest_path` (função), [`test_algorithms.py`](../../tests/test_algorithms.py), math, find_pattern(), money_backbone(), Ocorrências do formato ``pattern`` dentro de ``graph`` (algoritmo VF2). Cada…, Espinha dorsal do dinheiro: a ramificação de peso máximo (algoritmo de… (+8 more)

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "test_bcb.py"
Cohesion: 0.25
Nodes (11): [`test_bcb.py`](../../tests/test_bcb.py), io, _http(), Download dos dados abertos do BCB, sem rede: o ``urlopen`` é substituído., Faz o ``urlopen`` levantar cada erro de ``falhas`` e depois responder com uma…, _Resposta, _servidor(), urlopen() (+3 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.20
Nodes (5): As abas, Escolher a rede, Explorador interativo, Guia do explorador, Pass-through (dinheiro que atravessa a conta)

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.18
Nodes (11): 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN) (+3 more)

### Community 49 - "plot_test_statistic"
Cohesion: 0.15
Nodes (19): Axes, `plot_normality` (função), `plot_test_statistic` (função), _grid(), Path, Linha de cima: ``top`` painéis da estatística; linha de baixo: histograma e Q-Q…, Etapa 01: z do modelo nulo da reciprocidade e o grau de entrada contra a normal., Etapa 02: z do Mann-Whitney e H do Kruskal-Wallis no atributo de maior efeito. (+11 more)

### Community 50 - "Detection"
Cohesion: 0.06
Nodes (44): App e testes, Mapa do código, Pacote `pixfraud`, Scripts, Classes e funções, `Detection` (classe), `detection` (função), `pixfraud.models.base` (+36 more)

### Community 51 - "mapa-do-codigo.md"
Cohesion: 0.06
Nodes (34): `app/explorador.py`, `pixfraud.anomaly`, Quem usa este módulo, `pixfraud.graph_models`, Quem usa este módulo, `pixfraud.models`, Quem usa este módulo, `pixfraud.models.supervised.neural` (+26 more)

### Community 52 - "holm_correction"
Cohesion: 0.25
Nodes (8): `holm_correction` (função), Correção de Holm, holm_correction(), _precision_at_k(), ndarray, Fração de fraudes entre as ``k`` contas de maior escore (``k`` padrão: nº de…, p-valores ajustados pelo método de Holm-Bonferroni (controla o erro familiar)., test_holm_correction()

### Community 53 - "gnn.py"
Cohesion: 0.12
Nodes (17): Classes e funções, `directed_sage` (função), `graphsage_scores` (função), `pixfraud.models.supervised.neural.graphsage_directed`, Quem usa este módulo, `available` (função), Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch. Os modelos…, directed_sage() (+9 more)

### Community 54 - "Fluxo da pesquisa"
Cohesion: 0.29
Nodes (7): A ordem das etapas, As pastas seguem as etapas, Cada etapa no projeto, Como está hoje × o ideal, Fluxo da pesquisa, Mapa mental, Por que esta ordem

### Community 55 - "test_stats.py"
Cohesion: 0.23
Nodes (12): `cliffs_delta` (função), [`test_stats.py`](../../tests/test_stats.py), cliffs_delta(), Delta de Cliff: P(X > Y) - P(X < Y), de -1 a 1 (0 = distribuições iguais)., Testes de `pixfraud.stats`: efeito, correções, bootstrap, testes pareados,…, _roles_sample(), test_cliffs_delta_and_labels(), test_compare_groups_finds_the_separating_feature() (+4 more)

### Community 56 - "documentar_codigo.py"
Cohesion: 0.07
Nodes (52): ast, Module, app_note(), build_notes(), _cli_options(), _definition_block(), _definitions(), directories_note() (+44 more)

### Community 57 - "unsupervised/__init__.py"
Cohesion: 0.08
Nodes (30): `top_fraction` (função), Classes e funções, `node2vec_embedding` (função), `node2vec_isolation_forest` (função), scipy_sparse, scipy_stats, sklearn_decomposition, sklearn_exceptions (+22 more)

### Community 58 - "main"
Cohesion: 0.22
Nodes (10): bcb_reference(), compare_with_reference(), main(), DataFrame, Path, As mesmas estatísticas, nos dados abertos do Pix (só agregados, sem dado…, As estatísticas do BCB calculadas numa rede sintética. Golpe é o Pix da vítima…, Para cada (cenário, estatística): média do gerador, IC 95% t, valor do BCB e… (+2 more)

### Community 59 - "_mean_percentile"
Cohesion: 0.40
Nodes (5): _mean_percentile(), Series, Combinação de métodos: média dos percentis de cada um, nas contas avaliadas., Escore de um detector não supervisionado (não usa as contas conhecidas)., _scores()

### Community 60 - "ecod"
Cohesion: 0.14
Nodes (16): Classes e funções, `ecod` (função), `pixfraud.models.unsupervised.statistical.ecod`, Quem usa este módulo, Classes e funções, `pca` (função), `pixfraud.models.unsupervised.statistical.pca`, Quem usa este módulo (+8 more)

### Community 61 - "_plot"
Cohesion: 0.29
Nodes (7): `model_color` (função), _plot(), DataFrame, Path, AP média e IC 95% de cada detector em cada conjunto de atributos., model_color(), Cor fixa de um modelo nas figuras (cinza-médio para um modelo sem cor definida).

### Community 62 - "`pixfraud.algorithms`"
Cohesion: 0.13
Nodes (21): `bipartite_projection` (função), Classes e funções, `cosine_similarity` (função), `find_pattern` (função), Funções internas, `hubs_authorities` (função), `pixfraud.algorithms`, Quem usa este módulo (+13 more)

### Community 63 - "Modelos"
Cohesion: 0.17
Nodes (12): As pastas, Cada modelo, Como cada modelo se saiu, Como reproduzir, Modelos, Não supervisionados, O ganho de verdade: nas redes de teste, O que a tabela diz (+4 more)

### Community 64 - "`pixfraud.stats`"
Cohesion: 0.25
Nodes (8): Funções internas, `paired_comparison` (função), `pixfraud.stats`, Quem usa este módulo, Teste de Wilcoxon pareado, paired_comparison(), Compara duas abordagens medidas nas mesmas unidades (ex.: mesmas sementes).…, test_paired_comparison_and_summary()

### Community 65 - "pandas"
Cohesion: 0.10
Nodes (25): collections_abc, html, networkx, numpy, pandas, scipy, O dataset sintético parece o Pix real? Validação do gerador contra o Banco…, Que tipo de rede é a do Pix sintético? E o que passeios e cosseno dizem sobre… (+17 more)

### Community 66 - "_profile"
Cohesion: 0.50
Nodes (4): _profile(), DataFrame, Series, Mediana, por papel, do que as contas fazem: quem paga, quem recebe e quanto…

### Community 67 - "_plot_share"
Cohesion: 0.33
Nodes (6): _plot_share(), DataFrame, Path, Por (cenário, modelo): razão de chances mediana do comércio no top-k, em…, Mapa de calor: fração das k primeiras contas de cada modelo que são comércios., _tests_table()

### Community 68 - "visualization.py"
Cohesion: 0.15
Nodes (15): matplotlib, matplotlib_animation, matplotlib_colors, matplotlib_lines, matplotlib_pyplot, Vitrine de todos os modelos: qual abordagem funciona, e em qual cenário? Para…, Avalia os detectores em cenários de dificuldade (configs/cenarios.yaml). O…, Avalia os detectores num dataset externo (AMLworld), janela por janela. Usa a… (+7 more)

### Community 69 - "null_model_test"
Cohesion: 0.18
Nodes (11): `null_model_test` (função), [`auditar_papeis.py`](../../scripts/01_dados/auditar_papeis.py), [`baixar_dados_bcb.py`](../../scripts/01_dados/baixar_dados_bcb.py), [`gerar_dataset.py`](../../scripts/01_dados/gerar_dataset.py), [`importar_dataset.py`](../../scripts/01_dados/importar_dataset.py), `scripts/01_dados/`, [`validar_realismo.py`](../../scripts/01_dados/validar_realismo.py), null_model_test() (+3 more)

### Community 70 - "reproduzir_tudo.py"
Cohesion: 0.11
Nodes (23): csv, datetime, os, abrir(), anotar(), formatar(), gnn_disponivel(), graphify() (+15 more)

### Community 71 - "average-precision.md"
Cohesion: 0.33
Nodes (3): Classes raras (desbalanceamento), KNN (k vizinhos mais próximos), ROC-AUC

### Community 72 - "_attach_roles"
Cohesion: 0.50
Nodes (4): _attach_roles(), DiGraph, Path, Copia o papel de cada conta (de accounts.csv) para os vértices do grafo, se…

### Community 73 - "evaluate"
Cohesion: 0.13
Nodes (20): Classes e funções, `evaluate` (função), `pixfraud.evaluation`, Quem usa este módulo, `ranking_metrics` (função), `recall_by_group` (função), [`test_evaluation.py`](../../tests/test_evaluation.py), Average precision (AP) (+12 more)

### Community 74 - "explorador.py"
Cohesion: 0.11
Nodes (18): br(), brl(), DataFrame, Series, Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório (só…, Papel de cada conta, com as vítimas de golpe destacadas como ``vitima``., Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Valor em reais sem centavos, com ponto de milhar. (+10 more)

### Community 75 - "experiment.py"
Cohesion: 0.18
Nodes (12): concurrent_futures, importlib_metadata, inspect, json, platform, Otimiza os hiperparâmetros de cada modelo em redes de validação, até achar o…, Núcleo do experimento: transações -> grafo -> atributos -> detectores ->…, Todos os modelos de detecção, um arquivo por modelo, agrupados por tipo e por… (+4 more)

### Community 76 - "Param"
Cohesion: 0.14
Nodes (14): `expand` (função), Funções internas, `pixfraud.tuning.search_space`, Quem usa este módulo, expand(), Param, Amplia ``space`` onde o vencedor ``chosen`` caiu numa ponta da lista. Devolve o…, Os valores testados de um hiperparâmetro e, se ele puder crescer, os limites. (+6 more)

### Community 77 - "gradient_boosting_scores"
Cohesion: 0.15
Nodes (15): Classes e funções, `gradient_boosting_scores` (função), `make_gradient_boosting` (função), `pixfraud.models.supervised.trees.gradient_boosting`, Quem usa este módulo, HistGradientBoostingClassifier, sklearn_ensemble, gradient_boosting_scores() (+7 more)

### Community 78 - "Instruções para agentes"
Cohesion: 0.25
Nodes (8): Ao editar notas, Autoria, Como se orientar, Código, Git, Instruções para agentes, Regra principal: LGPD no contexto do Pix, head()

### Community 79 - "Resultados"
Cohesion: 0.12
Nodes (17): 10. Redes neurais para grafos (GNN), 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial, 16. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador (+9 more)

### Community 80 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.17
Nodes (16): _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), Path, Desenha os dois grafos de conhecimento do repositório para o README. São… (+8 more)

### Community 81 - "Glossário"
Cohesion: 0.40
Nodes (5): Avaliação e estatística, Detecção, Glossário, Pix e dados, Teoria dos grafos

### Community 82 - "compare_groups"
Cohesion: 0.16
Nodes (16): Classes e funções, `compare_groups` (função), `dunn_posthoc` (função), `effect_size_label` (função), `kruskal_groups` (função), `summarize_runs` (função), Delta de Cliff ($\delta$), Teste de Kruskal-Wallis (+8 more)

### Community 83 - "_look_alike_transactions"
Cohesion: 0.07
Nodes (35): _after_activity(), _amounts(), _camouflage_transactions(), _collector_payouts(), _day_weights(), _fraud_ring(), _hops(), _later() (+27 more)

### Community 84 - "exportar_grafo_de_notas.py"
Cohesion: 0.17
Nodes (15): Pattern, re, como_json(), _filtros_do_cofre(), grafo_de_notas(), main(), notas_do_cofre(), Path (+7 more)

### Community 85 - "Documentação da pesquisa"
Cohesion: 0.50
Nodes (4): A pesquisa, Anotações, Documentação da pesquisa, Documentação do código e dos dados

### Community 86 - "A rede Pix dentro do cofre"
Cohesion: 0.40
Nodes (4): A rede Pix dentro do cofre, Como gerar outros recortes, Figuras estáticas, Rede inteira, interativa

### Community 87 - "Revisão bibliográfica"
Cohesion: 0.50
Nodes (4): Como fichar uma leitura, Fichamentos, Revisão bibliográfica, Sugestões de leitura

### Community 88 - "test_graph_models.py"
Cohesion: 0.20
Nodes (14): [`test_graph_models.py`](../../tests/test_graph_models.py), fixture, parametrize, Testes de `pixfraud.graph_models` e de `communities.peeling_scores`: detectores…, Grafo esparso aleatório com um bloco denso plantado: 6 contas que pagam todas a…, sparse_graph_with_block(), test_densest_subgraph_still_finds_the_block(), test_fraudar_detector_marks_the_block() (+6 more)

### Community 89 - "`scripts/04_avaliacao/`"
Cohesion: 0.14
Nodes (14): `known_fraud_scores` (função), [`avaliar_atributos.py`](../../scripts/04_avaliacao/avaliar_atributos.py), [`avaliar_cenarios.py`](../../scripts/04_avaliacao/avaliar_cenarios.py), [`avaliar_deteccao_online.py`](../../scripts/04_avaliacao/avaliar_deteccao_online.py), [`avaliar_externo.py`](../../scripts/04_avaliacao/avaliar_externo.py), [`avaliar_gnn.py`](../../scripts/04_avaliacao/avaliar_gnn.py), [`avaliar_gnn_rotulos.py`](../../scripts/04_avaliacao/avaliar_gnn_rotulos.py), [`avaliar_propagacao.py`](../../scripts/04_avaliacao/avaliar_propagacao.py) (+6 more)

### Community 90 - "fit_sage"
Cohesion: 0.15
Nodes (12): Classes e funções, `fit_sage` (função), `GraphSAGE` (classe), `sage_known_fraud_scores` (função), `sage_supervised_scores` (função), fit_sage(), GraphSAGE, ndarray (+4 more)

### Community 91 - "isolation_forest"
Cohesion: 0.18
Nodes (11): Classes e funções, `isolation_forest` (função), `pixfraud.models.unsupervised.isolation.isolation_forest`, Quem usa este módulo, `pixfraud.models.unsupervised.isolation`, Quem usa este módulo, Modelos de **isolamento**: a conta suspeita se separa das outras com poucos…, isolation_forest() (+3 more)

### Community 92 - "candidates"
Cohesion: 0.23
Nodes (12): `candidates` (função), Classes e funções, `full_params` (função), `grid` (função), `Param` (classe), candidates(), full_params(), grid() (+4 more)

### Community 93 - "exploration.py"
Cohesion: 0.21
Nodes (8): [`test_gnn_direcionada.py`](../../tests/test_gnn_direcionada.py), Gera o explorador interativo da rede inteira (HTML). A página mostra todas as…, O que o explorador interativo (``app/explorador.py``) e a página da rede…, Detecção de fraudes em transações PIX com teoria dos grafos e machine learning., Testes da GraphSAGE direcionada de `pixfraud.gnn` (`graphsage_scores`). Pulados…, test_graphsage_beats_chance_and_covers_every_account(), test_graphsage_is_available(), test_graphsage_is_reproducible_with_the_seed()

### Community 94 - "prepare_matrix"
Cohesion: 0.15
Nodes (18): `pixfraud.gnn`, Quem usa este módulo, `pixfraud.models.supervised.neural.graphsage`, Quem usa este módulo, prepare_matrix(), DataFrame, Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza…, DataFrame (+10 more)

### Community 95 - "out_of_fold_scores"
Cohesion: 0.18
Nodes (11): ClassifierMixin, `pixfraud.models.supervised`, Quem usa este módulo, out_of_fold_scores(), DataFrame, Series, Probabilidade de fraude de cada conta, dada pelo modelo treinado sem ela.…, Como as peças se encaixam (+3 more)

### Community 96 - "Módulos"
Cohesion: 0.05
Nodes (54): `all_model_scores` (função), Classes e funções, `feature_ablation` (função), Funções internas, `load_experiment_config` (função), `load_scenarios` (função), `pixfraud.experiment`, `prepare` (função) (+46 more)

### Community 97 - "dominant_scores"
Cohesion: 0.18
Nodes (10): Classes e funções, `dominant_scores` (função), `pixfraud.models.unsupervised.neural.dominant`, Quem usa este módulo, Redes neurais para grafos (GNN), dominant_scores(), DataFrame, Graph (+2 more)

### Community 98 - "choose"
Cohesion: 0.22
Nodes (11): `choose` (função), `chosen_params` (função), Classes e funções, `model_scores` (função), `pixfraud.tuning.search`, Quem usa este módulo, choose(), chosen_params() (+3 more)

### Community 99 - "test_flow.py"
Cohesion: 0.27
Nodes (10): [`test_flow.py`](../../tests/test_flow.py), A(), fixture, Testes de `pixfraud.flow`: fluxo máximo, corte mínimo, contas a bloquear e…, test_blocking_accounts(), test_label_spreading_pulls_toward_known_sides(), test_label_spreading_reaches_ring_members(), test_max_flow_equals_min_cut() (+2 more)

### Community 100 - "adjacency"
Cohesion: 0.20
Nodes (10): `adjacency` (função), Classes e funções, `pixfraud.models.torch_utils`, Quem usa este módulo, `require_torch` (função), adjacency(), Graph, Index (+2 more)

### Community 101 - "SimulationConfig"
Cohesion: 0.15
Nodes (12): _dataset_pequeno(), Dataset com uma única quadrilha, pequeno o bastante para desenhar., _chain_slots(), Valida as opções de texto e normaliza as tipologias de lavagem para tupla., Quantas posições de intermediário a quadrilha tem, conforme as tipologias de…, Parâmetros da simulação (descritos em ``configs/experimento.yaml``)., SimulationConfig, Escrevendo um teste novo (+4 more)

### Community 103 - "test_anomaly.py"
Cohesion: 0.13
Nodes (25): Classes e funções, `dbscan` (função), `pixfraud.models.unsupervised.proximity.dbscan`, Quem usa este módulo, [`test_anomaly.py`](../../tests/test_anomaly.py), dbscan(), DataFrame, DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.… (+17 more)

### Community 104 - "test_buscar.py"
Cohesion: 0.31
Nodes (9): [`test_buscar.py`](../../tests/test_buscar.py), _cofre(), Path, Testes da busca única (scripts/ferramentas/buscar.py) num cofre e num grafo de…, test_codigo_acha_pelo_nome_e_mostra_so_vizinhos_do_repositorio(), test_codigo_citado_conta_as_notas_que_apontam_para_cada_py(), test_normalizar_ignora_acentos_maiusculas_e_separadores(), test_notas_exigem_todos_os_termos_e_poem_o_titulo_na_frente() (+1 more)

### Community 105 - "test_gnn.py"
Cohesion: 0.27
Nodes (9): [`test_gnn.py`](../../tests/test_gnn.py), fixture, Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")., 300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.…, ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known() (+1 more)

### Community 106 - "test_online.py"
Cohesion: 0.31
Nodes (9): [`test_online.py`](../../tests/test_online.py), parametrize, Testes de `pixfraud.online`: dinheiro recuperado calculado à mão e pontos de…, _recovered(), test_blocked_mule_keeps_money_that_arrives_later(), test_exposure_and_first_flags(), test_recovered_amount(), test_relevant_checkpoints_skip_quiet_periods() (+1 more)

### Community 107 - "test_tuning.py"
Cohesion: 0.31
Nodes (9): [`test_tuning.py`](../../tests/test_tuning.py), lento, Testes de `pixfraud.tuning` (busca de hiperparâmetros) e da organização de…, test_choose_keeps_the_current_config_on_a_tie(), test_every_grid_names_real_models_and_parameters(), test_expand_only_touches_parameters_whose_winner_is_at_an_edge(), test_old_modules_reexport_the_same_models(), test_param_goes_beyond_the_edge_with_the_same_step_and_stops_at_the_limit() (+1 more)

### Community 108 - "bcb.py"
Cohesion: 0.18
Nodes (8): pypandoc, main(), Gera o relatório a partir dos capítulos em Markdown de relatorio/capitulos/.…, Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a…, Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. Os…, urllib_error, urllib_parse, urllib_request

### Community 109 - "Mapa"
Cohesion: 0.20
Nodes (10): 1. Dados, 2. Exploração, 3. Modelos, 4. Avaliação, 5. Interpretação, Ferramentas, Mapa, Pipeline (+2 more)

### Community 110 - "fetch"
Cohesion: 0.22
Nodes (9): Classes e funções, `fetch` (função), `pixfraud.bcb`, Quem usa este módulo, main(), Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a…, fetch(), DataFrame (+1 more)

### Community 111 - "fraudar"
Cohesion: 0.25
Nodes (9): Classes e funções, `fraudar` (função), `pixfraud.models.unsupervised.graph.fraudar`, Quem usa este módulo, `pixfraud.models.unsupervised.graph`, Quem usa este módulo, fraudar(), Graph (+1 more)

### Community 112 - "plot_value_matrix"
Cohesion: 0.28
Nodes (9): _plot_ablation(), _plot_ceiling(), DataFrame, Path, Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo., Um painel por cenário: conjunto de atributos × modelo, da AP média (tetos…, plot_value_matrix(), Matriz de resultados: uma célula colorida por valor, com o número escrito nela.… (+1 more)

### Community 113 - "friedman_models"
Cohesion: 0.29
Nodes (8): `friedman_models` (função), `plot_critical_difference` (função), Teste de Friedman e diferença crítica de Nemenyi, friedman_models(), Teste de Friedman entre vários modelos medidos nas mesmas unidades (sementes).…, plot_critical_difference(), Postos médios do teste de Friedman com a diferença crítica de Nemenyi.…, test_friedman_models_matches_scipy_and_gives_the_critical_difference()

### Community 114 - "test_features.py"
Cohesion: 0.29
Nodes (7): [`test_features.py`](../../tests/test_features.py), chain(), fixture, Testes de `pixfraud.features`: cada atributo conferido à mão num grafo pequeno., Cadeia A -> B -> C -> D, um pagamento extra E -> B e uma conta F sem transações., test_features(), test_graph_aggregates_repeated_pairs()

### Community 115 - "_metrics"
Cohesion: 0.25
Nodes (8): _metrics(), _plot(), DataFrame, Path, Series, Timedelta, Fração detectada em até 72 h, atraso mediano e dinheiro recuperado em cada…, Painéis modelo × métrica; em cada um, conjunto de atributos (e oráculo) ×…

### Community 116 - "features.py"
Cohesion: 0.33
Nodes (4): collections, Avalia a detecção ao longo do tempo: a quadrilha é sinalizada a tempo de…, Atributos por conta usados pelos detectores de anomalia. Os atributos são…, Detecção ao longo do tempo: a conta foi sinalizada a tempo de bloquear o…

### Community 117 - "load_search_spaces"
Cohesion: 0.29
Nodes (7): `load_search_spaces` (função), `model_function` (função), load_search_spaces(), model_function(), Path, Lê as grades do YAML: ``{modelo: {hiperparâmetro: Param}}``., A função de ``model`` num dos registros de ``pixfraud.models``.

### Community 118 - "_plot_metric"
Cohesion: 0.33
Nodes (7): _plot_effects(), _plot_metric(), DataFrame, Path, Series, Matriz conjunto de atributos × cenário da média da métrica, um painel por…, Matriz atributo × cenário do delta de Cliff médio (> 0: maior nas contas…

### Community 119 - "Próximos passos"
Cohesion: 0.33
Nodes (6): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório

### Community 120 - "main"
Cohesion: 0.33
Nodes (6): main(), Avalia os candidatos de hiperparâmetros numa rede de validação (para o pool de…, Grava a configuração com os hiperparâmetros escolhidos e um cabeçalho de como…, Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a…, _score_star(), _write_config()

### Community 121 - "_plot_typologies"
Cohesion: 0.33
Nodes (6): _plot_typologies(), _pool(), DataFrame, Path, Junta as janelas: acertos somados sobre contas somadas, por tipologia,…, Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo.

### Community 122 - "_plot"
Cohesion: 0.33
Nodes (6): _known_label(), _plot(), DataFrame, Path, Rótulo do nível de conhecimento: as contestações ou a fração de fraudes…, Matriz método × (cenário, fração conhecida) da AP média.

### Community 123 - "Classes e funções"
Cohesion: 0.40
Nodes (5): Classes e funções, `known_fraud_out_of_fold` (função), `out_of_fold_scores` (função), `pixfraud.models.supervised.cross_validation`, Quem usa este módulo

### Community 124 - "bootstrap_metric"
Cohesion: 0.40
Nodes (5): `bootstrap_metric` (função), Bootstrap, bootstrap_metric(), Estimativa pontual e IC por bootstrap percentil de uma métrica de desempenho.…, test_bootstrap_metric_perfect_ranking()

### Community 125 - "[`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py)"
Cohesion: 0.40
Nodes (5): [`analisar_tipo_de_rede.py`](../../scripts/02_exploracao/analisar_tipo_de_rede.py), [`criar_grafo.py`](../../scripts/02_exploracao/criar_grafo.py), [`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py), `scripts/02_exploracao/`, [`visualizar_rede.py`](../../scripts/02_exploracao/visualizar_rede.py)

### Community 126 - "_plot"
Cohesion: 0.50
Nodes (4): _plot(), DataFrame, Path, Matriz método × cenário da AP média.

### Community 127 - "_plot"
Cohesion: 0.50
Nodes (4): _plot(), DataFrame, Path, Matriz método × cenário da AP média.

### Community 128 - "_plot"
Cohesion: 0.50
Nodes (4): _plot(), DataFrame, Path, Matriz método × (cenário, fração conhecida) da AP média.

### Community 129 - "cross_validation.py"
Cohesion: 0.50
Nodes (3): sklearn_base, sklearn_model_selection, Validação cruzada dos modelos supervisionados: nenhuma conta recebe a nota de…

### Community 130 - "Configurações"
Cohesion: 0.67
Nodes (3): Configurações, Criar um cenário, Mudar um parâmetro

### Community 131 - "`pixfraud.patterns`"
Cohesion: 0.67
Nodes (3): Funções internas, `pixfraud.patterns`, Quem usa este módulo

## Knowledge Gaps
- **238 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Ao editar notas`, `Git` (+233 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 902 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `algorithms.py`, `flow.py`, `recovered_amount`, `test_explorer.py`, `external.py`, `permutation_test_metric`, `generate_dataset`, `rank_models`, `draw_graph`, `with_overrides`, `test_network.py`, `describe`, `temporal.py`, `communities.py`, `plot_heat_graph`, `tuning/__init__.py`, `cycle`, `label_spreading`, `build_features`, `graph_from_csv`, `build_graph`, `test_algorithms.py`, `Detection`, ``pixfraud.algorithms``, `evaluate`, `Param`, `compare_groups`, `out_of_fold_scores`, `choose`, `SimulationConfig`, `fetch`, `plot_value_matrix`, `friedman_models`, `load_search_spaces`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `Detection` connect `Detection` to `Módulos`, `pandas`, `visualization.py`, `test_anomaly.py`, `evaluate`, `one_class_svm`, `experiment.py`, `fraudar`, `Modelos usados na pesquisa (e outros que caberiam)`, `autoencoder`, `unsupervised/__init__.py`, `isolation_forest`, `ecod`, `out_of_fold_scores`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `generate_dataset()` connect `generate_dataset` to `audit_roles`, `Módulos`, `test_scripts.py`, `test_flow.py`, `SimulationConfig`, `experiment.py`, `test_tuning.py`, `with_overrides`, `test_network.py`, `_look_alike_transactions`, `main`, `main`, `test_graph_models.py`, `exploration.py`, `plot_heat_graph`, `simulation.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `generate_dataset()` (e.g. with ``draw_structure` (função)` and ``generate_dataset` (função)`) actually correct?**
  _`generate_dataset()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 56 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 56 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _238 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `audit_roles` be split into smaller, more focused modules?**
  _Cohesion score 0.05975609756097561 - nodes in this community are weakly interconnected._