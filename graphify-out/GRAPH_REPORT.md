# Graph Report - deteccao-fraudes-pix-grafos  (2026-10-06)

## Corpus Check
- 135 files · ~84,474 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .bib 1)

## Summary
- 1298 nodes · 3348 edges · 78 communities (64 shown, 14 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `01802a02`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- gnn.py
- Módulos
- undirected_simple
- flow.py
- ilustrar_grafos_de_conhecimento.py
- test_docs.py
- external.py
- buscar.py
- test_evaluation.py
- anomaly.py
- pytest
- generate_dataset
- explorador.py
- draw_graph
- argparse
- explorer.py
- network.py
- glossario.md
- avaliar_sementes.py
- graph.py
- json
- evaluate
- plot_model_intervals
- mapa-da-pesquisa.md
- plot_value_matrix
- pandas
- communities.py
- graph_models.py
- _fraud_ring
- pixfraud
- flow_layout
- save_dataset
- _plot
- patterns.py
- reproduzir_tudo.py
- plot_heat_graph
- build_features
- build_graph
- Resultados
- Graph
- mapa-dos-testes.md
- networkx
- gerar_dataset.py
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- test_bcb.py
- guia-do-explorador.md
- Modelos usados na pesquisa (e outros que caberiam)
- Próximos passos
- prepare_matrix
- _git
- oddball_scores
- _plot_models
- _plot
- effect_size_label
- gerar_relatorio.py
- test_communities.py
- _known_frauds
- average-precision.md
- test_explorer.py
- exportar_grafo_de_notas.py
- Instruções para agentes
- Glossário
- numpy
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- _mean_percentile
- test_gnn.py
- test_experiment.py
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- test_gnn_direcionada.py
- test_anomaly.py
- Reproduzir os resultados
- _DirectedSAGE
- Configurações

## God Nodes (most connected - your core abstractions)
1. `Módulos` - 55 edges
2. `generate_dataset()` - 54 edges
3. `build_graph()` - 27 edges
4. `SimulationConfig` - 27 edges
5. `Detection` - 21 edges
6. `prepare()` - 21 edges
7. `save_metadata()` - 21 edges
8. `main()` - 20 edges
9. `load_experiment_config()` - 20 edges
10. `load_config()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `1. Preparação dos atributos` --references--> `prepare_matrix()`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Random Forest (como teto supervisionado)` --references--> `supervised_scores()`  [INFERRED]
  docs/glossario/random-forest.md → src/pixfraud/experiment.py
- `Validação cruzada estratificada` --references--> `supervised_scores()`  [INFERRED]
  docs/glossario/validacao-cruzada.md → src/pixfraud/experiment.py
- `Propagação de risco (culpa por associação)` --references--> `propagate_risk()`  [INFERRED]
  docs/glossario/propagacao-de-risco.md → src/pixfraud/flow.py
- `6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)` --references--> `propagate_risk()`  [INFERRED]
  docs/modelos.md → src/pixfraud/flow.py

## Import Cycles
- None detected.

## Communities (78 total, 14 thin omitted)

### Community 0 - "gnn.py"
Cohesion: 0.12
Nodes (10): Redes neurais para grafos (GNN), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN), _adjacency(), available(), dominant_scores(), _fit_sage(), graphsage_scores(), _require_torch() (+2 more)

### Community 1 - "Módulos"
Cohesion: 0.10
Nodes (15): _amounts(), cosine_similarity(), find_pattern(), hubs_authorities(), laundering_depth(), longest_chain(), money_backbone(), similar_accounts() (+7 more)

### Community 2 - "undirected_simple"
Cohesion: 0.29
Nodes (5): densest_subgraph(), _fraudar_weighted(), undirected_simple(), test_densest_subgraph_finds_planted_clique(), test_densest_subgraph_still_finds_the_block()

### Community 3 - "flow.py"
Cohesion: 0.13
Nodes (14): Fluxo máximo e corte mínimo, _as_list(), blocking_accounts(), blocking_cut(), _flow_network(), label_spreading(), max_money_flow(), propagate_risk() (+6 more)

### Community 4 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.08
Nodes (18): _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), _rotulo(), checkpoint_flags() (+10 more)

### Community 5 - "test_docs.py"
Cohesion: 0.10
Nodes (17): Abrir, Busca única nos dois grafos, Cores do grafo, por tipo de nota, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais), Por que nenhuma nota se chama "README" (+9 more)

