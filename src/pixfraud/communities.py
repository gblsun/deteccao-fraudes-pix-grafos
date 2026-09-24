"""Comunidades, núcleos, subgrafos densos e egonets.

Todas as funções trabalham na versão não direcionada do grafo (ida e volta
viram uma aresta só), porque aqui interessa *quem se relaciona com quem*.

* ``detect_communities``: Louvain ou propagação de rótulos;
* ``participation_coefficient``: quanto as ligações de uma conta se espalham
  por comunidades diferentes (contas-ponte);
* ``core_numbers``: decomposição em k-núcleos;
* ``densest_subgraph``: subgrafo mais denso pelo algoritmo guloso de Charikar,
  com a opção de pesos do FRAUDAR, que resistem a camuflagem;
* ``peeling_scores``: a mesma remoção gulosa transformada em escore por conta
  (o núcleo ponderado), usada pelo detector ``fraudar`` de ``pixfraud.graph_models``;
* ``oddball_scores``: anomalias de egonet (OddBall).
"""

from __future__ import annotations

import heapq
import itertools

import networkx as nx
import numpy as np
import pandas as pd

STRUCTURAL_EXTRA = ["core_number", "participation", "oddball_en", "oddball_ew"]


def undirected_simple(graph: nx.Graph, weight: str | None = None) -> nx.Graph:
    """Versão não direcionada e simples (sem laços). Com ``weight``, soma os pesos de ida e volta."""
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes)
    for u, v, data in graph.edges(data=True):
        if u == v:
            continue
        w = data.get(weight, 1.0) if weight else 1.0
        if simple.has_edge(u, v):
            simple[u][v]["weight"] += w
        else:
            simple.add_edge(u, v, weight=w)
    return simple


def detect_communities(
    graph: nx.Graph,
    method: str = "louvain",
    seed: int = 42,
    weight: str | None = None,
    resolution: float = 1.0,
) -> pd.Series:
    """Comunidade de cada conta (0 = a maior).

    ``method="louvain"`` maximiza a modularidade (Blondel et al., 2008);
    ``"label_propagation"`` é mais rápido: cada conta adota o rótulo mais comum
    entre os vizinhos até estabilizar. Por padrão ignora os valores
    (``weight=None``); com ``weight="amount"``, arestas de valor alto pesam mais.
    """
    simple = undirected_simple(graph, weight)
    w = "weight" if weight else None
    if method == "louvain":
        groups = nx.community.louvain_communities(simple, weight=w, resolution=resolution, seed=seed)
    elif method == "label_propagation":
        groups = nx.community.asyn_lpa_communities(simple, weight=w, seed=seed)
    else:
        raise ValueError("method deve ser 'louvain' ou 'label_propagation'")
    ordered = sorted(groups, key=len, reverse=True)
    return pd.Series({v: i for i, group in enumerate(ordered) for v in group}, name="community")


def community_summary(graph: nx.Graph, communities: pd.Series, labels: pd.Series | None = None) -> pd.DataFrame:
    """Tamanho, arestas internas e externas de cada comunidade (e nº de fraudes, se ``labels``)."""
    simple = undirected_simple(graph)
    rows = {c: {"contas": 0, "arestas internas": 0, "arestas externas": 0} for c in communities.unique()}
    for v, c in communities.items():
        rows[c]["contas"] += 1
    for u, v in simple.edges():
        cu, cv = communities[u], communities[v]
        if cu == cv:
            rows[cu]["arestas internas"] += 1
        else:
            rows[cu]["arestas externas"] += 1
            rows[cv]["arestas externas"] += 1
    summary = pd.DataFrame.from_dict(rows, orient="index").sort_index()
    size = summary["contas"]
    summary["densidade interna"] = summary["arestas internas"] / (size * (size - 1) / 2).where(size > 1)
    if labels is not None:
        summary["fraudes"] = labels.reindex(communities.index).fillna(False).astype(bool).groupby(communities).sum()
    summary.index.name = "comunidade"
    return summary


