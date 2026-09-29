"""Fluxo de dinheiro, cortes mínimos ("onde bloquear") e propagação de risco.

* ``max_money_flow``: quanto dinheiro, no máximo, pode ter ido das contas de
  origem até a conta de destino, se cada aresta só comporta o valor que de fato
  passou por ela (capacidade = ``amount``).
* ``blocking_cut`` e ``blocking_accounts``: pelo teorema do fluxo máximo e
  corte mínimo (Ford e Fulkerson), o menor conjunto de Pix (ou de contas) cujo
  bloqueio interrompe todo o fluxo vale exatamente o fluxo máximo.
* ``propagate_risk``: "culpa por associação", um PageRank personalizado que
  parte de contas já sabidamente fraudulentas.
* ``label_spreading``: a mesma ideia, mas com exemplos positivos e negativos
  (contas sabidamente legítimas puxam as vizinhas para baixo).

Atenção: no grafo agregado o tempo é ignorado. Para respeitar a ordem dos Pix,
aplique estas funções sobre ``pixfraud.temporal.temporal_trail``.
"""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import numpy as np
import pandas as pd
import scipy.sparse as sp

SUPER_SOURCE = "__origem__"


def max_money_flow(graph: nx.DiGraph, sources, sink, capacity: str = "amount") -> tuple[float, dict]:
    """Fluxo máximo de ``sources`` (uma conta ou várias) até ``sink``.

    Devolve ``(valor, fluxo)``, em que ``fluxo[u][v]`` é quanto passa pela
    aresta ``u -> v`` numa solução ótima (só arestas com fluxo positivo).
    Várias origens são tratadas com uma "superorigem" ligada a todas elas.
    """
    network = _flow_network(graph, _as_list(sources), sink, capacity)
    if network is None:
        return 0.0, {}
    value, flow = nx.maximum_flow(network, SUPER_SOURCE, sink, capacity=capacity)
    used = {
        u: {v: f for v, f in targets.items() if f > 1e-9}
        for u, targets in flow.items()
        if u != SUPER_SOURCE
    }
    return float(value), {u: t for u, t in used.items() if t}


def blocking_cut(graph: nx.DiGraph, sources, sink, capacity: str = "amount") -> tuple[float, list]:
    """Corte mínimo: os Pix de menor valor total que separam ``sources`` de ``sink``.

    Devolve ``(valor do corte, [(u, v, valor), ...])``. Pelo teorema do fluxo
    máximo e corte mínimo, o valor do corte é igual ao fluxo máximo.
    """
    network = _flow_network(graph, _as_list(sources), sink, capacity)
    if network is None:
        return 0.0, []
    value, (reachable, _) = nx.minimum_cut(network, SUPER_SOURCE, sink, capacity=capacity)
    edges = [
        (u, v, network[u][v][capacity])
        for u in reachable
        if u != SUPER_SOURCE
        for v in network.successors(u)
        if v not in reachable
    ]
    return float(value), sorted(edges, key=lambda e: -e[2])


def blocking_accounts(graph: nx.DiGraph, sources, sink) -> list | None:
    """Menor conjunto de contas cujo bloqueio separa ``sources`` de ``sink``.

    Usa a técnica de *dividir vértices*: cada conta vira um par
    ``entrada -> saída`` com capacidade 1, e as arestas originais têm
    capacidade infinita. O corte mínimo nesse grafo auxiliar só pode cortar
    pares, ou seja, contas (teorema de Menger). As origens e o destino nunca
    são escolhidos. Devolve ``None`` se alguma origem pagar o destino
    diretamente, pois aí nenhum bloqueio de conta intermediária resolve.
    """
    sources = _as_list(sources)
    relevant = relevant_accounts(graph, sources, sink)
    if relevant is None:
        return []
    fixed = set(sources) | {sink}
    if any(graph.has_edge(s, sink) for s in sources):
        return None

    def tail(v):
        return v if v in fixed else (v, "saida")

    def head(v):
        return v if v in fixed else (v, "entrada")

    aux = nx.DiGraph()
    for v in relevant - fixed:
        aux.add_edge((v, "entrada"), (v, "saida"), capacity=1)
    for u, v in graph.subgraph(relevant).edges():
        aux.add_edge(tail(u), head(v))  # sem capacidade = infinita
    for s in sources:
        aux.add_edge(SUPER_SOURCE, s)
    _, (reachable, _) = nx.minimum_cut(aux, SUPER_SOURCE, sink)
    return sorted(v for v in relevant - fixed if (v, "entrada") in reachable and (v, "saida") not in reachable)


