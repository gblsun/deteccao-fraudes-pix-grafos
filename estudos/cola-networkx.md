# Cola: teoria dos grafos × NetworkX

## Glossário

| Português | Inglês | NetworkX | No Pix |
|-----------|--------|----------|--------|
| vértice | vertex / node | `G.nodes` | conta |
| aresta | edge | `G.edges` | Pix (ou todos os Pix de um par) |
| grafo direcionado (dígrafo) | directed graph | `nx.DiGraph` | pagador → recebedor |
| multigrafo | multigraph | `nx.MultiDiGraph` | um Pix por aresta |
| grafo ponderado | weighted graph | atributo `amount` | valor transferido |
| grau de entrada / saída | in-degree / out-degree | `G.in_degree(v)`, `G.out_degree(v)` | de quantas contas recebe / para quantas envia |
| força | strength | `G.in_degree(v, weight="amount")` | quanto recebeu |
| densidade | density | `nx.density(G)` | fração das relações possíveis que existem |
| caminho | path | `nx.shortest_path(G, u, v)` | rota do dinheiro |
| alcançável | reachable | `nx.has_path`, `nx.descendants`, `nx.ancestors` | o dinheiro pode ter chegado |
| fracamente / fortemente conexo | weakly / strongly connected | `nx.is_weakly_connected`, `nx.strongly_connected_components` | dinheiro circula (CFC) |
| condensação | condensation | `nx.condensation(G)` | fluxo entre grupos |
| ciclo | cycle | `nx.simple_cycles(G)` | round-tripping |
| grafo acíclico (DAG) | directed acyclic graph | `nx.is_directed_acyclic_graph` | cadeia de lavagem |
| subgrafo induzido | induced subgraph | `G.subgraph(nos)` | recorte |
| vizinhança (ego) | ego graph | `nx.ego_graph(G, v, radius)` | contas próximas |
| intermediação | betweenness centrality | `nx.betweenness_centrality` | conta "no meio do caminho" |
| proximidade | closeness centrality | `nx.closeness_centrality` | conta perto de todas |
| PageRank | PageRank | `nx.pagerank(G, weight=...)` | para onde o dinheiro escoa |
| coeficiente de agrupamento | clustering coefficient | `nx.clustering(G.to_undirected())` | contatos que se conhecem |
| reciprocidade | reciprocity | `nx.reciprocity(G, nos)` | Pix de ida e volta |

## Comandos

```python
import networkx as nx

# criar
G = nx.DiGraph()
G.add_edge("ana", "bia", amount=50.0)           # cria os vértices se não existirem
G.add_edges_from([("bia", "caio"), ("caio", "ana")], amount=10.0)
G.add_node("loja", role="comercio")
G = nx.from_pandas_edgelist(df, "sender", "receiver", edge_attr=["amount"], create_using=nx.DiGraph)

# inspecionar
G.number_of_nodes(), G.number_of_edges()
list(G.successors("ana")), list(G.predecessors("ana"))
G["ana"]["bia"]                                  # atributos da aresta
G.nodes["loja"]                                  # atributos do vértice
nx.get_node_attributes(G, "role")
nx.set_node_attributes(G, {"ana": "normal"}, "role")

# converter
U = G.to_undirected()
R = G.reverse()                                  # inverte o sentido de todas as arestas
H = G.subgraph(["ana", "bia"]).copy()
df = nx.to_pandas_edgelist(G)
M = nx.to_pandas_adjacency(G, weight="amount")

# geradores
nx.path_graph(5, create_using=nx.DiGraph)
nx.cycle_graph(5, create_using=nx.DiGraph)
nx.star_graph(5), nx.complete_graph(5)
nx.gnm_random_graph(n, m), nx.barabasi_albert_graph(n, m), nx.watts_strogatz_graph(n, k, p)

# salvar e ler
nx.write_gexf(G, "rede.gexf")                    # Gephi
nx.write_graphml(G, "rede.graphml")
```

## Armadilhas comuns

- **Peso não é distância.** Em `nx.shortest_path(G, weight="amount")` e na intermediação
  com `weight=`, o peso é tratado como *comprimento*: valores altos viram caminhos
  "longos". Para valores financeiros, calcule caminhos sem peso ou use `1 / valor`.
- **Proximidade em dígrafos usa distâncias de chegada.** Para usar as de saída, calcule em
  `G.reverse()`.
- **`to_undirected()` junta ida e volta.** Pares com Pix nos dois sentidos viram uma aresta
  só, e os atributos de uma das direções se perdem.
- **Intermediação exata é cara**, $O(nm)$. Use `k=` (amostragem) em grafos grandes e fixe
  `seed=` para ter resultados reprodutíveis.
- **O grafo agregado esquece o tempo.** Alcançabilidade no grafo não garante que o dinheiro
  de fato passou por ali (notebook 01, caminhos temporais).
- **Iterar e modificar ao mesmo tempo** (`for v in G: G.remove_node(v)`) dá erro. Itere sobre
  `list(G)`.
