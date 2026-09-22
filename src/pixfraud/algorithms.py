"""Algoritmos clássicos de teoria dos grafos aplicados às transações.

| Função | Algoritmo | Pergunta que responde |
|---|---|---|
| ``money_backbone`` | ramificação máxima (Edmonds) | qual a principal origem do dinheiro de cada conta? |
| ``widest_path`` | caminho gargalo (Dijkstra modificado) | qual o maior valor que passa por uma única rota? |
| ``laundering_depth``, ``longest_chain`` | condensação + maior caminho em DAG | por quantas camadas o dinheiro passa? |
| ``find_pattern`` | monomorfismo de subgrafos (VF2) | onde este formato aparece na rede? |
| ``hubs_authorities`` | HITS | quem distribui e quem concentra? |
| ``similar_accounts`` | Jaccard / SimRank | que contas se parecem com esta? |
| ``bipartite_projection`` | projeção de grafo bipartido | que vítimas pagaram as mesmas laranjas? |
"""

from __future__ import annotations

import heapq
import itertools
from collections.abc import Iterable

import networkx as nx
import pandas as pd
from networkx.algorithms import isomorphism


def money_backbone(graph: nx.DiGraph, weight: str = "amount") -> nx.DiGraph:
    """Espinha dorsal do dinheiro: a ramificação de peso máximo (algoritmo de Edmonds).

    Uma *ramificação* é uma floresta de arborescências: cada conta fica com no
    máximo uma aresta de entrada, sem ciclos. A de peso máximo guarda, para
    cada conta, a origem que mais contribuiu para o seu dinheiro (exceto
    quando isso formaria um ciclo). O resultado é uma "árvore genealógica" do
    dinheiro, bem mais fácil de desenhar que a rede inteira.
    """
    backbone = nx.maximum_branching(graph, attr=weight, preserve_attrs=True)
    backbone.add_nodes_from(graph.nodes(data=True))
    return backbone


def widest_path(graph: nx.DiGraph, source, target, weight: str = "amount") -> tuple[list, float]:
    """Caminho gargalo: a rota de ``source`` até ``target`` cuja menor aresta é a maior possível.

    É o Dijkstra com duas trocas: em vez de somar, toma o mínimo ao longo do
    caminho, e em vez de minimizar, maximiza. O valor devolvido é o maior
    montante que poderia ter seguido *uma única rota*. Devolve ``([], 0.0)``
    se não houver caminho.
    """
    if source == target:
        return [source], float("inf")
    width = {source: float("inf")}
    parent = {}
    done = set()
    counter = itertools.count()
    heap = [(-float("inf"), next(counter), source)]
    while heap:
        negative, _, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        if u == target:
            break
        for v, data in graph[u].items():
            candidate = min(-negative, data.get(weight, 1.0))
            if v not in done and candidate > width.get(v, 0.0):
                width[v] = candidate
                parent[v] = u
                heapq.heappush(heap, (-candidate, next(counter), v))
    if target not in done:
        return [], 0.0
    path = [target]
    while path[-1] != source:
        path.append(parent[path[-1]])
    return path[::-1], float(width[target])


def laundering_depth(graph: nx.DiGraph) -> pd.Series:
    """Por quantas camadas o dinheiro ainda pode passar depois de sair de cada conta.

    As componentes fortemente conexas viram vértices (condensação, sempre um
    DAG). A profundidade de uma componente é o comprimento do maior caminho
    que sai dela, calculado de trás para a frente na ordem topológica
    (programação dinâmica). Contas da mesma componente têm a mesma profundidade.
    """
    condensed = nx.condensation(graph)
    depth = {}
    for c in reversed(list(nx.topological_sort(condensed))):
        depth[c] = 1 + max((depth[s] for s in condensed.successors(c)), default=-1)
    mapping = condensed.graph["mapping"]
    return pd.Series({v: depth[mapping[v]] for v in graph}, name="laundering_depth")


def longest_chain(graph: nx.DiGraph) -> list:
    """Maior cadeia (caminho mais longo) de um grafo acíclico, como uma trilha de lavagem."""
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("maior caminho só é eficiente em grafos acíclicos; use a condensação ou uma trilha temporal")
    return nx.dag_longest_path(graph)


