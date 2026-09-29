---
tags: [mapa]
---

# Estudos: teoria dos grafos aplicada a fraudes no Pix

Material de estudo para a fundamentação teórica da pesquisa. Cada notebook traz teoria
curta, código comentado com exemplos do próprio projeto e exercícios. As respostas estão em
[gabarito.ipynb](gabarito.ipynb): tente antes de olhar!

## Como usar

Na raiz do repositório (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
pip install -e ".[dev,notebooks]"
jupyter lab
```

Abra a pasta `estudos/`. Os notebooks já vêm executados, então dá para lê-los direto no
GitHub. Mesmo assim, o melhor é rodar célula por célula e mexer nos exemplos.

## Roteiro

| #  | Notebook | Conceitos | Leitura de apoio | Objetivos da proposta |
|----|----------|-----------|------------------|-----------------------|
| 01 | [Fundamentos](01_fundamentos.ipynb) | grafo direcionado e ponderado, multigrafo, lista e matriz de adjacência, grau, lema do aperto de mãos, caminhos, conectividade forte e fraca, condensação, ciclos, caminhos temporais | Diestel, cap. 1; Easley & Kleinberg, cap. 2 | 1, 3, 4 |
| 02 | [Construindo grafos](02_construindo_grafos.ipynb) | decisões de modelagem, janelas de tempo, geradores de grafos, layouts, recortes (ego graph, trilha do dinheiro), exportação | — | 3, 4, 9 |
| 03 | [Métricas de centralidade](03_metricas_de_centralidade.ipynb) | grau, proximidade, intermediação (à mão e aproximada), PageRank (método da potência), agrupamento, reciprocidade | Easley & Kleinberg, cap. 3 e 14; Brandes (2001) | 5 |
| 04 | [Padrões de fraude](04_padroes_de_fraude.ipynb) | fan-in, fan-out, cadeia, ciclo, scatter-gather; injeção de padrões; por que "anomalia tem dois lados" | Altman et al. (2023); Akoglu et al. (2015) | 6, 7, 9 |
| 05 | [Modelos de redes](05_modelos_de_redes.ipynb) | Erdős–Rényi, Barabási–Albert, Watts–Strogatz, lei de potência, mundo pequeno, modelo nulo | Easley & Kleinberg, cap. 18 e 20 | 11 |
| 06 | [Tipo de rede](06_tipo_de_rede.ipynb) | arestas direcionadas (grau de entrada × saída), lei de potência e estimador de máxima verossimilhança, Barabási–Albert (ligação preferencial), componente gigante fraca e forte e transição de fase, passeio aleatório e matriz de transição, similaridade de cosseno = ângulo entre vetores | Barabási, *Network Science*, cap. 3 a 5; Clauset et al. (2009); Easley & Kleinberg, cap. 14 | 5, 11 |

As referências estão em [docs/referencias.bib](../docs/referencias.bib). Anote as leituras
em [docs/revisao-bibliografica.md](../docs/revisao-bibliografica.md).

Consulta rápida de conceitos e comandos: [cola-networkx.md](cola-networkx.md).

## Ferramentas para criar grafos

Todas estão no pacote `pixfraud` e são usadas nos notebooks.

**Criar e recortar** (`pixfraud.graph`)

| Função | Para quê |
|--------|----------|
| `graph_from_edges([("ana", "bia", 50), ...])` | grafo a partir de uma lista de arestas (exemplos, exercícios) |
| `graph_from_csv(arquivo, source=..., target=..., amount=...)` | grafo a partir de qualquer CSV de transações; `aggregate=False` devolve o multigrafo |
| `build_graph(transacoes, contas)` | o grafo do projeto, a partir das tabelas do dataset |
| `money_trail(G, conta, max_hops, direction)` | trilha do dinheiro: para frente (`"forward"`), para trás (`"backward"`) ou os dois (`"both"`) |
| `adjacency_matrix(G, weight=None)` | matriz de adjacência rotulada (`DataFrame`) |
| `describe(G)` | resumo: vértices, arestas, densidade, componentes, reciprocidade… |

**Tipo de rede** (`pixfraud.network` e `pixfraud.algorithms`)

| Função | Para quê |
|--------|----------|
| `degree_sequence(G, "in")`, `fit_power_law(graus)` | graus de entrada/saída/total e expoente da lei de potência (com `k_min` e distância KS) |
| `component_summary(G)`, `giant_component(G, strong=True)` | componentes fracas e fortes e a componente gigante |
| `compare_network_models(G)` | a rede ao lado de um Erdős–Rényi e de um Barabási–Albert do mesmo tamanho |
| `random_walk(G, conta)`, `random_walk_visits(G, vitimas)` | passeios aleatórios que seguem o dinheiro |
| `cosine_similarity(a, b)`, `vector_angle(a, b)`, `similar_accounts(G, conta, "cosine_out")` | similaridade de cosseno, ângulo entre vetores e contas parecidas pelos valores |

**Padrões de fraude** (`pixfraud.patterns`)

| Função | Para quê |
|--------|----------|
| `fan_in`, `fan_out`, `chain`, `cycle`, `scatter_gather`, `mule_ring` | geram o padrão como um pequeno `DiGraph`, com papéis e valores |
| `inject(G, padrao, prefix=..., seed=...)` | insere o padrão numa rede maior (vítimas viram contas existentes) |
| `fraud_nodes(G)` | lista as contas com papel de fraude |

**Desenhar e exportar** (`pixfraud.visualization`)

| Função | Para quê |
|--------|----------|
| `draw_graph(G, color_by="role", layout="auto")` | desenho estático; cores por papel ou por um escore |
| `save_graph(G, "arquivo.ext")` | `.png`/`.svg`/`.pdf`, `.html` (interativo) ou `.gexf`/`.graphml` (Gephi) |
| `plot_heat_graph`, `plot_risk_heatmap` | grafo de calor e heatmap de risco dos detectores |

**Pela linha de comando** (na raiz do repositório):

```powershell
python scripts/criar_grafo.py padrao mule_ring --saida reports/estudos/anel.png
python scripts/criar_grafo.py padrao chain --tamanho 6 --saida reports/estudos/cadeia.html
python scripts/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --contas estudos/dados/exemplo_contas.csv --saida reports/estudos/exemplo.png
python scripts/criar_grafo.py csv data/synthetic/transactions.csv --conta C000333 --saltos 5 --direcao tras --saida reports/estudos/trilha.html
```

## Dados de exemplo

`dados/exemplo_transacoes.csv` tem 20 Pix entre 11 contas, pequeno o bastante para conferir
tudo à mão:

- um grupo de amigos (ana, bruno, carla, davi, elisa) que trocam Pix entre si;
- dois comércios (padaria, mercado);
- um golpe: carla (de madrugada) e fabio pagam `conta_x`, que repassa quase tudo para
  `conta_y`, que repassa para `conta_z`.

Os papéis estão em `dados/exemplo_contas.csv`.
