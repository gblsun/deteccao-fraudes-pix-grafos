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

As duas últimas são modelos semi-supervisionados e moram em
``pixfraud.models.semi_supervised``; continuam importáveis daqui.

Atenção: no grafo agregado o tempo é ignorado. Para respeitar a ordem dos Pix,
aplique estas funções sobre ``pixfraud.temporal.temporal_trail``.
"""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

from pixfraud.models.semi_supervised import label_spreading, propagate_risk

__all__ = ["blocking_accounts", "blocking_cut", "label_spreading", "max_money_flow", "propagate_risk",
           "relevant_accounts"]

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
        """Nó de saída de uma conta dividida (as fixas não se dividem)."""
        return v if v in fixed else (v, "saida")

    def head(v):
        """Nó de entrada de uma conta dividida (as fixas não se dividem)."""
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


def _as_list(sources) -> list:
    """Uma conta ou uma coleção de contas, sempre como lista."""
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
    """Rede de fluxo só com as contas entre as origens e o destino, com uma super-origem."""
    relevant = relevant_accounts(graph, sources, sink)
    if relevant is None:
        return None
    network = nx.DiGraph()
    for u, v, data in graph.subgraph(relevant).edges(data=True):
        network.add_edge(u, v, **{capacity: data.get(capacity, 1.0)})
    for s in sources:
        network.add_edge(SUPER_SOURCE, s)  # capacidade infinita
    return network
