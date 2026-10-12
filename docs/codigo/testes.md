---
tags: [codigo]
---

# Testes

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Como rodar e o que cada grupo cobre: [mapa dos testes](../../tests/mapa-dos-testes.md) · [mapa do código](mapa-do-codigo.md)

## [`test_algorithms.py`](../../tests/test_algorithms.py)

Testes de `pixfraud.algorithms`: caminho gargalo, ramificação máxima, VF2, HITS e similaridade.

- `test_widest_path`
- `test_money_backbone_keeps_main_source`
- `test_laundering_depth_and_longest_chain`
- `test_find_pattern_locates_injected_scatter_gather`
- `test_hits_similarity_and_projection`
- `test_cosine_similarity_is_the_angle_between_vectors`
- `test_similar_accounts_cosine_uses_amounts`

## [`test_anomaly.py`](../../tests/test_anomaly.py)

Testes de `pixfraud.anomaly` e `pixfraud.evaluation`: detectores e métricas.

- `test_detector_flags_outlier`
- `test_every_detector_returns_aligned_finite_scores`
- `test_every_detector_survives_few_and_repeated_columns`
- `test_ecod_uses_both_tails`
- `test_one_class_svm_approximation_on_big_datasets`
- `test_autoencoder_is_reproducible_with_the_seed`
- `test_kmeans_scores_a_small_odd_group_against_the_large_ones`
- `test_pca_flags_the_account_that_breaks_the_correlation`
- `test_evaluate_perfect_ranking`
- `test_dbscan_handles_mostly_identical_accounts`
- `test_dbscan_falls_back_to_core_points_on_big_datasets`
- `test_prepare_matrix_rejects_negative_features`
- `test_local_outlier_factor_flags_the_point_in_the_sparse_region`

## [`test_app.py`](../../tests/test_app.py)

Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver instalado).

- `test_app_runs_all_tabs_with_the_saved_dataset`
- `test_typed_seed_generates_a_new_network`

## [`test_bcb.py`](../../tests/test_bcb.py)

Download dos dados abertos do BCB, sem rede: o `urlopen` é substituído.

- `test_tenta_de_novo_em_504_e_falha_de_conexao`
- `test_desiste_depois_das_tentativas`
- `test_nao_tenta_de_novo_em_erro_definitivo`

## [`test_buscar.py`](../../tests/test_buscar.py)

Testes da busca única (scripts/ferramentas/buscar.py) num cofre e num grafo de código minúsculos.

- `test_normalizar_ignora_acentos_maiusculas_e_separadores`
- `test_termos_tiram_palavras_de_parada_mas_guardam_a_expressao`
- `test_notas_exigem_todos_os_termos_e_poem_o_titulo_na_frente`
- `test_codigo_acha_pelo_nome_e_mostra_so_vizinhos_do_repositorio`
- `test_codigo_citado_conta_as_notas_que_apontam_para_cada_py`

## [`test_communities.py`](../../tests/test_communities.py)

Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e OddBall.

- `test_communities_split_the_cliques`
- `test_participation_and_cores`
- `test_densest_subgraph_finds_planted_clique`
- `test_fraudar_finds_rings_one_after_another`
- `test_fraudar_scores_ignore_a_block_that_is_most_of_the_network`
- `test_oddball_flags_star`
- `test_structural_features_columns`

## [`test_docs.py`](../../tests/test_docs.py)

Testes da documentação: links que funcionam, docstrings, README e mapa em cada pasta.