def propagate_risk(
    graph: nx.DiGraph,
    seeds: Iterable,
    alpha: float = 0.85,
    direction: str = "both",
    weight: str | None = "amount",
    relative: bool = False,
) -> pd.Series:
    """Culpa por associação: PageRank personalizado a partir das contas ``seeds``.

    A "moeda" do PageRank sempre salta de volta para uma das contas-semente,
    então o escore mede o quão perto (e por quantos caminhos) cada conta está
    delas. ``direction``: ``"forward"`` segue o dinheiro (para onde as sementes
    pagaram), ``"backward"`` volta à origem (quem pagou as sementes) e
    ``"both"`` ignora o sentido, o que alcança as laranjas "irmãs" que repassam
    para o mesmo intermediário. Com ``relative=True`` o escore é dividido pelo
    PageRank comum, para não favorecer só as contas muito conectadas
    (como comércios).
    """
    seeds = [s for s in seeds if s in graph]
    if not seeds:
        raise ValueError("nenhuma conta-semente está no grafo")
    if direction == "forward":
        g = graph
    elif direction == "backward":
        g = graph.reverse(copy=False)
    elif direction == "both":
        g = graph.to_undirected(as_view=True)
    else:
        raise ValueError("direction deve ser 'forward', 'backward' ou 'both'")
    personalization = dict.fromkeys(seeds, 1.0)
    score = pd.Series(nx.pagerank(g, alpha=alpha, personalization=personalization, weight=weight), name="risk")
    if relative:
        score = score / pd.Series(nx.pagerank(g, alpha=alpha, weight=weight))
    return score.sort_values(ascending=False)


def label_spreading(
    graph: nx.DiGraph,
    positives: Iterable,
    negatives: Iterable = (),
    alpha: float = 0.85,
    weight: str | None = None,
    max_iter: int = 200,
    tol: float = 1e-6,
) -> pd.Series:
    """Propagação de rótulos com exemplos positivos **e negativos** (Zhou et al., 2004).

    Cada conta começa com +1 (fraude conhecida), -1 (legítima conhecida) ou 0
    (desconhecida), e a cada passo recebe a média dos vizinhos, normalizada
    pelos graus (``S = D^{-1/2} W D^{-1/2}``), sem esquecer o valor inicial:
    ``F <- alpha * S F + (1 - alpha) * Y``. No fim, o escore diz de qual dos
    dois lados a conta está mais perto no grafo.

    A diferença para ``propagate_risk`` é usar também o que se sabe de bom: uma
    conta ao lado de muitas legítimas conhecidas é puxada para baixo. O grafo é
    tratado como não direcionado, e com ``weight=None`` cada par de contas pesa
    1, para os comércios, com muitos Pix, não dominarem.
    """
    nodes = list(graph.nodes)
    position = {v: i for i, v in enumerate(nodes)}
    positives = [position[v] for v in positives if v in position]
    if not positives:
        raise ValueError("nenhuma conta positiva está no grafo")
    adjacency = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight=weight, format="csr")
    symmetric = (adjacency + adjacency.T).tocsr()
    degree = np.asarray(symmetric.sum(axis=1)).ravel()
    inv_sqrt = np.divide(1.0, np.sqrt(degree), out=np.zeros_like(degree, dtype=float), where=degree > 0)
    normalized = sp.diags(inv_sqrt) @ symmetric @ sp.diags(inv_sqrt)

    seeds = np.zeros(len(nodes))
    seeds[[position[v] for v in negatives if v in position]] = -1.0
    seeds[positives] = 1.0
    scores = seeds.copy()
    for _ in range(max_iter):
        updated = alpha * (normalized @ scores) + (1 - alpha) * seeds
        converged = np.abs(updated - scores).max() < tol
        scores = updated
        if converged:
            break
    return pd.Series(scores, index=nodes, name="risk").sort_values(ascending=False)


def _as_list(sources) -> list:
    if isinstance(sources, (str, bytes)) or not isinstance(sources, Iterable):
        return [sources]
    return list(sources)


def relevant_accounts(graph: nx.DiGraph, sources: list, sink) -> set | None:
    """Contas que estão em algum caminho de uma origem até o destino."""
    downstream = set(sources)
    for s in sources:
        downstream |= nx.descendants(graph, s)
    if sink not in downstream:
        return None
    return (downstream & (nx.ancestors(graph, sink) | {sink})) | set(sources)


def _flow_network(graph: nx.DiGraph, sources: list, sink, capacity: str) -> nx.DiGraph | None:
    relevant = relevant_accounts(graph, sources, sink)
    if relevant is None:
        return None
    network = nx.DiGraph()
    for u, v, data in graph.subgraph(relevant).edges(data=True):
        network.add_edge(u, v, **{capacity: data.get(capacity, 1.0)})
    for s in sources:
        network.add_edge(SUPER_SOURCE, s)  # capacidade infinita
    return network
