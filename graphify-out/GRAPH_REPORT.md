# Graph Report - deteccao-fraudes-pix-grafos  (2026-09-29)

## Corpus Check
- 183 files · ~94,954 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .csv 2, .bib 1)

## Summary
- 1610 nodes · 3356 edges · 108 communities (104 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78e4bccb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- gnn.py
- similar_accounts
- detect_communities
- graph_from_csv
- pathlib
- test_docs.py
- Módulos
- main
- fraudar_scores
- test_anomaly.py
- compare_runs
- generate_dataset
- load
- draw_graph
- load_experiment_config
- explorer_payload
- main
- resultados.md
- main
- prepare
- pandas
- save_dataset
- main
- mapa-da-pesquisa.md
- plot_value_matrix
- build_graph
- mapa-das-leituras.md
- 10. Modelos integrados em 29/09 (implementados, ainda sem resultados)
- experiment.py
- pixfraud
- test_scripts.py
- visualization.py
- test_algorithms.py
- Graph
- patterns.py
- reproduzir_tudo.py
- mapa-do-relatorio.md
- build_features
- ilustrar_grafos_de_conhecimento.py
- Resultados
- anomaly.py
- mapa-dos-testes.md
- test_patterns.py
- _fraud_ring
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
- two_cliques
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
- _normal_transactions
- Ideias futuras
- Documentação da pesquisa
- A rede Pix dentro do cofre
- Revisão bibliográfica
- main
- diario-de-pesquisa.md
- SimulationConfig
- Notas da pesquisa no Obsidian
- argparse
- _fit_sage
- test_gnn.py
- oddball_scores
- test_experiment.py
- Diário 2026-09-26
- Diário 2026-09-29
- community_layout
- Estudos: teoria dos grafos aplicada a fraudes no Pix
- test_gnn_direcionada.py
- algorithms.py
- _look_alike_transactions
- Próximos passos
- Diário 2026-09-22
- Reproduzir os resultados

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
- `1. Preparação dos atributos` --references--> `prepare_matrix()`  [INFERRED]
  docs/modelos.md → src/pixfraud/anomaly.py
- `Próximo passo` --references--> `densest_subgraph()`  [INFERRED]
  docs/diario/2026-09-22.md → src/pixfraud/communities.py
- `6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)` --references--> `propagate_risk()`  [INFERRED]
  docs/modelos.md → src/pixfraud/flow.py
- `Pesquisa` --references--> `propagate_risk()`  [INFERRED]
  docs/proximos-passos.md → src/pixfraud/flow.py
- `O que cada arquivo testa` --references--> `graphsage_scores()`  [INFERRED]
  tests/mapa-dos-testes.md → src/pixfraud/gnn.py

## Import Cycles
- None detected.

## Communities (108 total, 4 thin omitted)

### Community 0 - "gnn.py"
Cohesion: 0.14
Nodes (23): Redes neurais para grafos (GNN), 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN), Index, sklearn_model_selection, _adjacency(), available(), dominant_scores(), graphsage_scores() (+15 more)

### Community 1 - "similar_accounts"
Cohesion: 0.16
Nodes (16): _amounts(), bipartite_projection(), hubs_authorities(), laundering_depth(), DataFrame, DiGraph, Graph, Series (+8 more)

### Community 2 - "detect_communities"
Cohesion: 0.17
Nodes (16): Coeficiente de participação, Comunidades e modularidade (Louvain), K-núcleo (core number), core_numbers(), detect_communities(), participation_coefficient(), _power_law_score(), Series (+8 more)

### Community 3 - "graph_from_csv"
Cohesion: 0.06
Nodes (45): Decisões (e por quê), Diário 2026-09-21, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Fluxo máximo e corte mínimo, MultiDiGraph (+37 more)

### Community 4 - "pathlib"
Cohesion: 0.09
Nodes (27): Explorador interativo da pesquisa (Streamlit). Rodar na raiz do repositório:…, collections_abc, html, json, matplotlib_animation, networkx, pathlib, pytest (+19 more)