### Community 6 - "external.py"
Cohesion: 0.11
Nodes (17): main(), _account(), _account_id(), _accounts_table(), _amlworld_chunk(), load_amlworld(), load_amlworld_patterns(), load_paysim() (+9 more)

### Community 7 - "buscar.py"
Cohesion: 0.17
Nodes (10): buscar_codigo(), buscar_notas(), _carregar_exportador(), _casa(), codigo_citado(), grafo_velho(), _lista(), main() (+2 more)

### Community 8 - "test_evaluation.py"
Cohesion: 0.20
Nodes (5): ranking_metrics(), recall_by_group(), test_plot_value_matrix(), test_ranking_metrics(), test_recall_by_group()

### Community 9 - "anomaly.py"
Cohesion: 0.10
Nodes (10): 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), Outros modelos que caberiam nesta pesquisa, autoencoder(), Detection, ecod(), one_class_svm(), _top_fraction(), test_autoencoder_is_reproducible_with_the_seed() (+2 more)

### Community 10 - "pytest"
Cohesion: 0.07
Nodes (23): Correção de Holm, Delta de Cliff ($\delta$), Teste de Mann-Whitney, Teste de Wilcoxon pareado, cliffs_delta(), compare_groups(), contingency_test(), holm_correction() (+15 more)

### Community 11 - "generate_dataset"
Cohesion: 0.10
Nodes (19): generate_dataset(), _has_look_alikes(), test_checkpoint_flags_budget(), calibrated(), dataset(), test_collector_payouts_empties_the_collector(), test_collector_payouts_off_by_default_keeps_dataset(), test_commercial_hours_also_apply_to_slow_forwards() (+11 more)

### Community 12 - "explorador.py"
Cohesion: 0.15
Nodes (7): all_metrics(), explorer_page(), load(), prepared(), risk_scores(), roles_with_victims(), with_roles()

### Community 13 - "draw_graph"
Cohesion: 0.11
Nodes (14): _animacao(), quadro(), _legenda(), main(), _padroes(), _rede_exemplo(), draw_graph(), _format_amount() (+6 more)

### Community 14 - "argparse"
Cohesion: 0.14
Nodes (26): main(), main(), _evaluate(), main(), main(), main(), main(), main() (+18 more)

### Community 15 - "explorer.py"
Cohesion: 0.16
Nodes (7): community_layout(), explorer_payload(), _first_days(), _free_spot(), network_explorer_html(), _place_center(), save_network_explorer()

### Community 16 - "network.py"
Cohesion: 0.08
Nodes (18): _ccdf(), _degree_graphs(), _measure(), _plot_degrees(), compare_network_models(), component_summary(), degree_sequence(), fit_power_law() (+10 more)

### Community 17 - "glossario.md"
Cohesion: 0.13
Nodes (8): Conta laranja (conta de passagem), Grafo direcionado ponderado, Intervalo de confiança (IC 95%), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Propagação de risco (culpa por associação), Random Forest (como teto supervisionado), Validação cruzada estratificada

### Community 18 - "avaliar_sementes.py"
Cohesion: 0.15
Nodes (9): _convergence(), _draws(), main(), _one_seed(), _paired_needs(), _plot(), _run(), _seeds_for_power() (+1 more)

### Community 19 - "graph.py"
Cohesion: 0.09
Nodes (13): _attach_roles(), main(), adjacency_matrix(), describe(), graph_from_csv(), graph_from_edges(), money_trail(), test_widest_path() (+5 more)

### Community 20 - "json"
Cohesion: 0.24
Nodes (3): _cofre(), test_codigo_citado_conta_as_notas_que_apontam_para_cada_py(), test_notas_exigem_todos_os_termos_e_poem_o_titulo_na_frente()

### Community 21 - "evaluate"
Cohesion: 0.25
Nodes (7): Average precision (AP), Precision@k, evaluate(), Como as peças se encaixam, Onde mexer para..., `pixfraud`: o código da pesquisa, Referência completa da API

### Community 22 - "plot_model_intervals"
Cohesion: 0.23
Nodes (7): format_ci(), format_number(), model_label(), plot_differences(), plot_model_intervals(), test_formatters_use_decimal_comma(), test_standard_result_figures()

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.14
Nodes (8): Parâmetros dos experimentos, Cronograma, Mapa da pesquisa, Trilha de estudos, Convenções, Notebooks da pesquisa, Mapa dos notebooks, Mapa dos scripts