def participation_coefficient(graph: nx.Graph, communities: pd.Series) -> pd.Series:
    """Coeficiente de participação (Guimerà e Amaral, 2005).

    $P_i = 1 - \\sum_c (k_{ic} / k_i)^2$, em que $k_{ic}$ é o nº de vizinhos de
    $i$ na comunidade $c$. Vale 0 quando todos os vizinhos estão numa mesma
    comunidade e se aproxima de 1 quando eles se espalham por muitas.
    """
    simple = undirected_simple(graph)
    result = {}
    for v in simple:
        k = simple.degree(v)
        if k == 0:
            result[v] = 0.0
            continue
        counts = pd.Series([communities[u] for u in simple[v]]).value_counts()
        result[v] = 1.0 - float(((counts / k) ** 2).sum())
    return pd.Series(result, name="participation")


def core_numbers(graph: nx.Graph) -> pd.Series:
    """k-núcleo de cada conta: o maior k tal que ela está num subgrafo em que todos têm grau >= k."""
    return pd.Series(nx.core_number(undirected_simple(graph)), name="core_number")


def densest_subgraph(graph: nx.Graph, weight: str | None = None, fraudar: bool = False) -> tuple[set, float]:
    """Subgrafo de maior densidade (peso total / nº de contas), pelo algoritmo guloso de Charikar.

    Remove, uma a uma, a conta de menor grau (ponderado) e guarda o melhor
    momento. É uma aproximação de fator 2 do ótimo e roda em O(m log n).

    Com ``fraudar=True``, cada aresta ``u -> v`` pesa $1 / \\log(d^-(v) + 5)$,
    como no FRAUDAR (Hooi et al., 2016). Assim, Pix para contas muito
    procuradas (comércios) valem pouco, e a camuflagem "pagar a padaria" não
    ajuda uma quadrilha a se esconder.
    """
    simple = _fraudar_weighted(graph) if fraudar else undirected_simple(graph, weight)
    if simple.number_of_nodes() == 0:
        return set(), 0.0
    order, _, densities = _peel(simple)
    best_cut = int(np.argmax(densities))  # densities[i]: densidade depois de tirar as i primeiras contas
    return set(simple) - set(order[:best_cut]), float(densities[best_cut])


def peeling_scores(graph: nx.Graph, weight: str | None = None, fraudar: bool = True) -> pd.Series:
    """Escore por conta tirado da mesma remoção gulosa do ``densest_subgraph``.

    O escore de uma conta é o maior grau (ponderado) que a remoção já tinha
    precisado atingir quando chegou a ela: a generalização do k-núcleo para
    pesos. Uma conta num bloco denso só sai quando a remoção já está "cortando
    fundo", então fica com escore alto; e, ao contrário do subgrafo mais denso,
    que devolve um bloco só, cada bloco denso (cada quadrilha) recebe o seu
    nível. Empates são desfeitos pela ordem de remoção: quem sai depois fica
    à frente. Com ``fraudar=True`` (padrão), usa os pesos do FRAUDAR.
    """
    simple = _fraudar_weighted(graph) if fraudar else undirected_simple(graph, weight)
    order, removal_degree, _ = _peel(simple)
    level = np.maximum.accumulate(removal_degree) if len(order) else np.array([])
    tie_break = np.arange(len(order)) / max(len(order), 1) * 1e-9 * (level.max() if len(order) else 0.0)
    return pd.Series(level + tie_break, index=order, name="score").reindex(list(graph.nodes), fill_value=0.0)


def _fraudar_weighted(graph: nx.Graph) -> nx.Graph:
    """Grafo simples com o peso do FRAUDAR, ``1 / log(grau de entrada do destino + 5)``, em cada aresta."""
    in_degree = dict(graph.in_degree()) if graph.is_directed() else dict(graph.degree())
    weighted = nx.DiGraph() if graph.is_directed() else nx.Graph()
    weighted.add_nodes_from(graph.nodes)
    for u, v in graph.edges():
        weighted.add_edge(u, v, fraudar=1.0 / np.log(in_degree[v] + 5))
    return undirected_simple(weighted, "fraudar")