- `test_every_folder_has_a_readme`
- `test_every_docs_folder_has_a_named_map_note`: As pastas do cofre de pesquisa têm uma nota-mapa com nome próprio (não "README"), porque o Obsidian rotula cada nó do grafo pelo nome do arquivo.
- `test_every_vault_note_has_tags_frontmatter`: Toda nota do cofre tem uma tag (para colorir o grafo); README e estudos/ ficam de fora de propósito (ver docs/obsidian.md).
- `test_relative_links_point_to_existing_files`
- `test_public_code_has_docstrings`
- `test_notes_graph_json_is_up_to_date`: docs/grafo-de-notas.json (o grafo do Obsidian para agentes de IA) acompanha as notas.
- `test_code_docs_are_up_to_date`: docs/codigo/ (uma nota por módulo, pasta de scripts e diretório) acompanha as docstrings.
- `test_every_directory_is_described`: Todo diretório versionado tem uma descrição em documentar_codigo.DIRECTORIES.
- `test_code_graph_leaves_out_private_and_generated_files`: O grafo do Graphify (graphify-out/, ver docs/obsidian.md) não lê o PDF original da proposta (arquivo de submissão) nem dados e resultados gerados.

## [`test_evaluation.py`](../../tests/test_evaluation.py)

Testes de `evaluation.recall_by_group` e `visualization.plot_value_matrix`.

- `test_recall_by_group`
- `test_plot_value_matrix`
- `test_ranking_metrics`
- `test_formatters_use_decimal_comma`
- `test_standard_result_figures`

## [`test_experiment.py`](../../tests/test_experiment.py)

Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários.

- `test_run_seeds_one_dataset_per_seed`
- `test_seeded_models_reach_every_random_detector`
- `test_run_seeds_in_parallel_gives_the_same_results`
- `test_run_seeds_can_run_only_some_detectors`
- `test_comparisons_use_known_feature_sets`
- `test_repository_scenarios_are_valid`
- `test_load_scenarios_rejects_unknown_parameter`
- `test_save_metadata`
- `test_feature_ablation_finds_the_informative_feature`
- `test_supervised_scores_are_out_of_fold`
- `test_known_fraud_scores_learn_from_a_few_known`
- `test_supervised_scores_rejects_unknown_model`

## [`test_exploration.py`](../../tests/test_exploration.py)

Testes de `pixfraud.exploration`: o que o explorador interativo calcula.

- `test_network_summary_counts_by_hand`
- `test_top_k_outcome_sorts_hits_misses_and_false_alarms`
- `test_rank_models_orders_each_group_by_ap_and_feeds_the_picker`
- `test_generate_network_is_reproducible_and_follows_the_scenario`

## [`test_explorer.py`](../../tests/test_explorer.py)

Testes de `pixfraud.explorer`: layout por comunidades e página da rede inteira.

- `test_community_layout_keeps_groups_apart`
- `test_ring_accounts_are_drawn_in_the_center`
- `test_payload_and_page`
- `test_several_risk_models_go_to_the_model_picker`

## [`test_external.py`](../../tests/test_external.py)

Testes de `pixfraud.external`: AMLworld e PaySim com arquivos de exemplo embutidos.

- `test_load_amlworld`
- `test_load_paysim`
- `test_amlworld_payment_formats`
- `test_load_amlworld_patterns`
- `test_time_windows_relabel_each_window`

## [`test_features.py`](../../tests/test_features.py)

Testes de `pixfraud.features`: cada atributo conferido à mão num grafo pequeno.

- `test_graph_aggregates_repeated_pairs`
- `test_features`

## [`test_flow.py`](../../tests/test_flow.py)

Testes de `pixfraud.flow`: fluxo máximo, corte mínimo, contas a bloquear e propagação de risco.

- `test_max_flow_equals_min_cut`
- `test_single_source_is_limited_by_its_route`
- `test_blocking_accounts`
- `test_propagate_risk_reaches_ring_members`
- `test_label_spreading_pulls_toward_known_sides`
- `test_label_spreading_reaches_ring_members`

## [`test_gnn.py`](../../tests/test_gnn.py)

Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]").

- `test_sage_learns_the_ring_from_structure_alone`
- `test_sage_finds_the_rest_of_the_ring_from_a_few_known`
- `test_dominant_scores_are_aligned_and_flag_the_ring`
- `test_dominant_refuses_graphs_that_would_not_fit`