### Community 5 - "test_docs.py"
Cohesion: 0.15
Nodes (16): ast, O que fiz, Cores do grafo, por tipo de nota, importlib_util, re, parametrize, Testes da documentação: links que funcionam, docstrings, README e mapa em cada…, As pastas do cofre de pesquisa têm uma nota-mapa com nome próprio (não… (+8 more)

### Community 6 - "Módulos"
Cohesion: 0.07
Nodes (48): Average precision (AP), Precision@k, main(), evaluate(), DataFrame, Series, ranking_metrics(), Todas as métricas do módulo para uma detecção; ``k`` padrão = nº de fraudes… (+40 more)

### Community 7 - "main"
Cohesion: 0.06
Nodes (44): DatetimeIndex, Explicabilidade para auditoria, O que existe hoje, O que falta, Onde entraria no código, Por que importa para esta pesquisa especificamente, Custo operacional, não só AP e precision@k, Grafos heterogêneos (+36 more)

### Community 8 - "fraudar_scores"
Cohesion: 0.39
Nodes (8): FRAUDAR, 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura), fraudar_blocks(), fraudar_scores(), Blocos densos um depois do outro, como no FRAUDAR (Hooi et al., 2016). Acha o…, Escore por conta a partir dos blocos do FRAUDAR, para comparar com os…, test_fraudar_finds_rings_one_after_another(), test_fraudar_scores_ignore_a_block_that_is_most_of_the_network()

### Community 9 - "test_anomaly.py"
Cohesion: 0.09
Nodes (36): DBSCAN e k-distance, Isolation Forest, Local Outlier Factor (LOF), Outros modelos que caberiam nesta pesquisa, autoencoder(), dbscan(), Detection, ecod() (+28 more)

### Community 10 - "compare_runs"
Cohesion: 0.06
Nodes (43): Bootstrap, Correção de Holm, Delta de Cliff ($\delta$), Intervalo de confiança (IC 95%), Teste de Mann-Whitney, Teste de Wilcoxon pareado, _evaluate(), Roda cada cenário com ``n_seeds`` sementes; devolve execuções, resumo,… (+35 more)

### Community 11 - "generate_dataset"
Cohesion: 0.09
Nodes (20): hashlib, generate_dataset(), _has_look_alikes(), Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``., calibrated(), dataset(), fixture, parametrize (+12 more)