def _peel(simple: nx.Graph) -> tuple[list, np.ndarray, np.ndarray]:
    """Remoção gulosa de Charikar: tira sempre a conta de menor grau ponderado.

    Devolve a ordem de remoção, o grau de cada conta no momento em que saiu e a
    densidade (peso total / nº de contas) antes de cada remoção e no fim.
    """
    degree = {v: sum(d["weight"] for d in simple[v].values()) for v in simple}
    total = sum(d["weight"] for *_, d in simple.edges(data=True))
    remaining = simple.number_of_nodes()
    counter = itertools.count()
    heap = [(d, next(counter), v) for v, d in degree.items()]
    heapq.heapify(heap)
    removed, order, removal_degree = set(), [], []
    densities = [total / remaining if remaining else 0.0]
    while heap:
        d, _, v = heapq.heappop(heap)
        if v in removed or d != degree[v]:
            continue  # entrada desatualizada
        removed.add(v)
        order.append(v)
        removal_degree.append(degree[v])
        total -= degree[v]
        remaining -= 1
        for u, data in simple[v].items():
            if u not in removed:
                degree[u] -= data["weight"]
                heapq.heappush(heap, (degree[u], next(counter), u))
        densities.append(total / remaining if remaining else 0.0)
    return order, np.array(removal_degree, dtype=float), np.array(densities)


def egonet_features(graph: nx.Graph, weight: str = "amount") -> pd.DataFrame:
    """Medidas da egonet (a conta, seus vizinhos e as arestas entre eles).

    * ``n_neighbors`` ($N$): vizinhos distintos;
    * ``egonet_edges`` ($E$): arestas da egonet = $N$ + triângulos da conta;
    * ``egonet_weight`` ($W$): valor total dos Pix da conta (entrada + saída).
    """
    simple = undirected_simple(graph)
    triangles = nx.triangles(simple)
    if graph.is_directed():
        strength = {v: graph.in_degree(v, weight=weight) + graph.out_degree(v, weight=weight) for v in graph}
    else:
        strength = dict(graph.degree(weight=weight))
    df = pd.DataFrame({
        "n_neighbors": pd.Series(dict(simple.degree())),
        "egonet_edges": pd.Series(dict(simple.degree())) + pd.Series(triangles),
        "egonet_weight": pd.Series(strength),
    })
    return df.astype(float)


def oddball_scores(graph: nx.Graph, weight: str = "amount") -> pd.DataFrame:
    """Escores do OddBall (Akoglu, McGlohon e Faloutsos, 2010).

    Em redes reais, as egonets seguem leis de potência: $E \\propto N^{\\alpha}$
    e $W \\propto E^{\\beta}$. Ajustamos as retas em escala log-log e medimos o
    quanto cada conta se afasta delas:

    $$\\text{escore} = \\frac{\\max(y, \\hat y)}{\\min(y, \\hat y)} \\cdot \\log(|y - \\hat y| + 1)$$

    * ``oddball_en``: vizinhança "estrela" (vizinhos que não se conhecem, como
      as vítimas de uma laranja) ou "quase clique";
    * ``oddball_ew``: muito dinheiro para o tamanho da vizinhança.
    """
    ego = egonet_features(graph, weight)
    scores = pd.DataFrame(0.0, index=ego.index, columns=["oddball_en", "oddball_ew"])
    valid = ego[(ego["n_neighbors"] >= 2) & (ego["egonet_weight"] > 0)]
    if len(valid) >= 3:
        scores.loc[valid.index, "oddball_en"] = _power_law_score(valid["n_neighbors"], valid["egonet_edges"])
        scores.loc[valid.index, "oddball_ew"] = _power_law_score(valid["egonet_edges"], valid["egonet_weight"])
    return scores


def structural_features(graph: nx.Graph, communities: pd.Series | None = None, seed: int = 42) -> pd.DataFrame:
    """Atributos ``STRUCTURAL_EXTRA`` por conta, prontos para ``pixfraud.features``."""
    if communities is None:
        communities = detect_communities(graph, seed=seed)
    df = pd.concat(
        [core_numbers(graph), participation_coefficient(graph, communities), oddball_scores(graph)],
        axis=1,
    )
    return df[STRUCTURAL_EXTRA].astype(float)


def _power_law_score(x: pd.Series, y: pd.Series) -> np.ndarray:
    slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
    expected = np.exp(intercept) * x**slope
    ratio = np.maximum(y, expected) / np.minimum(y, expected)
    return (ratio * np.log(np.abs(y - expected) + 1)).to_numpy()
