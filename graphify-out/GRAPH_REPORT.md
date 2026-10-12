# Graph Report - deteccao-fraudes-pix-grafos  (2026-10-12)

## Corpus Check
- 193 files · ~111,723 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .bib 1)

## Summary
- 1656 nodes · 3820 edges · 87 communities (83 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 248 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `193a02ba`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- load_dataset
- algorithms.py
- test_scripts.py
- flow.py
- test_online.py
- explorer.py
- external.py
- test_docs.py
- main
- unsupervised/__init__.py
- Series
- generate_dataset
- explorador.py
- draw_graph
- with_overrides
- autoencoder.py
- compare_network_models
- glossario.md
- _run
- test_graph_tools.py
- buscar.py
- evaluate
- model_label
- mapa-da-pesquisa.md
- plot_value_matrix
- temporal.py
- communities.py
- mapa-dos-modelos.md
- test_communities.py
- pixfraud
- flow_layout
- simulation.py
- pytest
- search_space.py
- patterns.py
- contingency_test
- label_spreading
- build_features
- graph_from_csv
- test_experiment.py
- fluxo-da-pesquisa.md
- _animacao
- test_patterns.py
- test_algorithms.py
- Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning
- Cola: teoria dos grafos × NetworkX
- test_bcb.py
- guia-do-explorador.md
- Modelos usados na pesquisa (e outros que caberiam)
- explain_account
- Detection
- structural_features
- holm_correction
- graphsage_directed.py
- compare_groups
- test_stats.py
- detect_communities
- test_graph_models.py
- compare_with_reference
- _mean_percentile
- ecod.py
- _plot
- cosine_similarity
- Modelos
- paired_comparison
- Testes de hipótese para classificadores
- _profile
- _plot_share
- kruskal_groups
- null_model_test
- bcb_reference
- average-precision.md
- _attach_roles
- _known_frauds
- _git
- Instruções para agentes
- Glossário
- DataFrame
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- gnn.py
- Módulos
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- SimulationConfig
- test_anomaly.py

## God Nodes (most connected - your core abstractions)
1. `generate_dataset()` - 65 edges
2. `Módulos` - 55 edges
3. `Detection` - 36 edges
4. `SimulationConfig` - 33 edges
5. `prepare_matrix()` - 32 edges
6. `build_graph()` - 28 edges
7. `prepare()` - 27 edges
8. `with_overrides()` - 27 edges
9. `load_scenarios()` - 25 edges
10. `load_config()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `Grafo direcionado ponderado` --references--> `build_graph()`  [INFERRED]
  docs/glossario/grafo-direcionado-ponderado.md → src/pixfraud/graph.py
- `Outros modelos que caberiam nesta pesquisa` --references--> `Detection`  [INFERRED]
  docs/modelos.md → src/pixfraud/models/base.py
- `Escrevendo um teste novo` --references--> `SimulationConfig`  [INFERRED]
  tests/mapa-dos-testes.md → src/pixfraud/simulation.py
- `Intervalo de confiança (IC 95%)` --references--> `summarize_runs()`  [INFERRED]
  docs/glossario/intervalo-de-confianca.md → src/pixfraud/stats.py
- `Um modelo é melhor que outro?` --references--> `compare_runs()`  [INFERRED]
  docs/glossario/testes-para-classificadores.md → src/pixfraud/stats.py

## Import Cycles
- 4-file cycle: `src/pixfraud/models/__init__.py -> src/pixfraud/models/unsupervised/__init__.py -> src/pixfraud/models/unsupervised/neural/__init__.py -> src/pixfraud/models/unsupervised/neural/dominant.py -> src/pixfraud/models/__init__.py`

## Communities (87 total, 4 thin omitted)

### Community 0 - "load_dataset"
Cohesion: 0.11
Nodes (18): main(), main(), _check_saved_dataset(), Avisa se ``data_dir`` não é o dataset da semente do YAML (o do explorador da…, draw_structure(), load_dataset(), _negative_binomial(), Path (+10 more)

### Community 1 - "algorithms.py"
Cohesion: 0.11
Nodes (24): heapq, itertools, networkx_algorithms, _amounts(), bipartite_projection(), find_pattern(), hubs_authorities(), laundering_depth() (+16 more)

### Community 2 - "test_scripts.py"
Cohesion: 0.06
Nodes (56): csv, datetime, os, 2. Exploração, 3. Modelos, 4. Avaliação, 5. Interpretação, Ferramentas (+48 more)

### Community 3 - "flow.py"
Cohesion: 0.20
Nodes (18): Fluxo máximo e corte mínimo, main(), _as_list(), blocking_accounts(), blocking_cut(), _flow_network(), max_money_flow(), DiGraph (+10 more)

### Community 4 - "test_online.py"
Cohesion: 0.09
Nodes (26): DatetimeIndex, _metrics(), _plot(), DataFrame, Path, Series, Timedelta, Painéis modelo × métrica; em cada um, conjunto de atributos (e oráculo) ×… (+18 more)

### Community 5 - "explorer.py"
Cohesion: 0.11
Nodes (28): html, math, community_layout(), explorer_payload(), _first_days(), _free_spot(), network_explorer_html(), _place_center() (+20 more)

### Community 6 - "external.py"
Cohesion: 0.12
Nodes (30): main(), _account(), _account_id(), _accounts_table(), _amlworld_chunk(), load_amlworld(), load_amlworld_patterns(), load_paysim() (+22 more)

### Community 7 - "test_docs.py"
Cohesion: 0.07
Nodes (37): ast, Abrir, Busca única nos dois grafos, Cores do grafo, por tipo de nota, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais) (+29 more)

### Community 8 - "main"
Cohesion: 0.19
Nodes (15): _chance_table(), _evaluate(), _evaluate_star(), main(), _plot_comparisons(), _plot_critical_difference(), _plot_models(), DataFrame (+7 more)

### Community 9 - "unsupervised/__init__.py"
Cohesion: 0.12
Nodes (16): sklearn_ensemble, sklearn_kernel_approximation, sklearn_linear_model, sklearn_svm, Modelos de **fronteira**: uma superfície envolve as contas normais, e a…, one_class_svm(), DataFrame, One-Class SVM (Schölkopf et al., 2001): uma fronteira que envolve a maior parte… (+8 more)

### Community 10 - "Series"
Cohesion: 0.22
Nodes (10): Bootstrap, bootstrap_metric(), permutation_test_metric(), Series, Estimativa pontual e IC por bootstrap percentil de uma métrica de desempenho.…, O modelo é melhor que o acaso? Teste de permutação da métrica. Embaralha o…, Fraudes entre as ``k`` contas de maior escore contra um sorteio de ``k``…, topk_hypergeom() (+2 more)

### Community 11 - "generate_dataset"
Cohesion: 0.08
Nodes (27): hashlib, generate_dataset(), _has_look_alikes(), Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., calibrated(), dataset(), fixture, parametrize (+19 more)

### Community 12 - "explorador.py"
Cohesion: 0.05
Nodes (39): explorer_page(), model_scores(), network(), network_title(), DataFrame, Series, Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório (só…, Papel de cada conta, com as vítimas de golpe destacadas como ``vitima``. (+31 more)

### Community 13 - "draw_graph"
Cohesion: 0.21
Nodes (15): draw_graph(), _format_amount(), graph_html(), _layout(), _node_colors(), Graph, Path, Cor (hex) de cada vértice e itens de legenda ``{categoria: cor}``. ``color_by``… (+7 more)

### Community 14 - "with_overrides"
Cohesion: 0.14
Nodes (41): main(), main(), main(), main(), main(), _evaluate(), main(), Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,… (+33 more)

### Community 15 - "autoencoder.py"
Cohesion: 0.22
Nodes (8): sklearn_exceptions, sklearn_neural_network, autoencoder(), DataFrame, Autoencoder: uma rede neural que aprendeu a reconstruir as contas típicas erra…, Autoencoder: a conta que a rede não consegue reconstruir é anômala. Uma rede…, Redes neurais **de reconstrução**: aprendem a reconstruir as contas típicas e…, test_autoencoder_is_reproducible_with_the_seed()

### Community 16 - "compare_network_models"
Cohesion: 0.07
Nodes (39): Componente gigante, _ccdf(), _degree_graphs(), _measure(), _plot_degrees(), DataFrame, DiGraph, Graph (+31 more)

### Community 17 - "glossario.md"
Cohesion: 0.16
Nodes (7): Conta laranja (conta de passagem), Grafo direcionado ponderado, MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), PCA (análise de componentes principais), Propagação de risco (culpa por associação), Glossário

### Community 18 - "_run"
Cohesion: 0.14
Nodes (14): _draws(), _one_seed(), _paired_needs(), _plot(), DataFrame, Path, Diferença pareada média de cada comparação e o nº de sementes para detectá-la.…, Menor nº de sementes para um teste t pareado detectar o efeito padronizado… (+6 more)

### Community 19 - "test_graph_tools.py"
Cohesion: 0.17
Nodes (12): adjacency_matrix(), describe(), DataFrame, Graph, Series, Resumo das propriedades básicas do grafo (útil para conferir exercícios)., Matriz de adjacência rotulada: linha = origem, coluna = destino. Com…, Testes de `pixfraud.graph`: criação de grafos, trilha do dinheiro e resumo. (+4 more)

### Community 20 - "buscar.py"
Cohesion: 0.07
Nodes (37): collections, importlib_util, buscar_codigo(), buscar_notas(), _carregar_exportador(), _casa(), codigo_citado(), grafo_velho() (+29 more)

### Community 21 - "evaluate"
Cohesion: 0.06
Nodes (46): ClassifierMixin, Average precision (AP), Precision@k, HistGradientBoostingClassifier, RandomForestClassifier, sklearn_base, evaluate(), DataFrame (+38 more)

### Community 22 - "model_label"
Cohesion: 0.23
Nodes (12): format_ci(), format_number(), model_label(), plot_differences(), plot_model_intervals(), Nome legível de um modelo, o mesmo em todas as figuras e tabelas., Número com vírgula decimal, como no resto da documentação (``0,58``)., Média e intervalo de confiança no formato único dos resultados: ``0,58 [0,52;… (+4 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.12
Nodes (11): Configurações, Criar um cenário, Mudar um parâmetro, Parâmetros dos experimentos, Cronograma, Mapa da pesquisa, Trilha de estudos, Convenções (+3 more)

### Community 24 - "plot_value_matrix"
Cohesion: 0.05
Nodes (48): categorical_variables(), _plot_roles(), DataFrame, Path, Series, Variáveis sim/não de cada conta, para cruzar com o gabarito., Por (cenário, atributo): efeito médio, IC 95% t entre as sementes e em quantas…, Matriz atributo × cenário do ε² médio do Kruskal-Wallis entre os papéis. (+40 more)

### Community 25 - "temporal.py"
Cohesion: 0.10
Nodes (31): Caminho temporal, Tempo de permanência (dwell time), _best_hops(), _check_direction(), dwell_time(), DataFrame, DiGraph, Series (+23 more)

### Community 26 - "communities.py"
Cohesion: 0.15
Nodes (26): Coeficiente de participação, K-núcleo (core number), community_summary(), core_numbers(), _densest(), densest_subgraph(), _fraudar_weighted(), participation_coefficient() (+18 more)

### Community 27 - "mapa-dos-modelos.md"
Cohesion: 0.16
Nodes (6): DBSCAN e k-distance, Detecção conformal (p-valor por conta), Isolation Forest, K-Means, Local Outlier Factor (LOF), Modelos

### Community 28 - "test_communities.py"
Cohesion: 0.20
Nodes (13): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), fraudar_blocks(), fraudar_scores(), Blocos densos um depois do outro, como no FRAUDAR (Hooi et al., 2016). Acha o…, Escore por conta a partir dos blocos do FRAUDAR, para comparar com os…, fixture, Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e… (+5 more)

### Community 30 - "flow_layout"
Cohesion: 0.40
Nodes (4): flow_layout(), reorder(), DiGraph, Posiciona os vértices da esquerda para a direita, no sentido do dinheiro. Só…

### Community 31 - "simulation.py"
Cohesion: 0.06
Nodes (80): argparse, collections_abc, concurrent_futures, copy, dataclasses, importlib_metadata, matplotlib, matplotlib_animation (+72 more)

### Community 32 - "pytest"
Cohesion: 0.33
Nodes (3): pytest, streamlit_testing_v1, Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver…

### Community 33 - "search_space.py"
Cohesion: 0.07
Nodes (49): inspect, json, main(), _score_star(), _write_config(), Otimização de hiperparâmetros: busca em grade que se amplia sozinha, escolhida…, average_precision(), choose() (+41 more)

### Community 34 - "patterns.py"
Cohesion: 0.19
Nodes (20): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), cycle(), fan_in(), fan_out(), inject() (+12 more)

### Community 35 - "contingency_test"
Cohesion: 0.18
Nodes (12): Documentação, Funções em [`stats.py`](../src/pixfraud/stats.py), Implementação, Kruskal-Wallis ou Friedman?, Plano de testes estatísticos, Referências, Regras gerais, Scripts (+4 more)

### Community 36 - "label_spreading"
Cohesion: 0.29
Nodes (6): Modelos **semi-supervisionados**: usam só as poucas fraudes já conhecidas, como…, label_spreading(), DiGraph, Series, Propagação de rótulos com exemplos positivos **e negativos** (Zhou et al.,…, test_label_spreading_pulls_toward_known_sides()

### Community 37 - "build_features"
Cohesion: 0.07
Nodes (32): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+24 more)

### Community 38 - "graph_from_csv"
Cohesion: 0.22
Nodes (10): MultiDiGraph, graph_from_csv(), money_trail(), DiGraph, Path, Lê uma tabela de transações em CSV e monta o grafo. ``source``, ``target`` e…, Subgrafo das contas alcançáveis a partir de ``account`` em até ``max_hops``…, A() (+2 more)

### Community 39 - "test_experiment.py"
Cohesion: 0.05
Nodes (45): Random Forest (como teto supervisionado), Validação cruzada estratificada, 10. Redes neurais para grafos (GNN), 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive, 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial (+37 more)

### Community 40 - "fluxo-da-pesquisa.md"
Cohesion: 0.31
Nodes (3): Intervalo de confiança (IC 95%), Otimização de hiperparâmetros, Semente (aleatória)

### Community 41 - "_animacao"
Cohesion: 0.25
Nodes (11): _animacao(), quadro(), _legenda(), main(), _padroes(), Path, O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora., Itens de legenda só dos papéis que aparecem no desenho, na ordem de ROLE_COLORS. (+3 more)

### Community 42 - "test_patterns.py"
Cohesion: 0.18
Nodes (12): fraud_nodes(), mule_ring(), Graph, Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor)., Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.…, parametrize, Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num…, test_cycle_is_strongly_connected() (+4 more)

### Community 43 - "test_algorithms.py"
Cohesion: 0.22
Nodes (10): longest_chain(), Caminho gargalo: a rota de ``source`` até ``target`` cuja menor aresta é a…, Maior cadeia (caminho mais longo) de um grafo acíclico, como uma trilha de…, widest_path(), graph_from_edges(), Cria um grafo a partir de uma lista de arestas; prático para exemplos e…, Testes de `pixfraud.algorithms`: caminho gargalo, ramificação máxima, VF2, HITS…, test_laundering_depth_and_longest_chain() (+2 more)

### Community 44 - "Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning"
Cohesion: 0.20
Nodes (10): 1. Objetivos do Projeto, 2. Procedimentos Metodológicos, 3. Cronograma, 4. Referências Bibliográficas, Cursos e materiais complementares, Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning, Introdução, Objetivo Geral (+2 more)

### Community 45 - "Cola: teoria dos grafos × NetworkX"
Cohesion: 0.40
Nodes (4): Armadilhas comuns, Cola: teoria dos grafos × NetworkX, Comandos, Glossário

### Community 46 - "test_bcb.py"
Cohesion: 0.12
Nodes (19): io, main(), Baixa estatísticas do PIX da API de dados abertos do Banco Central. Exemplos:…, fetch(), DataFrame, Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. Os…, Baixa um recurso da API em uma única requisição. ``resource`` é um apelido de…, _http() (+11 more)

### Community 47 - "guia-do-explorador.md"
Cohesion: 0.22
Nodes (4): As abas, Escolher a rede, Explorador interativo, Guia do explorador

### Community 48 - "Modelos usados na pesquisa (e outros que caberiam)"
Cohesion: 0.17
Nodes (12): 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), 1. Preparação dos atributos, 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado), 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado), 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado), 5. Louvain e OddBall (dentro dos atributos), 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado), 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado) (+4 more)

### Community 49 - "explain_account"
Cohesion: 0.24
Nodes (10): Axes, Figure, explain_account(), plot_critical_difference(), plot_risk_heatmap(), DataFrame, Series, Heatmap de risco: por que cada conta foi considerada suspeita. As linhas são as… (+2 more)

### Community 50 - "Detection"
Cohesion: 0.09
Nodes (33): scipy_sparse, sklearn_cluster, sklearn_decomposition, sklearn_neighbors, sklearn_preprocessing, Detection, prepare_matrix(), DataFrame (+25 more)

### Community 51 - "structural_features"
Cohesion: 0.24
Nodes (10): Egonet e OddBall, egonet_features(), oddball_scores(), DataFrame, Medidas da egonet (a conta, seus vizinhos e as arestas entre eles). *…, Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010). Em redes reais, as…, Atributos ``STRUCTURAL_EXTRA`` por conta, prontos para ``pixfraud.features``., structural_features() (+2 more)

### Community 52 - "holm_correction"
Cohesion: 0.22
Nodes (9): Correção de Holm, dunn_posthoc(), holm_correction(), _precision_at_k(), ndarray, Teste de Dunn (1964): que pares de grupos diferem, depois de um Kruskal-Wallis…, p-valores ajustados pelo método de Holm-Bonferroni (controla o erro familiar)., test_dunn_posthoc_finds_the_pairs_that_differ() (+1 more)

### Community 53 - "graphsage_directed.py"
Cohesion: 0.12
Nodes (16): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório, sklearn_model_selection, directed_sage() (+8 more)

### Community 54 - "compare_groups"
Cohesion: 0.15
Nodes (13): A ordem das etapas, As pastas seguem as etapas, Cada etapa no projeto, Como está hoje × o ideal, Fluxo da pesquisa, Mapa mental, Por que esta ordem, Delta de Cliff ($\delta$) (+5 more)

### Community 55 - "test_stats.py"
Cohesion: 0.20
Nodes (10): cliffs_delta(), friedman_models(), Teste de Friedman entre vários modelos medidos nas mesmas unidades (sementes).…, Delta de Cliff: P(X > Y) - P(X < Y), de -1 a 1 (0 = distribuições iguais)., Testes de `pixfraud.stats`: efeito, correções, bootstrap, testes pareados,…, _roles_sample(), test_cliffs_delta_and_labels(), test_compare_runs_between_models() (+2 more)

### Community 56 - "detect_communities"
Cohesion: 0.40
Nodes (5): Comunidades e modularidade (Louvain), detect_communities(), Comunidade de cada conta (0 = a maior). ``method="louvain"`` maximiza a…, parametrize, test_communities_split_the_cliques()

### Community 57 - "test_graph_models.py"
Cohesion: 0.10
Nodes (23): Detectores que olham só para a estrutura do grafo, sem a tabela de atributos.…, fraudar(), Graph, FRAUDAR (Hooi et al., 2016): contas em blocos densos, como uma quadrilha, ficam…, FRAUDAR como escore por conta (``communities.peeling_scores``). O núcleo…, Modelos de **estrutura do grafo**: recebem o grafo, não a tabela de atributos.…, node2vec_embedding(), node2vec_isolation_forest() (+15 more)

### Community 58 - "compare_with_reference"
Cohesion: 0.40
Nodes (5): compare_with_reference(), DataFrame, As estatísticas do BCB calculadas numa rede sintética. Golpe é o Pix da vítima…, Para cada (cenário, estatística): média do gerador, IC 95% t, valor do BCB e…, synthetic_statistics()

### Community 59 - "_mean_percentile"
Cohesion: 0.40
Nodes (5): _mean_percentile(), Series, Combinação de métodos: média dos percentis de cada um, nas contas avaliadas., Escore de um detector não supervisionado (não usa as contas conhecidas)., _scores()

### Community 60 - "ecod.py"
Cohesion: 0.22
Nodes (8): scipy_stats, ecod(), DataFrame, ECOD (Li et al., 2022): a conta está na cauda de vários atributos ao mesmo…, ECOD: probabilidade de cauda empírica, atributo por atributo (Li et al., 2022).…, Modelos **estatísticos**: a conta suspeita é rara segundo a distribuição dos…, test_ecod_uses_both_tails(), warnings

### Community 61 - "_plot"
Cohesion: 0.40
Nodes (5): _plot(), DataFrame, Path, model_color(), Cor fixa de um modelo nas figuras (cinza-médio para um modelo sem cor definida).

### Community 62 - "cosine_similarity"
Cohesion: 0.50
Nodes (5): cosine_similarity(), Cosseno do ângulo entre os vetores ``a`` e ``b``. $$\\cos\\theta = \\frac{a…, Ângulo entre ``a`` e ``b``: $\\theta = \\arccos(\\cos\\theta)$, em graus (ou…, vector_angle(), test_cosine_similarity_is_the_angle_between_vectors()

### Community 63 - "Modelos"
Cohesion: 0.17
Nodes (12): As pastas, Cada modelo, Como cada modelo se saiu, Como reproduzir, Modelos, Não supervisionados, O ganho de verdade: nas redes de teste, O que a tabela diz (+4 more)

### Community 64 - "paired_comparison"
Cohesion: 0.50
Nodes (4): Teste de Wilcoxon pareado, paired_comparison(), Compara duas abordagens medidas nas mesmas unidades (ex.: mesmas sementes).…, test_paired_comparison_and_summary()

### Community 65 - "Testes de hipótese para classificadores"
Cohesion: 0.50
Nodes (4): O modelo é melhor que o acaso?, Testes de hipótese para classificadores, Um modelo é melhor que outro?, "É comércio ou não?"

### Community 66 - "_profile"
Cohesion: 0.50
Nodes (4): _profile(), DataFrame, Series, Mediana, por papel, do que as contas fazem: quem paga, quem recebe e quanto…

### Community 67 - "_plot_share"
Cohesion: 0.50
Nodes (4): _plot_share(), DataFrame, Path, Mapa de calor: fração das k primeiras contas de cada modelo que são comércios.

### Community 68 - "kruskal_groups"
Cohesion: 0.50
Nodes (4): epsilon_squared_label(), kruskal_groups(), Rótulo do ε² do Kruskal-Wallis (limiares usuais de η²: 0,01, 0,06 e 0,14)., Kruskal-Wallis de cada atributo entre os grupos de ``groups`` (ex.: o papel da…

### Community 69 - "null_model_test"
Cohesion: 0.50
Nodes (4): null_model_test(), DiGraph, Compara ``statistic(graph)`` com grafos aleatórios de mesmos graus de entrada e…, test_null_model_detects_excess_reciprocity()

### Community 70 - "bcb_reference"
Cohesion: 0.67
Nodes (3): bcb_reference(), Path, As mesmas estatísticas, nos dados abertos do Pix (só agregados, sem dado…

### Community 71 - "average-precision.md"
Cohesion: 0.26
Nodes (4): Classes raras (desbalanceamento), KNN (k vizinhos mais próximos), ROC-AUC, Supervisionado e não supervisionado

### Community 72 - "_attach_roles"
Cohesion: 0.67
Nodes (3): _attach_roles(), DiGraph, Path

### Community 78 - "Instruções para agentes"
Cohesion: 0.25
Nodes (8): Ao editar notas, Autoria, Como se orientar, Código, Git, Instruções para agentes, Regra principal: LGPD no contexto do Pix, head()

### Community 81 - "Glossário"
Cohesion: 0.40
Nodes (5): Avaliação e estatística, Detecção, Glossário, Pix e dados, Teoria dos grafos

### Community 83 - "DataFrame"
Cohesion: 0.09
Nodes (26): 1. Dados, _accounts_table(), _amounts(), audit_roles(), _camouflage_transactions(), _contestations(), _day_weights(), _look_alike_transactions() (+18 more)

### Community 85 - "Documentação da pesquisa"
Cohesion: 0.50
Nodes (4): A pesquisa, Anotações, Documentação da pesquisa, Documentação do código e dos dados

### Community 86 - "A rede Pix dentro do cofre"
Cohesion: 0.40
Nodes (4): A rede Pix dentro do cofre, Como gerar outros recortes, Figuras estáticas, Rede inteira, interativa

### Community 87 - "Revisão bibliográfica"
Cohesion: 0.50
Nodes (4): Como fichar uma leitura, Fichamentos, Revisão bibliográfica, Sugestões de leitura

### Community 94 - "gnn.py"
Cohesion: 0.06
Nodes (42): Redes neurais para grafos (GNN), Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch. Os modelos…, Todos os modelos de detecção, um arquivo por modelo, agrupados por tipo e por…, fit_sage(), GraphSAGE, DataFrame, Graph, ndarray (+34 more)

### Community 96 - "Módulos"
Cohesion: 0.13
Nodes (22): main(), prepare(), Prepared, DataFrame, Repete o experimento com várias sementes. Cada semente gera um dataset…, Tudo o que os detectores precisam, calculado uma vez por dataset (ver…, Monta o grafo e calcula todos os atributos (seção ``atributos`` da…, Roda cada detector (``models``, ou todos de ``DETECTORS``) em cada conjunto de… (+14 more)

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 101 - "SimulationConfig"
Cohesion: 0.11
Nodes (21): _dataset_pequeno(), Dataset com uma única quadrilha, pequeno o bastante para desenhar., build_graph(), Monta o grafo direcionado de transações. Todas as transferências de um mesmo…, propagate_risk(), DiGraph, Series, Culpa por associação: PageRank personalizado a partir das contas ``seeds``. A… (+13 more)

### Community 103 - "test_anomaly.py"
Cohesion: 0.14
Nodes (17): dbscan(), DataFrame, DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.…, pca(), DataFrame, PCA: soma das projeções da conta nas componentes principais, divididas pela…, blob_with_outlier(), fixture (+9 more)

## Knowledge Gaps
- **135 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Ao editar notas`, `Git` (+130 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 714 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `algorithms.py`, `flow.py`, `test_online.py`, `explorer.py`, `external.py`, `generate_dataset`, `explorador.py`, `draw_graph`, `with_overrides`, `compare_network_models`, `test_graph_tools.py`, `evaluate`, `plot_value_matrix`, `temporal.py`, `search_space.py`, `patterns.py`, `build_features`, `graph_from_csv`, `test_algorithms.py`, `test_bcb.py`, `explain_account`, `Detection`, `structural_features`, `compare_groups`, `detect_communities`, `cosine_similarity`, `SimulationConfig`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `evaluate` to `Módulos`, `mapa-dos-modelos.md`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Detection` connect `Detection` to `Módulos`, `test_anomaly.py`, `unsupervised/__init__.py`, `autoencoder.py`, `Modelos usados na pesquisa (e outros que caberiam)`, `evaluate`, `test_graph_models.py`, `ecod.py`, `gnn.py`, `simulation.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 54 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _135 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `load_dataset` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Should `algorithms.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11333333333333333 - nodes in this community are weakly interconnected._