### Community 12 - "load"
Cohesion: 0.16
Nodes (18): all_metrics(), explorer_page(), load(), prepared(), DataFrame, Series, Cópia do grafo com o atributo ``role`` em cada vértice (para colorir os…, Contas e Pix da pasta; gera o dataset sintético se ela ainda estiver vazia. (+10 more)

### Community 13 - "draw_graph"
Cohesion: 0.06
Nodes (51): Axes, Figure, _plot_comparisons(), _plot_models(), DataFrame, Path, Series, Um painel por cenário: cada modelo com a AP média e o IC 95%, agrupados por… (+43 more)

### Community 14 - "load_experiment_config"
Cohesion: 0.08
Nodes (37): main(), _plot(), DataFrame, Path, Matriz método × cenário da AP média., main(), _plot(), DataFrame (+29 more)

### Community 15 - "explorer_payload"
Cohesion: 0.20
Nodes (15): main(), explorer_payload(), _first_days(), network_explorer_html(), DataFrame, DiGraph, Path, Series (+7 more)

### Community 16 - "main"
Cohesion: 0.07
Nodes (40): _ccdf(), _degree_graphs(), main(), _measure(), _plot_degrees(), DataFrame, DiGraph, Graph (+32 more)

### Community 17 - "resultados.md"
Cohesion: 0.13
Nodes (6): Classes raras (desbalanceamento), Conta laranja (conta de passagem), MED (Mecanismo Especial de Devolução), Pass-through (dinheiro que atravessa a conta), Glossário, ROC-AUC

### Community 18 - "main"
Cohesion: 0.13
Nodes (18): _convergence(), _draws(), main(), _one_seed(), _paired_needs(), _plot(), DataFrame, Path (+10 more)

### Community 19 - "prepare"
Cohesion: 0.20
Nodes (11): main(), _plot_typologies(), _pool(), DataFrame, Path, Junta as janelas: acertos somados sobre contas somadas, por tipologia,…, Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo., prepare() (+3 more)

### Community 20 - "pandas"
Cohesion: 0.16
Nodes (11): pandas, Avalia a detecção ao longo do tempo: a quadrilha é sinalizada a tempo de…, FRAUDAR: blocos densos acham as quadrilhas? E quando a rede legítima também é…, Comunidades, núcleos, subgrafos densos e egonets. Todas as funções trabalham na…, Atributos por conta usados pelos detectores de anomalia. Os atributos são…, Detecção ao longo do tempo: a conta foi sinalizada a tempo de bloquear o…, Testes de `pixfraud.communities`: comunidades, k-núcleos, subgrafo denso e…, chain() (+3 more)

### Community 21 - "save_dataset"
Cohesion: 0.15
Nodes (14): main(), _accounts_table(), _contestations(), load_dataset(), DataFrame, Path, Grava ``accounts.csv`` e ``transactions.csv`` em ``out_dir`` (criada se não…, Lê as tabelas gravadas por ``save_dataset`` (vale também para os datasets… (+6 more)

### Community 22 - "main"
Cohesion: 0.10
Nodes (26): Decisões (e por quê), Diário 2026-09-28, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações, Random Forest (como teto supervisionado), Validação cruzada estratificada (+18 more)

### Community 23 - "mapa-da-pesquisa.md"
Cohesion: 0.08
Nodes (16): Configurações, Criar um cenário, Mudar um parâmetro, Parâmetros dos experimentos, Cronograma, Ideias futuras, Mapa da pesquisa, Atas (+8 more)

### Community 24 - "plot_value_matrix"
Cohesion: 0.24
Nodes (11): main(), _plot_effects(), _plot_metric(), DataFrame, Path, Series, Matriz conjunto de atributos × cenário da média da métrica, um painel por…, Matriz atributo × cenário do delta de Cliff médio (> 0: maior nas contas… (+3 more)

### Community 25 - "build_graph"
Cohesion: 0.05
Nodes (51): Caminho temporal, Grafo direcionado ponderado, Tempo de permanência (dwell time), Anotações feitas à mão na reunião, Desde a última reunião, Discussão e decisões, Dúvidas em aberto, O que foi feito (29/09) (+43 more)

### Community 27 - "10. Modelos integrados em 29/09 (implementados, ainda sem resultados)"
Cohesion: 0.15
Nodes (16): 10. Modelos integrados em 29/09 (implementados, ainda sem resultados), ndarray, Rótulo binário dos detectores que só dão escore: a fração ``fraction`` de maior…, _top_fraction(), fraudar(), node2vec_embedding(), node2vec_isolation_forest(), DataFrame (+8 more)

### Community 28 - "experiment.py"
Cohesion: 0.16
Nodes (16): copy, dataclasses, importlib_metadata, inspect, numpy, platform, Que tipo de rede é a do Pix sintético? E o que passeios e cosseno dizem sobre…, Redes neurais para grafos: aprender a estrutura ajuda a achar fraude? Compara,… (+8 more)

### Community 30 - "test_scripts.py"
Cohesion: 0.21
Nodes (20): _check_metadata(), Testes de fumaça dos scripts de avaliação, num dataset minúsculo., O *_meta.json existe e tem o que é preciso para refazer o resultado., _run(), test_avaliar_atributos(), test_avaliar_cenarios(), test_avaliar_deteccao_online(), test_avaliar_externo() (+12 more)

### Community 31 - "visualization.py"
Cohesion: 0.13
Nodes (21): concurrent_futures, matplotlib, matplotlib_colors, matplotlib_lines, matplotlib_pyplot, scipy, Quanto cada atributo contribui, e quão longe estamos de um modelo que viu os…, Avalia os detectores em cenários de dificuldade (configs/cenarios.yaml). O… (+13 more)

### Community 32 - "test_algorithms.py"
Cohesion: 0.15
Nodes (14): math, find_pattern(), longest_chain(), Ocorrências do formato ``pattern`` dentro de ``graph`` (algoritmo VF2). Cada…, Caminho gargalo: a rota de ``source`` até ``target`` cuja menor aresta é a…, Maior cadeia (caminho mais longo) de um grafo acíclico, como uma trilha de…, widest_path(), graph_from_edges() (+6 more)

### Community 33 - "Graph"
Cohesion: 0.16
Nodes (18): _densest(), densest_subgraph(), _fraudar_weighted(), _peel(), peeling_scores(), Graph, ndarray, Subgrafo de maior densidade (peso total / nº de contas), pelo algoritmo guloso… (+10 more)

### Community 34 - "patterns.py"
Cohesion: 0.19
Nodes (19): 8. Validação externa: AMLworld, Ferramentas para criar grafos, _add(), chain(), cycle(), fan_in(), fan_out(), inject() (+11 more)

### Community 35 - "reproduzir_tudo.py"
Cohesion: 0.12
Nodes (21): csv, datetime, os, abrir(), anotar(), formatar(), graphify(), main() (+13 more)

### Community 36 - "mapa-do-relatorio.md"
Cohesion: 0.12
Nodes (8): Resumo {.unnumbered}, Introdução, Fundamentação teórica, Conclusão, Como escrever, Estrutura, Relatório final, Mapa do relatório

### Community 37 - "build_features"
Cohesion: 0.08
Nodes (27): Coeficiente de agrupamento (clustering), Grau (in_degree, out_degree), Intermediação (betweenness centrality), PageRank (ponderado pelo valor), Atributos, Como começar, Como o dinheiro se move, Dados (+19 more)

### Community 38 - "ilustrar_grafos_de_conhecimento.py"
Cohesion: 0.22
Nodes (13): collections, _cor_da_nota(), _grafo_de_notas(), _grafo_do_codigo(), _grupos_do_obsidian(), main(), _pasta(), Path (+5 more)

### Community 39 - "Resultados"
Cohesion: 0.12
Nodes (16): 10. Redes neurais para grafos (GNN), 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000, 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro, 14. Cuidados na interpretação, 15. Conclusão parcial, 16. Próximos passos, 1. Cenário base: o tabular parece bastar, 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador (+8 more)

### Community 40 - "anomaly.py"
Cohesion: 0.14
Nodes (14): scipy_stats, sklearn_cluster, sklearn_decomposition, sklearn_ensemble, sklearn_exceptions, sklearn_kernel_approximation, sklearn_linear_model, sklearn_neighbors (+6 more)

### Community 41 - "mapa-dos-testes.md"
Cohesion: 0.33
Nodes (4): Escrevendo um teste novo, O que cada arquivo testa, Testes, Mapa dos testes

### Community 42 - "test_patterns.py"
Cohesion: 0.18
Nodes (12): fraud_nodes(), mule_ring(), Graph, Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor)., Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.…, parametrize, Testes de `pixfraud.patterns`: formato dos padrões de fraude e injeção num…, test_chain_loses_fee_at_each_hop() (+4 more)

### Community 43 - "_fraud_ring"
Cohesion: 0.20
Nodes (12): _collector_payouts(), _fraud_ring(), _hops(), _later(), _launder(), _pick_person(), Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora…, Uma pessoa que ainda não é laranja: a conta cedida ou alugada para a quadrilha. (+4 more)

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

### Community 71 - "two_cliques"
Cohesion: 0.67
Nodes (3): fixture, Dois cliques de 5 contas ligados por uma única aresta a4 -> b0., two_cliques()

### Community 72 - "Mapa das leituras"
Cohesion: 0.29
Nodes (7): Aprendizado de máquina e avaliação, Como acrescentar uma leitura, Dados: Pix e datasets públicos, Detecção de anomalias em grafos, Grafos e redes, Mapa das leituras, Trabalhos relacionados: fraude com redes neurais em grafos

### Community 73 - "Resultados"
Cohesion: 0.29
Nodes (7): A comparação entre atributos tabulares e de grafo depende do gerador, Detectar a tempo de bloquear o dinheiro, Perfis de fraude, Poucos rótulos rendem muito, Resultados, Validação do dataset sintético, Validação externa

### Community 74 - "propagate_risk"
Cohesion: 0.15
Nodes (14): Propagação de risco (culpa por associação), 6. Culpa por associação: usar as contestações que já existem, _evaluate(), _evaluate_star(), main(), Todas as famílias numa semente, avaliadas nas mesmas contas (as que ninguém…, label_spreading(), propagate_risk() (+6 more)

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

### Community 83 - "_normal_transactions"
Cohesion: 0.18
Nodes (14): _amounts(), _camouflage_transactions(), _day_weights(), _merchant_popularity(), _normal_transactions(), _or(), ndarray, _random_seconds() (+6 more)

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

### Community 88 - "main"
Cohesion: 0.17
Nodes (13): _known_frauds(), _known_label(), main(), _mean_percentile(), _plot(), DataFrame, Path, Series (+5 more)

### Community 89 - "diario-de-pesquisa.md"
Cohesion: 0.24
Nodes (4): Diário de pesquisa, Notas, Para que serve, Diário de pesquisa

### Community 90 - "SimulationConfig"
Cohesion: 0.18
Nodes (10): Parâmetros da simulação (descritos em ``configs/experimento.yaml``)., SimulationConfig, data(), fixture, prepared(), fixture, parametrize, test_graph_detectors_run_on_a_generated_dataset() (+2 more)

### Community 91 - "Notas da pesquisa no Obsidian"
Cohesion: 0.20
Nodes (10): Abrir, Grafo de conhecimento do código (Graphify), Notas da pesquisa no Obsidian, Para agentes e ferramentas de IA, Plugins da comunidade (opcionais), Por que nenhuma nota se chama "README", Regras, Rotina (+2 more)

### Community 92 - "argparse"
Cohesion: 0.22
Nodes (5): argparse, pypandoc, Gera o relatório a partir dos capítulos em Markdown de relatorio/capitulos/.…, Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.…, Gera o explorador interativo da rede inteira (HTML). A página mostra todas as…

### Community 93 - "_fit_sage"
Cohesion: 0.17
Nodes (9): _DirectedSAGE(), __init__(), _fit_sage(), _GraphSAGE, ndarray, Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos…, Treina uma GraphSAGE com os rótulos de ``train`` e devolve a probabilidade de…, GraphSAGE de 2 camadas com uma convolução para cada sentido do Pix. (+1 more)

### Community 94 - "test_gnn.py"
Cohesion: 0.22
Nodes (8): fixture, Testes de `pixfraud.gnn` (precisam do torch: pip install -e ".[gnn]")., 300 contas numa rede esparsa e uma "quadrilha" de 12 contas densamente ligadas.…, ring_in_sparse_network(), test_dominant_refuses_graphs_that_would_not_fit(), test_dominant_scores_are_aligned_and_flag_the_ring(), test_sage_finds_the_rest_of_the_ring_from_a_few_known(), test_sage_learns_the_ring_from_structure_alone()

### Community 95 - "oddball_scores"
Cohesion: 0.20
Nodes (11): Egonet e OddBall, community_summary(), egonet_features(), oddball_scores(), DataFrame, Medidas da egonet (a conta, seus vizinhos e as arestas entre eles). *…, Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010). Em redes reais, as…, Tamanho, arestas internas e externas de cada comunidade (e nº de fraudes, se… (+3 more)

### Community 96 - "test_experiment.py"
Cohesion: 0.15
Nodes (17): Repete o experimento com várias sementes. Cada semente gera um dataset…, Cópia da seção ``modelos`` com ``seed`` em todo detector que aceita semente.…, _run_one_seed(), run_seeds(), seeded_models(), _planted(), parametrize, Testes de `pixfraud.experiment`: várias sementes e leitura dos cenários. (+9 more)

### Community 97 - "Diário 2026-09-26"
Cohesion: 0.33
Nodes (6): Decisões (e por quê), Diário 2026-09-26, Dúvidas e bloqueios, O que fiz, Próximo passo, Resultados e observações

### Community 98 - "Diário 2026-09-29"
Cohesion: 0.25
Nodes (8): Decisões (e por quê), Diário 2026-09-29, Dúvidas e bloqueios, Integração do branch `local-2026-09-24`, O que fiz, Próximo passo, Quantas sementes usar (conversa de 29/09), Resultados e observações

### Community 99 - "community_layout"
Cohesion: 0.29
Nodes (8): community_layout(), _free_spot(), _place_center(), Graph, ndarray, Primeiro ponto da espiral de girassol em que um disco de ``radius`` não encosta…, Posições que deixam as comunidades visíveis. Cada comunidade recebe um disco de…, Põe cada grupo ligado de ``sub`` (uma quadrilha, em geral) num círculo em volta…

### Community 100 - "Estudos: teoria dos grafos aplicada a fraudes no Pix"
Cohesion: 0.50
Nodes (4): Como usar, Dados de exemplo, Estudos: teoria dos grafos aplicada a fraudes no Pix, Roteiro

### Community 103 - "algorithms.py"
Cohesion: 0.18
Nodes (12): heapq, itertools, networkx_algorithms, cosine_similarity(), money_backbone(), Algoritmos clássicos de teoria dos grafos aplicados às transações. | Função |…, Cosseno do ângulo entre os vetores ``a`` e ``b``. $$\\cos\\theta = \\frac{a…, Ângulo entre ``a`` e ``b``: $\\theta = \\arccos(\\cos\\theta)$, em graus (ou… (+4 more)

### Community 104 - "_look_alike_transactions"
Cohesion: 0.29
Nodes (7): _after_activity(), _look_alike_transactions(), Instante em que ``delay`` segundos de atividade terão passado a partir de…, Pix legítimos que se parecem com partes de uma quadrilha ("negativos…, Dias do período (a partir de 0) em que cai o ``salary_business_day``-ésimo dia…, _salary_days(), test_activity_clock()

### Community 105 - "Próximos passos"
Cohesion: 0.33
Nodes (6): Dados, Para a próxima reunião, Pesquisa, Pesquisa (reunião de 24/09), Próximos passos, Repositório

### Community 106 - "Diário 2026-09-22"
Cohesion: 0.40
Nodes (5): Decisões (e por quê), Diário 2026-09-22, Dúvidas e bloqueios, Próximo passo, Resultados e observações

### Community 107 - "Reproduzir os resultados"
Cohesion: 0.67
Nodes (3): Mapa, Reproduzir os resultados, Scripts

## Knowledge Gaps
- **333 isolated node(s):** `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix`, `Como se orientar`, `Ao editar notas` (+328 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 749 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Módulos` connect `Módulos` to `gnn.py`, `similar_accounts`, `detect_communities`, `graph_from_csv`, `main`, `test_anomaly.py`, `compare_runs`, `generate_dataset`, `draw_graph`, `load_experiment_config`, `explorer_payload`, `main`, `prepare`, `main`, `plot_value_matrix`, `build_graph`, `10. Modelos integrados em 29/09 (implementados, ainda sem resultados)`, `test_algorithms.py`, `patterns.py`, `build_features`, `test_bcb.py`, `propagate_risk`, `SimulationConfig`, `oddball_scores`, `test_experiment.py`, `algorithms.py`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Why does ``pixfraud`: o código da pesquisa` connect `Módulos` to `guia-do-explorador.md`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `generate_dataset()` connect `generate_dataset` to `test_experiment.py`, `Módulos`, `main`, `_look_alike_transactions`, `propagate_risk`, `_fraud_ring`, `load`, `load_experiment_config`, `main`, `_normal_transactions`, `save_dataset`, `main`, `main`, `build_graph`, `SimulationConfig`, `experiment.py`, `test_scripts.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 54 inferred relationships involving `Módulos` (e.g. with `cosine_similarity()` and `find_pattern()`) actually correct?**
  _`Módulos` has 54 INFERRED edges - model-reasoned connections that need verification._
- **What connects `pixfraud`, `Autoria`, `Regra principal: LGPD no contexto do Pix` to the rest of the system?**
  _333 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `gnn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13666666666666666 - nodes in this community are weakly interconnected._
- **Should `graph_from_csv` be split into smaller, more focused modules?**
  _Cohesion score 0.05697278911564626 - nodes in this community are weakly interconnected._