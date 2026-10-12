# `pixfraud`: o código da pesquisa

Pacote Python com tudo o que é reaproveitado pelos scripts, notebooks e pelo app. Cada
módulo começa com uma docstring que explica o que ele faz; aqui fica o mapa.

## Como as peças se encaixam

```mermaid
flowchart LR
    subgraph dados [Dados]
        simulation["simulation.py<br/>gerador sintético"]
        external["external.py<br/>AMLworld e PaySim"]
        bcb["bcb.py<br/>estatísticas do BCB"]
    end
    graph["graph.py<br/>grafo de transações"]
    temporal["temporal.py<br/>tempo de permanência"]
    communities["communities.py<br/>k-núcleo, OddBall"]
    features["features.py<br/>atributos por conta"]
    anomaly["models/<br/>um arquivo por modelo"]
    tuning["tuning/<br/>hiperparâmetros"]
    evaluation["evaluation.py<br/>métricas"]
    experiment["experiment.py<br/>uma ou várias sementes"]
    stats["stats.py<br/>testes estatísticos"]
    online["online.py<br/>detectou a tempo?"]
    visualization["visualization.py<br/>figuras"]

    simulation --> graph
    external --> graph
    graph --> features
    temporal --> features
    communities --> features
    features --> anomaly --> evaluation
    experiment --> features
    experiment --> anomaly
    tuning --> anomaly
    experiment --> evaluation
    evaluation --> stats
    online --> experiment
    evaluation --> visualization
```

Os scripts de `scripts/` chamam `experiment.py` (uma rodada) e `stats.py` (várias
rodadas); `bcb.py` serve para calibrar e validar o gerador.

## Módulos

| Módulo | Para que serve | Funções principais |
|--------|----------------|--------------------|
| [`simulation.py`](simulation.py) | gera contas e Pix sintéticos com quadrilhas; parâmetros que desligam os atalhos do gerador | `generate_dataset`, `SimulationConfig`, `with_overrides` |
| [`external.py`](external.py) | converte AMLworld e PaySim para o formato do projeto; tipologias e janelas de tempo | `load_amlworld`, `load_amlworld_patterns`, `time_windows` |
| [`bcb.py`](bcb.py) | baixa estatísticas agregadas do Pix (dados abertos do Banco Central) | `fetch` |
| [`graph.py`](graph.py) | monta o grafo direcionado e ponderado; trilha do dinheiro; resumo | `build_graph`, `money_trail`, `describe` |
| [`temporal.py`](temporal.py) | caminhos que respeitam a ordem dos Pix; tempo de permanência | `temporal_trail`, `dwell_time`, `temporal_features` |
| [`communities.py`](communities.py) | comunidades (Louvain), k-núcleos, subgrafo mais denso, OddBall | `detect_communities`, `oddball_scores`, `structural_features` |
| [`features.py`](features.py) | atributos por conta, agrupados em conjuntos (tabular, grafo...) | `build_features`, `FEATURE_SETS` |
| [`models/`](models/mapa-dos-modelos.md) | **todos os modelos, um arquivo por modelo**, em `unsupervised/` (por família: `proximity/`, `statistical/`, `isolation/`, `boundary/`, `neural/`, `graph/`), `semi_supervised/` (PageRank personalizado, label spreading) e `supervised/` (`trees/`, `neural/`); o que cada um faz e como se saiu está no [mapa dos modelos](models/mapa-dos-modelos.md) | `DETECTORS`, `GRAPH_DETECTORS`, `SUPERVISED`, `Detection` |
| [`tuning/`](tuning/__init__.py) | otimização de hiperparâmetros: grades de [`configs/busca_hiperparametros.yaml`](../../configs/busca_hiperparametros.yaml) que se ampliam sozinhas quando o vencedor cai na ponta, escolhidas em redes de validação (sementes separadas das de avaliação) | `load_search_spaces`, `expand`, `score_candidates`, `choose` |
| [`anomaly.py`](anomaly.py), [`graph_models.py`](graph_models.py), [`gnn.py`](gnn.py) | nomes antigos, mantidos para scripts, notebooks e notas que já os usam: só reexportam de `models/` (as funções de propagação também continuam em `flow.py`) | os mesmos de antes |
| [`evaluation.py`](evaluation.py) | precision, recall, AP, precision@k; recall por grupo | `evaluate`, `recall_by_group` |
| [`experiment.py`](experiment.py) | o pipeline inteiro, uma semente ou várias; cenários | `prepare`, `run_detectors`, `run_seeds`, `load_scenarios` |
| [`stats.py`](stats.py) | Mann-Whitney com delta de Cliff, Kruskal-Wallis + Dunn, Friedman + Nemenyi, bootstrap, testes pareados, permutação e hipergeométrico contra o acaso, qui-quadrado/Fisher, modelo nulo | `compare_groups`, `kruskal_groups`, `friedman_models`, `compare_runs`, `permutation_test_metric` |
| [`online.py`](online.py) | detecção ao longo do tempo e dinheiro recuperável (MED) | `checkpoint_flags`, `recovered_amount` |
| [`flow.py`](flow.py) | fluxo máximo, corte mínimo ("onde bloquear"), propagação de risco | `max_money_flow`, `blocking_accounts`, `propagate_risk` |
| [`algorithms.py`](algorithms.py) | algoritmos clássicos aplicados ao dinheiro (Edmonds, gargalo, VF2, HITS, Jaccard e cosseno...) | `widest_path`, `find_pattern`, `hubs_authorities`, `similar_accounts`, `cosine_similarity` |
| [`network.py`](network.py) | que tipo de rede é: lei de potência, componente gigante, comparação com Erdős–Rényi e Barabási–Albert, passeios aleatórios | `fit_power_law`, `component_summary`, `compare_network_models`, `random_walk_visits` |
| [`patterns.py`](patterns.py) | padrões de fraude pequenos (fan-in, cadeia, ciclo...) e injeção num grafo | `PATTERNS`, `inject` |
| [`visualization.py`](visualization.py) | desenho, HTML interativo, grafo de calor, heatmap de risco, matrizes de resultados | `draw_graph`, `plot_heat_graph`, `explain_account`, `plot_value_matrix` |
| [`explorer.py`](explorer.py) | página HTML da rede inteira (sigma.js), com filtros, linha do tempo, seletor de modelo e o modo "Acertos" (com o gabarito) | `save_network_explorer` |
| [`exploration.py`](exploration.py) | o que o explorador Streamlit calcula: gerar a rede de uma semente e cenário, pontuar todos os modelos, resumo da rede e top-k | `generate_network`, `all_model_scores`, `rank_models`, `network_summary` |