### Community 24 - "plot_value_matrix"
Cohesion: 0.06
Nodes (12): _plot_ablation(), _plot_ceiling(), _plot_effects(), _plot_metric(), _plot_typologies(), _pool(), _plot(), _plot() (+4 more)

### Community 25 - "pandas"
Cohesion: 0.07
Nodes (37): Caminho temporal, Tempo de permanência (dwell time), _salary_days(), _best_hops(), _check_direction(), dwell_time(), temporal_features(), temporal_reachability() (+29 more)

### Community 26 - "communities.py"
Cohesion: 0.17
Nodes (10): Coeficiente de participação, Comunidades e modularidade (Louvain), K-núcleo (core number), core_numbers(), detect_communities(), participation_coefficient(), _power_law_score(), structural_features() (+2 more)

### Community 27 - "graph_models.py"
Cohesion: 0.11
Nodes (11): peeling_scores(), fraudar(), node2vec_embedding(), node2vec_isolation_forest(), sparse_graph_with_block(), test_fraudar_detector_marks_the_block(), test_node2vec_embedding_handles_isolated_accounts(), test_node2vec_embedding_is_reproducible() (+3 more)

### Community 28 - "_fraud_ring"
Cohesion: 0.18
Nodes (8): _after_activity(), _fraud_ring(), _hops(), _later(), _launder(), _pick_person(), _recruit(), test_activity_clock()

### Community 32 - "save_dataset"
Cohesion: 0.29
Nodes (3): save_dataset(), test_app_runs_all_tabs(), test_contestation_column_survives_save_and_load()

### Community 34 - "patterns.py"
Cohesion: 0.21
Nodes (11): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), cycle(), fan_in(), fan_out(), inject() (+3 more)

### Community 35 - "reproduzir_tudo.py"
Cohesion: 0.16
Nodes (8): abrir(), anotar(), formatar(), graphify(), main(), para_abrir(), plano(), tempos_medios()

### Community 36 - "plot_heat_graph"
Cohesion: 0.24
Nodes (3): explain_account(), plot_heat_graph(), plot_risk_heatmap()

### Community 37 - "build_features"
Cohesion: 0.09
Nodes (21): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+13 more)

### Community 38 - "build_graph"
Cohesion: 0.14
Nodes (11): _dataset_pequeno(), build_graph(), SimulationConfig, data(), test_features(), test_graph_aggregates_repeated_pairs(), test_label_spreading_reaches_ring_members(), test_propagate_risk_reaches_ring_members() (+3 more)

### Community 39 - "Resultados"
Cohesion: 0.11
Nodes (18): 10. Redes neurais para grafos (GNN), 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive, 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial, 16. Próximos passos, 1. Cenário base: o tabular parece bastar (+10 more)

### Community 40 - "Graph"
Cohesion: 0.24
Nodes (8): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), _densest(), fraudar_blocks(), fraudar_scores(), _peel(), test_fraudar_finds_rings_one_after_another(), test_fraudar_scores_ignore_a_block_that_is_most_of_the_network()

### Community 41 - "mapa-dos-testes.md"
Cohesion: 0.33
Nodes (4): Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes

### Community 42 - "networkx"
Cohesion: 0.15
Nodes (10): bipartite_projection(), fraud_nodes(), mule_ring(), test_hits_similarity_and_projection(), test_chain_loses_fee_at_each_hop(), test_cycle_is_strongly_connected(), test_flow_layout_and_exports(), test_inject_maps_victims_to_existing_accounts() (+2 more)

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
Cohesion: 0.29
Nodes (3): Explorador interativo, O que tem, Guia do explorador

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.22
Nodes (9): 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado), Como as peças se encaixam (+1 more)

### Community 49 - "Próximos passos"
Cohesion: 0.33
Nodes (6): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório

### Community 50 - "prepare_matrix"
Cohesion: 0.20
Nodes (8): Isolation Forest, Local Outlier Factor (LOF), isolation_forest(), local_outlier_factor(), prepare_matrix(), test_evaluate_perfect_ranking(), test_local_outlier_factor_flags_the_point_in_the_sparse_region(), test_prepare_matrix_rejects_negative_features()

### Community 52 - "oddball_scores"
Cohesion: 0.33
Nodes (4): Egonet e OddBall, egonet_features(), oddball_scores(), test_oddball_flags_star()

### Community 59 - "test_communities.py"
Cohesion: 0.22
Nodes (3): community_summary(), test_communities_split_the_cliques(), two_cliques()