## [`test_gnn_direcionada.py`](../../tests/test_gnn_direcionada.py)

Testes da GraphSAGE direcionada de `pixfraud.gnn` (`graphsage_scores`). Pulados sem o `torch_geometric`.

- `test_graphsage_is_available`
- `test_graphsage_beats_chance_and_covers_every_account`
- `test_graphsage_is_reproducible_with_the_seed`

## [`test_graph_models.py`](../../tests/test_graph_models.py)

Testes de `pixfraud.graph_models` e de `communities.peeling_scores`: detectores que só olham o grafo.

- `test_peeling_scores_put_the_dense_block_on_top`
- `test_peeling_scores_give_each_block_its_own_level`
- `test_densest_subgraph_still_finds_the_block`
- `test_fraudar_detector_marks_the_block`
- `test_node2vec_embedding_is_reproducible`
- `test_node2vec_embedding_handles_isolated_accounts`
- `test_graph_detectors_run_on_a_generated_dataset`
- `test_node2vec_isolation_forest_returns_one_score_per_account`

## [`test_graph_tools.py`](../../tests/test_graph_tools.py)

Testes de `pixfraud.graph`: criação de grafos, trilha do dinheiro e resumo.

- `test_graph_from_edges_aggregates_or_keeps_parallel_edges`
- `test_graph_from_csv_example`
- `test_adjacency_matrix_sums_are_degrees`
- `test_money_trail_directions`
- `test_describe`

## [`test_network.py`](../../tests/test_network.py)

Testes de `pixfraud.network`: lei de potência, componente gigante e passeios aleatórios.

- `test_degree_sequence_counts_distinct_partners`
- `test_power_law_fit_recovers_exponent`
- `test_barabasi_albert_is_more_heavy_tailed_than_erdos_renyi`
- `test_giant_component_weak_and_strong`
- `test_random_walk_follows_money_until_a_sink`
- `test_walks_from_victims_end_at_collectors`
- `test_compare_network_models`

## [`test_online.py`](../../tests/test_online.py)

Testes de `pixfraud.online`: dinheiro recuperado calculado à mão e pontos de corte.

- `test_recovered_amount`
- `test_blocked_mule_keeps_money_that_arrives_later`
- `test_exposure_and_first_flags`
- `test_relevant_checkpoints_skip_quiet_periods`
- `test_checkpoint_flags_budget`

## [`test_patterns.py`](../../tests/test_patterns.py)

Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num grafo.

- `test_patterns_are_well_formed`
- `test_chain_loses_fee_at_each_hop`
- `test_cycle_is_strongly_connected`
- `test_mule_ring_money_reaches_collector`
- `test_inject_maps_victims_to_existing_accounts`
- `test_flow_layout_and_exports`

## [`test_pipeline.py`](../../tests/test_pipeline.py)

Teste de fumaça: o pipeline completo roda de ponta a ponta num dataset pequeno.

- `test_pipeline_end_to_end`

## [`test_scripts.py`](../../tests/test_scripts.py)

Testes de fumaça dos scripts de avaliação, num dataset minúsculo.

- `test_avaliar_cenarios`
- `test_avaliar_robustez`
- `test_gerar_dataset_sorteia_semente_e_reproduz_com_seed`
- `test_reproduzir_tudo_lista_as_etapas_em_ordem`
- `test_reproduzir_tudo_extras_vem_depois_e_mostram_tempo`
- `test_reproduzir_tudo_roda_so_as_etapas_pedidas`
- `test_validar_realismo`
- `test_inferencia_atributos`
- `test_ilustrar_testes`
- `test_avaliar_externo`
- `test_avaliar_deteccao_online`
- `test_avaliar_atributos`
- `test_avaliar_propagacao`
- `test_avaliar_modelos`
- `test_avaliar_fraudar`
- `test_avaliar_gnn`
- `test_avaliar_gnn_rotulos`
- `test_gerar_relatorio`
- `test_investigar_falsos_positivos`
- `test_auditar_papeis`
- `test_gerar_dataset_com_estrutura_aleatoria`