## Onde mexer para...

| Quero... | Onde | E o teste em |
|----------|------|--------------|
| criar um atributo | função em `features.py` (ou `temporal.py`/`communities.py`) e o nome em `FEATURE_SETS` | `tests/test_features.py` |
| testar outro detector | arquivo novo na família certa de `models/unsupervised/` com uma função que devolve `Detection`, exportada no `__init__.py` da família, entrada em `DETECTORS` e `FAMILIES` (em `models/unsupervised/__init__.py`), parâmetros em `configs/experimento.yaml` e, se tiver hiperparâmetros, a grade em `configs/busca_hiperparametros.yaml` | `tests/test_anomaly.py`, `tests/test_tuning.py` |
| outro modelo supervisionado | arquivo novo em `models/supervised/trees/` (use `cross_validation.out_of_fold_scores`), entradas em `SUPERVISED` e `FACTORIES` | `tests/test_experiment.py` |
| simular outro comportamento | parâmetro novo em `SimulationConfig` (com padrão que não muda o dataset atual) e um cenário em `configs/cenarios.yaml` | `tests/test_simulation.py` |
| outra métrica | `evaluation.evaluate` | `tests/test_anomaly.py` |
| outro dataset público | carregador em `external.py` que devolve `accounts` e `transactions` | `tests/test_external.py` |

Os nomes das colunas (`account_id`, `sender`, `receiver`, `amount`, `timestamp`,
`is_fraud`...) estão descritos em [`data/README.md`](../../data/README.md).

## Referência completa da API

Todas as funções, com parâmetros e docstrings, numa página navegável (com busca e links
entre as funções), gerada a partir do código:

```powershell
pip install -e ".[docs]"
python -m pdoc pixfraud -d restructuredtext --math -o site/api
start site/api/index.html
```

A pasta `site/` não é versionada: gere de novo sempre que quiser a versão atual.