### Community 71 - "average-precision.md"
Cohesion: 0.29
Nodes (3): Classes raras (desbalanceamento), Glossário, ROC-AUC

### Community 74 - "test_explorer.py"
Cohesion: 0.40
Nodes (3): test_community_layout_keeps_groups_apart(), test_payload_and_page(), test_ring_accounts_are_drawn_in_the_center()

### Community 77 - "exportar_grafo_de_notas.py"
Cohesion: 0.22
Nodes (5): como_json(), _filtros_do_cofre(), grafo_de_notas(), main(), notas_do_cofre()

### Community 78 - "Instruções para agentes"
Cohesion: 0.29
Nodes (7): Ao editar notas, Autoria, Como se orientar, Código, Instruções para agentes, Regra principal: LGPD no contexto do Pix, head()

### Community 81 - "Glossário"
Cohesion: 0.40
Nodes (5): Avaliação e estatística, Detecção, Glossário, Pix e dados, Teoria dos grafos

### Community 83 - "numpy"
Cohesion: 0.12
Nodes (14): Bootstrap, _accounts_table(), _amounts(), _camouflage_transactions(), _collector_payouts(), _contestations(), _day_weights(), _look_alike_transactions() (+6 more)

### Community 85 - "Documentação da pesquisa"
Cohesion: 0.50
Nodes (4): A pesquisa, Anotações, Documentação da pesquisa, Documentação do código e dos dados

### Community 86 - "A rede Pix dentro do cofre"
Cohesion: 0.40
Nodes (4): A rede Pix dentro do cofre, Como gerar outros recortes, Figuras estáticas, Rede inteira, interativa

### Community 87 - "Revisão bibliográfica"
Cohesion: 0.50
Nodes (4): Como fichar uma leitura, Fichamentos, Revisão bibliográfica, Sugestões de leitura

### Community 94 - "test_gnn.py"
Cohesion: 0.22
Nodes (5): ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known(), test_sage_learns_the_ring_from_structure_alone()

### Community 96 - "test_experiment.py"
Cohesion: 0.09
Nodes (19): feature_ablation(), known_fraud_scores(), Prepared, run_detectors(), _run_one_seed(), run_seeds(), supervised_scores(), _planted() (+11 more)

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 103 - "test_anomaly.py"
Cohesion: 0.21
Nodes (8): DBSCAN e k-distance, dbscan(), blob_with_outlier(), test_dbscan_falls_back_to_core_points_on_big_datasets(), test_dbscan_handles_mostly_identical_accounts(), test_detector_flags_outlier(), test_every_detector_returns_aligned_finite_scores(), test_every_detector_survives_few_and_repeated_columns()

### Community 107 - "Reproduzir os resultados"
Cohesion: 0.67
Nodes (3): Mapa, Reproduzir os resultados, Scripts

### Community 116 - "_DirectedSAGE"
Cohesion: 0.22
Nodes (3): _DirectedSAGE(), __init__(), _GraphSAGE

### Community 118 - "Configurações"
Cohesion: 0.67
Nodes (3): Configurações, Criar um cenário, Mudar um parâmetro

## Knowledge Gaps
- **93 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Ao editar notas`, `Código` (+88 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 506 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `gnn.py`, `flow.py`, `ilustrar_grafos_de_conhecimento.py`, `external.py`, `test_evaluation.py`, `anomaly.py`, `pytest`, `generate_dataset`, `draw_graph`, `argparse`, `explorer.py`, `network.py`, `graph.py`, `evaluate`, `plot_value_matrix`, `pandas`, `communities.py`, `graph_models.py`, `patterns.py`, `plot_heat_graph`, `build_features`, `build_graph`, `test_bcb.py`, `prepare_matrix`, `oddball_scores`, `test_experiment.py`, `test_anomaly.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 54 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _93 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `gnn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12169312169312169 - nodes in this community are weakly interconnected._
- **Why does `propagate_risk()` connect `flow.py` to `Módulos`, `build_graph`, `Resultados`, `networkx`, `argparse`, `Modelos usados na pesquisa (e outros que caberiam)`, `glossario.md`, `Próximos passos`, `pandas`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `Módulos` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Why does `generate_dataset()` connect `generate_dataset` to `test_experiment.py`, `Módulos`, `save_dataset`, `test_gnn_direcionada.py`, `build_graph`, `gerar_dataset.py`, `explorador.py`, `argparse`, `numpy`, `pandas`, `_fraud_ring`, `experiment.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._