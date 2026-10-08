# Graph Report - deteccao-fraudes-pix-grafos  (2026-10-08)

## Corpus Check
- 184 files · ~98,054 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .bib 1)

## Summary
- 1534 nodes · 3951 edges · 81 communities (69 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 236 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1ba4fe40`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- gnn.py
- Módulos
- test_scripts.py
- flow.py
- online.py
- explorer.py
- external.py
- buscar.py
- evaluate
- one_class_svm.py
- pandas
- generate_dataset
- explorador.py
- draw_graph
- argparse
- prepare_matrix
- network.py
- glossario.md
- avaliar_sementes.py
- graph.py
- json
- out_of_fold_scores
- plot_model_intervals
- modelos.md
- matplotlib_pyplot
- temporal.py
- communities.py
- Detection
- pytest
- pixfraud
- plot_heat_graph
- test_app.py
- test_tuning.py
- patterns.py
- search_space.py
- label_spreading
- build_features
- build_graph
- Resultados
- testes-para-classificadores.md
- search.py
- networkx
- sage_supervised_scores
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- test_bcb.py
- guia-do-explorador.md
- Modelos usados na pesquisa (e outros que caberiam)
- Próximos passos
- unsupervised/__init__.py
- gerar_ilustracoes.py
- ilustrar_grafos_de_conhecimento.py
- graphsage_directed.py
- compare_groups
- effect_size_label
- gerar_relatorio.py
- node2vec_embedding
- supervised_scores
- run_detectors
- ecod.py
- main
- isolation_forest.py
- Cada modelo
- network_summary
- GraphSAGE
- mapa-dos-modelos.md
- Instruções para agentes
- Glossário
- numpy
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- _mean_percentile
- dominant_scores
- test_experiment.py
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- SimulationConfig
- test_anomaly.py
- parametros-dos-experimentos.md

## God Nodes (most connected - your core abstractions)
1. `generate_dataset()` - 57 edges
2. `Módulos` - 56 edges
3. `Detection` - 38 edges
4. `prepare_matrix()` - 33 edges
5. `build_graph()` - 28 edges
6. `SimulationConfig` - 28 edges
7. `prepare()` - 25 edges
8. `load_scenarios()` - 22 edges
9. `save_metadata()` - 22 edges
10. `load_config()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Outros modelos que caberiam nesta pesquisa` --references--> `Detection`  [INFERRED]
  docs/modelos.md → src/pixfraud/models/base.py
- `Escrevendo um teste novo` --references--> `SimulationConfig`  [INFERRED]
  tests/mapa-dos-testes.md → src/pixfraud/simulation.py
- `Intervalo de confiança (IC 95%)` --references--> `summarize_runs()`  [INFERRED]
  docs/glossario/intervalo-de-confianca.md → src/pixfraud/stats.py
- `Um modelo é melhor que outro?` --references--> `compare_runs()`  [INFERRED]
  docs/glossario/testes-para-classificadores.md → src/pixfraud/stats.py
- `Comunidades e modularidade (Louvain)` --references--> `detect_communities()`  [INFERRED]
  docs/glossario/comunidades-e-modularidade.md → src/pixfraud/communities.py

## Import Cycles
- 4-file cycle: `src/pixfraud/models/__init__.py -> src/pixfraud/models/unsupervised/__init__.py -> src/pixfraud/models/unsupervised/neural/__init__.py -> src/pixfraud/models/unsupervised/neural/dominant.py -> src/pixfraud/models/__init__.py`

## Communities (81 total, 12 thin omitted)

### Community 0 - "gnn.py"
Cohesion: 0.18
Nodes (3): adjacency(), available(), require_torch()

### Community 1 - "Módulos"
Cohesion: 0.11
Nodes (13): _amounts(), bipartite_projection(), cosine_similarity(), find_pattern(), hubs_authorities(), laundering_depth(), longest_chain(), similar_accounts() (+5 more)

### Community 2 - "test_scripts.py"
Cohesion: 0.21
Nodes (18): _check_metadata(), _run(), test_avaliar_atributos(), test_avaliar_cenarios(), test_avaliar_deteccao_online(), test_avaliar_externo(), test_avaliar_fraudar(), test_avaliar_gnn() (+10 more)

### Community 3 - "flow.py"
Cohesion: 0.16
Nodes (12): Fluxo máximo e corte mínimo, _attach_roles(), main(), _as_list(), blocking_accounts(), blocking_cut(), _flow_network(), max_money_flow() (+4 more)

### Community 4 - "online.py"
Cohesion: 0.10
Nodes (12): _metrics(), checkpoint_flags(), exposure_times(), first_flags(), recovered_amount(), relevant_checkpoints(), _recovered(), test_blocked_mule_keeps_money_that_arrives_later() (+4 more)

### Community 5 - "explorer.py"
Cohesion: 0.06
Nodes (28): Abrir, Busca única nos dois grafos, Cores do grafo, por tipo de nota, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais), Por que nenhuma nota se chama "README" (+20 more)

### Community 6 - "external.py"
Cohesion: 0.11
Nodes (17): main(), _account(), _account_id(), _accounts_table(), _amlworld_chunk(), load_amlworld(), load_amlworld_patterns(), load_paysim() (+9 more)

### Community 7 - "buscar.py"
Cohesion: 0.06
Nodes (26): buscar_codigo(), buscar_notas(), _carregar_exportador(), _casa(), codigo_citado(), grafo_velho(), _lista(), main() (+18 more)

### Community 8 - "evaluate"
Cohesion: 0.17
Nodes (8): Average precision (AP), Precision@k, evaluate(), ranking_metrics(), recall_by_group(), test_evaluate_perfect_ranking(), test_ranking_metrics(), test_recall_by_group()

### Community 10 - "pandas"
Cohesion: 0.11
Nodes (15): Bootstrap, Teste de Wilcoxon pareado, top_k_outcome(), bootstrap_metric(), contingency_test(), paired_comparison(), blob_with_outlier(), test_top_k_outcome_sorts_hits_misses_and_false_alarms() (+7 more)

### Community 11 - "generate_dataset"
Cohesion: 0.10
Nodes (19): generate_dataset(), _has_look_alikes(), test_checkpoint_flags_budget(), calibrated(), dataset(), test_collector_payouts_empties_the_collector(), test_collector_payouts_off_by_default_keeps_dataset(), test_commercial_hours_also_apply_to_slow_forwards() (+11 more)

### Community 12 - "explorador.py"
Cohesion: 0.07
Nodes (14): explorer_page(), model_scores(), network(), network_title(), roles_with_victims(), roll_dice(), with_roles(), picker_entries() (+6 more)

### Community 13 - "draw_graph"
Cohesion: 0.20
Nodes (8): draw_graph(), _format_amount(), graph_html(), _layout(), _node_colors(), save_graph(), _serializable(), to_html()

### Community 14 - "argparse"
Cohesion: 0.12
Nodes (27): main(), main(), _evaluate(), main(), main(), main(), main(), main() (+19 more)

### Community 15 - "prepare_matrix"
Cohesion: 0.14
Nodes (4): prepare_matrix(), autoencoder(), test_autoencoder_is_reproducible_with_the_seed(), test_prepare_matrix_rejects_negative_features()

### Community 16 - "network.py"
Cohesion: 0.08
Nodes (18): Componente gigante, _degree_graphs(), _measure(), _plot_degrees(), compare_network_models(), component_summary(), degree_sequence(), fit_power_law() (+10 more)

### Community 17 - "glossario.md"
Cohesion: 0.16
Nodes (7): Conta laranja (conta de passagem), DBSCAN e k-distance, Local Outlier Factor (LOF), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Propagação de risco (culpa por associação), Glossário

### Community 18 - "avaliar_sementes.py"
Cohesion: 0.15
Nodes (9): _convergence(), _draws(), main(), _one_seed(), _paired_needs(), _plot(), _run(), _seeds_for_power() (+1 more)

### Community 19 - "graph.py"
Cohesion: 0.10
Nodes (13): adjacency_matrix(), describe(), graph_from_csv(), graph_from_edges(), money_trail(), test_laundering_depth_and_longest_chain(), test_similar_accounts_cosine_uses_amounts(), test_widest_path() (+5 more)

### Community 20 - "json"
Cohesion: 0.24
Nodes (3): _cofre(), test_codigo_citado_conta_as_notas_que_apontam_para_cada_py(), test_notas_exigem_todos_os_termos_e_poem_o_titulo_na_frente()

### Community 21 - "out_of_fold_scores"
Cohesion: 0.09
Nodes (11): known_fraud_out_of_fold(), out_of_fold_scores(), gradient_boosting_scores(), make_gradient_boosting(), make_random_forest(), random_forest_known_fraud_scores(), random_forest_scores(), Como as peças se encaixam (+3 more)

### Community 22 - "plot_model_intervals"
Cohesion: 0.08
Nodes (12): _plot_comparisons(), _plot_models(), _plot(), explain_account(), format_ci(), format_number(), model_color(), model_label() (+4 more)

### Community 23 - "modelos.md"
Cohesion: 0.17
Nodes (7): Cronograma, Mapa da pesquisa, Trilha de estudos, Convenções, Notebooks da pesquisa, Mapa dos notebooks, Mapa dos scripts

### Community 24 - "matplotlib_pyplot"
Cohesion: 0.06
Nodes (15): _plot_ablation(), _plot_ceiling(), _plot_effects(), _plot_metric(), _plot(), _plot_typologies(), _pool(), _plot() (+7 more)

### Community 25 - "temporal.py"
Cohesion: 0.11
Nodes (15): Caminho temporal, Tempo de permanência (dwell time), _best_hops(), _check_direction(), dwell_time(), temporal_features(), temporal_reachability(), temporal_trail() (+7 more)

### Community 26 - "communities.py"
Cohesion: 0.06
Nodes (39): Coeficiente de participação, Comunidades e modularidade (Louvain), Egonet e OddBall, FRAUDAR, K-núcleo (core number), 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), community_summary() (+31 more)

### Community 27 - "Detection"
Cohesion: 0.16
Nodes (3): Detection, top_fraction(), fraudar()

### Community 28 - "pytest"
Cohesion: 0.18
Nodes (8): test_generate_network_is_reproducible_and_follows_the_scenario(), test_label_spreading_pulls_toward_known_sides(), test_walks_from_victims_end_at_collectors(), test_activity_clock(), test_calibrated_scenario_matches_bcb_numbers(), test_collector_payouts_and_cashout_are_alternatives(), test_invalid_realism_parameters_are_rejected(), test_with_overrides_validates_names()

### Community 30 - "plot_heat_graph"
Cohesion: 0.29
Nodes (3): flow_layout(), reorder(), plot_heat_graph()

### Community 33 - "test_tuning.py"
Cohesion: 0.14
Nodes (6): expand(), Param, _tidy(), test_every_grid_names_real_models_and_parameters(), test_expand_only_touches_parameters_whose_winner_is_at_an_edge(), test_param_goes_beyond_the_edge_with_the_same_step_and_stops_at_the_limit()

### Community 34 - "patterns.py"
Cohesion: 0.18
Nodes (13): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), cycle(), fan_in(), fan_out(), inject() (+5 more)

### Community 35 - "search_space.py"
Cohesion: 0.21
Nodes (6): candidates(), full_params(), grid(), load_search_spaces(), model_function(), test_grid_and_candidates_include_the_current_config_once()

### Community 37 - "build_features"
Cohesion: 0.09
Nodes (21): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+13 more)

### Community 38 - "build_graph"
Cohesion: 0.12
Nodes (10): Grafo direcionado ponderado, quadro(), build_graph(), chain(), test_features(), test_graph_aggregates_repeated_pairs(), A(), test_label_spreading_reaches_ring_members() (+2 more)

### Community 39 - "Resultados"
Cohesion: 0.12
Nodes (17): 10. Redes neurais para grafos (GNN), 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial, 16. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador (+9 more)

### Community 40 - "testes-para-classificadores.md"
Cohesion: 0.19
Nodes (6): Detecção conformal (p-valor por conta), Intervalo de confiança (IC 95%), O modelo é melhor que o acaso?, Testes de hipótese para classificadores, Um modelo é melhor que outro?, "É comércio ou não?"

### Community 41 - "search.py"
Cohesion: 0.18
Nodes (5): average_precision(), model_scores(), score_candidates(), params_key(), test_score_candidates_on_a_small_network()

### Community 42 - "networkx"
Cohesion: 0.13
Nodes (10): money_backbone(), fraud_nodes(), null_model_test(), test_money_backbone_keeps_main_source(), test_chain_loses_fee_at_each_hop(), test_cycle_is_strongly_connected(), test_inject_maps_victims_to_existing_accounts(), test_mule_ring_money_reaches_collector() (+2 more)

### Community 43 - "sage_supervised_scores"
Cohesion: 0.22
Nodes (3): fit_sage(), sage_known_fraud_scores(), sage_supervised_scores()

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "test_bcb.py"
Cohesion: 0.12
Nodes (9): main(), fetch(), _http(), _Resposta, _servidor(), urlopen(), test_desiste_depois_das_tentativas(), test_nao_tenta_de_novo_em_erro_definitivo() (+1 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.22
Nodes (4): As abas, Escolher a rede, Explorador interativo, Guia do explorador

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.18
Nodes (11): 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN) (+3 more)

### Community 49 - "Próximos passos"
Cohesion: 0.33
Nodes (6): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório

### Community 50 - "unsupervised/__init__.py"
Cohesion: 0.15
Nodes (3): knn(), local_outlier_factor(), test_local_outlier_factor_flags_the_point_in_the_sparse_region()

### Community 51 - "gerar_ilustracoes.py"
Cohesion: 0.26
Nodes (5): _animacao(), _legenda(), main(), _padroes(), _rede_exemplo()

### Community 52 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.24
Nodes (7): _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), _rotulo()

### Community 53 - "graphsage_directed.py"
Cohesion: 0.18
Nodes (3): directed_sage(), __init__(), graphsage_scores()

### Community 54 - "compare_groups"
Cohesion: 0.18
Nodes (8): Correção de Holm, Delta de Cliff ($\delta$), Teste de Kruskal-Wallis, Teste de Mann-Whitney, compare_groups(), holm_correction(), test_compare_groups_finds_the_separating_feature(), test_holm_correction()

### Community 55 - "effect_size_label"
Cohesion: 0.40
Nodes (3): cliffs_delta(), effect_size_label(), test_cliffs_delta_and_labels()

### Community 58 - "supervised_scores"
Cohesion: 0.22
Nodes (7): Random Forest (como teto supervisionado), Validação cruzada estratificada, supervised_scores(), _planted(), test_feature_ablation_finds_the_informative_feature(), test_supervised_scores_are_out_of_fold(), test_supervised_scores_rejects_unknown_model()

### Community 59 - "run_detectors"
Cohesion: 0.24
Nodes (5): 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive, feature_ablation(), known_fraud_scores(), run_detectors(), test_known_fraud_scores_learn_from_a_few_known()

### Community 61 - "main"
Cohesion: 0.32
Nodes (5): main(), _score_star(), choose(), chosen_params(), test_choose_keeps_the_current_config_on_a_tie()

### Community 63 - "Cada modelo"
Cohesion: 0.29
Nodes (7): As pastas, Cada modelo, Modelos, Não supervisionados, Semi-supervisionados, Supervisionado, semi-supervisionado ou não supervisionado?, Supervisionados (teto)

### Community 71 - "mapa-dos-modelos.md"
Cohesion: 0.14
Nodes (7): Classes raras (desbalanceamento), Isolation Forest, Otimização de hiperparâmetros, ROC-AUC, Semente (aleatória), Supervisionado e não supervisionado, Modelos

### Community 78 - "Instruções para agentes"
Cohesion: 0.29
Nodes (7): Ao editar notas, Autoria, Como se orientar, Código, Instruções para agentes, Regra principal: LGPD no contexto do Pix, head()

### Community 81 - "Glossário"
Cohesion: 0.40
Nodes (5): Avaliação e estatística, Detecção, Glossário, Pix e dados, Teoria dos grafos

### Community 83 - "numpy"
Cohesion: 0.08
Nodes (22): _ccdf(), _accounts_table(), _after_activity(), _amounts(), _camouflage_transactions(), _collector_payouts(), _contestations(), _fraud_ring() (+14 more)

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
Cohesion: 0.24
Nodes (3): _known_frauds(), _mean_percentile(), _scores()

### Community 94 - "dominant_scores"
Cohesion: 0.13
Nodes (7): Redes neurais para grafos (GNN), dominant_scores(), ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known(), test_sage_learns_the_ring_from_structure_alone()

### Community 96 - "test_experiment.py"
Cohesion: 0.10
Nodes (14): _evaluate(), _evaluate_star(), Prepared, _run_one_seed(), run_seeds(), seeded_models(), all_model_scores(), test_load_scenarios_rejects_unknown_parameter() (+6 more)

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 101 - "SimulationConfig"
Cohesion: 0.14
Nodes (7): _dataset_pequeno(), _day_weights(), SimulationConfig, data(), prepared(), test_graph_detectors_run_on_a_generated_dataset(), test_dataset_without_rings_has_only_legit_accounts()

### Community 103 - "test_anomaly.py"
Cohesion: 0.14
Nodes (10): dbscan(), kmeans(), pca(), test_dbscan_falls_back_to_core_points_on_big_datasets(), test_dbscan_handles_mostly_identical_accounts(), test_detector_flags_outlier(), test_every_detector_returns_aligned_finite_scores(), test_every_detector_survives_few_and_repeated_columns() (+2 more)

### Community 118 - "parametros-dos-experimentos.md"
Cohesion: 0.33
Nodes (4): Configurações, Criar um cenário, Mudar um parâmetro, Parâmetros dos experimentos

## Knowledge Gaps
- **114 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Ao editar notas`, `Código` (+109 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 639 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `flow.py`, `online.py`, `explorer.py`, `external.py`, `evaluate`, `generate_dataset`, `explorador.py`, `draw_graph`, `argparse`, `network.py`, `graph.py`, `out_of_fold_scores`, `plot_model_intervals`, `matplotlib_pyplot`, `temporal.py`, `communities.py`, `Detection`, `plot_heat_graph`, `test_tuning.py`, `patterns.py`, `search_space.py`, `label_spreading`, `build_features`, `build_graph`, `search.py`, `test_bcb.py`, `compare_groups`, `run_detectors`, `main`, `network_summary`, `test_experiment.py`, `SimulationConfig`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _114 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Módulos` be split into smaller, more focused modules?**
  _Cohesion score 0.10685483870967742 - nodes in this community are weakly interconnected._
- **Why does `Resultados` connect `Resultados` to `glossario.md`, `patterns.py`, `run_detectors`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Should `online.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09655172413793103 - nodes in this community are weakly interconnected._
- **Why does `graph_features()` connect `build_features` to `networkx`, `pandas`, `experiment.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Should `explorer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05649350649350649 - nodes in this community are weakly interconnected._