def find_pattern(
    graph: nx.DiGraph,
    pattern: nx.DiGraph,
    induced: bool = False,
    max_results: int = 100,
    candidates: Iterable | None = None,
) -> list[dict]:
    """Ocorrências do formato ``pattern`` dentro de ``graph`` (algoritmo VF2).

    Cada ocorrência é um dicionário ``{vértice do padrão: conta}``. Com
    ``induced=False`` (monomorfismo), a rede pode ter arestas a mais entre as
    contas encontradas; com ``induced=True`` (isomorfismo de subgrafo
    induzido), não pode. A busca é exponencial no pior caso, então limite o
    número de resultados (``max_results``) ou restrinja a busca a um conjunto
    de contas suspeitas (``candidates``).
    """
    host = graph.subgraph(candidates) if candidates is not None else graph
    matcher = isomorphism.DiGraphMatcher(host, pattern)
    found = matcher.subgraph_isomorphisms_iter() if induced else matcher.subgraph_monomorphisms_iter()
    return [{p: g for g, p in match.items()} for match in itertools.islice(found, max_results)]


def hubs_authorities(graph: nx.DiGraph, max_iter: int = 1000) -> pd.DataFrame:
    """HITS (Kleinberg): *hubs* apontam para boas autoridades; *autoridades* recebem de bons hubs.

    Numa rede de Pix, autoridades concentram dinheiro vindo de contas que
    pagam muita gente (coletores, comércios), e hubs distribuem.
    """
    hubs, authorities = nx.hits(graph, max_iter=max_iter)
    return pd.DataFrame({"hub": pd.Series(hubs), "authority": pd.Series(authorities)})


def similar_accounts(graph: nx.DiGraph, account, method: str = "jaccard_out", top: int = 10) -> pd.Series:
    """Contas mais parecidas com ``account`` pela vizinhança.

    * ``"jaccard_out"``: quem paga as mesmas contas (laranjas de uma quadrilha
      repassam para o mesmo intermediário);
    * ``"jaccard_in"``: quem recebe das mesmas contas;
    * ``"jaccard"``: vizinhos em qualquer sentido;
    * ``"simrank"``: "são parecidas as contas pagas por contas parecidas"
      (recursivo, bem mais lento).

    Jaccard: $|N(a) \\cap N(b)| / |N(a) \\cup N(b)|$.
    """
    if method == "simrank":
        scores = pd.Series(nx.simrank_similarity(graph, source=account))
        return scores.drop(account, errors="ignore").sort_values(ascending=False).head(top)
    neighbors = {
        "jaccard_out": graph.successors,
        "jaccard_in": graph.predecessors,
        "jaccard": lambda v: itertools.chain(graph.successors(v), graph.predecessors(v)),
    }
    if method not in neighbors:
        raise ValueError("method deve ser 'jaccard_out', 'jaccard_in', 'jaccard' ou 'simrank'")
    reverse = {
        "jaccard_out": graph.predecessors,
        "jaccard_in": graph.successors,
        "jaccard": lambda v: itertools.chain(graph.successors(v), graph.predecessors(v)),
    }[method]
    mine = set(neighbors[method](account))
    candidates = {c for n in mine for c in reverse(n)} - {account}
    scores = {}
    for c in candidates:
        theirs = set(neighbors[method](c))
        scores[c] = len(mine & theirs) / len(mine | theirs)
    return pd.Series(scores, name=method, dtype=float).sort_values(ascending=False).head(top)


def bipartite_projection(graph: nx.DiGraph, left: Iterable, right: Iterable) -> nx.Graph:
    """Projeção do grafo bipartido ``left`` × ``right`` sobre ``left``.

    Duas contas de ``left`` ficam ligadas se se relacionam (em qualquer
    sentido) com alguma conta em comum de ``right``; o peso da aresta é o
    número de contas em comum. Ex.: com vítimas × laranjas, as componentes
    da projeção revelam as quadrilhas.
    """
    left, right = set(left), set(right)
    bipartite = nx.Graph()
    bipartite.add_nodes_from(left)
    for u, v in graph.edges():
        if (u in left and v in right) or (u in right and v in left):
            bipartite.add_edge(u, v)
    return nx.bipartite.weighted_projected_graph(bipartite, left)