## [`test_simulation.py`](../../tests/test_simulation.py)

Testes de `pixfraud.simulation`: reprodutibilidade, rótulos e parâmetros de realismo.

- `test_same_seed_gives_same_dataset`
- `test_transactions_reference_known_accounts`
- `test_no_self_transfers_and_positive_amounts`
- `test_rings_have_expected_roles`
- `test_fraudulent_money_reaches_collectors`
- `test_dataset_without_rings_has_only_legit_accounts`
- `test_repository_config_is_valid`
- `test_with_overrides_validates_names`
- `test_commercial_hours_remove_the_night_signal`
- `test_commercial_hours_also_apply_to_slow_forwards`
- `test_activity_clock`
- `test_fraud_account_age_follows_parameter`
- `test_quiet_people_send_fewer_pix`
- `test_collector_payouts_off_by_default_keeps_dataset`
- `test_collector_payouts_empties_the_collector`
- `test_collector_payouts_and_cashout_are_alternatives`
- `test_realism_parameters_off_keep_the_original_dataset`
- `test_calibrated_scenario_matches_bcb_numbers`
- `test_look_alike_transactions_are_legitimate`
- `test_recruited_mules_keep_their_legit_history`
- `test_collectors_cash_out_to_a_merchant`
- `test_contestations_come_later_and_only_for_scams`
- `test_contestation_column_survives_save_and_load`
- `test_laundering_typologies_have_their_shape`
- `test_weekly_calendar_has_quieter_weekends`
- `test_invalid_realism_parameters_are_rejected`
- `test_every_role_matches_what_the_account_did`
- `test_audit_catches_a_wrong_role`
- `test_random_structure_off_draws_nothing`
- `test_random_structure_varies_with_the_seed`

## [`test_stats.py`](../../tests/test_stats.py)

Testes de `pixfraud.stats`: efeito, correções, bootstrap, testes pareados, modelo nulo, Kruskal-Wallis,
Dunn, Friedman e testes contra o acaso.

- `test_cliffs_delta_and_labels`
- `test_holm_correction`
- `test_compare_groups_finds_the_separating_feature`
- `test_bootstrap_metric_perfect_ranking`
- `test_paired_comparison_and_summary`
- `test_compare_runs_and_summary_by_scenario`
- `test_compare_runs_between_models`
- `test_null_model_detects_excess_reciprocity`
- `test_contingency_test`
- `test_kruskal_groups_matches_scipy_and_ranks_by_effect`
- `test_dunn_posthoc_finds_the_pairs_that_differ`
- `test_friedman_models_matches_scipy_and_gives_the_critical_difference`
- `test_permutation_and_hypergeometric_tests_against_chance`

## [`test_temporal.py`](../../tests/test_temporal.py)

Testes de `pixfraud.temporal`: caminhos que respeitam a ordem dos Pix.

- `test_backward_reachability_respects_time`
- `test_forward_reachability_gives_earliest_arrival`
- `test_trail_with_max_delay_and_hops`
- `test_dwell_time_and_windows`
- `test_temporal_features`

## [`test_tuning.py`](../../tests/test_tuning.py)

Testes de `pixfraud.tuning` (busca de hiperparâmetros) e da organização de `pixfraud.models`.

- `test_old_modules_reexport_the_same_models`
- `test_every_grid_names_real_models_and_parameters`
- `test_grid_and_candidates_include_the_current_config_once`
- `test_param_goes_beyond_the_edge_with_the_same_step_and_stops_at_the_limit`
- `test_expand_only_touches_parameters_whose_winner_is_at_an_edge`
- `test_choose_keeps_the_current_config_on_a_tie`
- `test_score_candidates_on_a_small_network`
