"""Que tipo de rede é a do Pix? Lei de potência, componente gigante e passeios aleatórios.

Ferramentas para caracterizar a rede de transações e compará-la com os modelos
clássicos (``estudos/05_modelos_de_redes.ipynb`` e ``06_tipo_de_rede.ipynb``):

* ``degree_sequence`` e ``fit_power_law``: a distribuição de graus segue uma
  lei de potência $P(k) \\propto k^{-\\alpha}$ na cauda? O expoente é estimado
  por máxima verossimilhança, como em Clauset, Shalizi e Newman (2009);
* ``component_summary`` e ``giant_component``: quanto da rede está numa só
  componente (fraca: ignorando o sentido; forte: seguindo o sentido do dinheiro);
* ``compare_network_models``: a rede ao lado de um Erdős–Rényi e de um
  Barabási–Albert do mesmo tamanho;
* ``random_walk`` e ``random_walk_visits``: passeios que seguem o dinheiro,
  escolhendo cada próximo Pix com probabilidade proporcional ao valor. Partindo
  das vítimas, onde o dinheiro termina? (O PageRank é o mesmo passeio com
  "teletransporte"; ver ``pixfraud.flow.propagate_risk``.)

A similaridade de cosseno entre contas está em ``pixfraud.algorithms``.
"""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import numpy as np
import pandas as pd

DEGREE_KINDS = ("total", "in", "out")


def degree_sequence(graph: nx.Graph, kind: str = "total") -> np.ndarray:
    """Graus dos vértices: nº de contas distintas com que cada conta transaciona.

    ``kind``: ``"in"`` (de quantas recebe), ``"out"`` (para quantas paga) ou
    ``"total"`` (parceiros em qualquer sentido; um par que paga nos dois
    sentidos conta uma vez só).
    """
    if kind not in DEGREE_KINDS:
        raise ValueError(f"kind deve ser um de {DEGREE_KINDS}")
    if kind == "total" or not graph.is_directed():
        degrees = nx.Graph(graph).degree()
    elif kind == "in":
        degrees = graph.in_degree()
    else:
        degrees = graph.out_degree()
    return np.array([d for _, d in degrees], dtype=int)


def fit_power_law(degrees: Iterable[int], k_min: int | None = None, min_tail: int = 20) -> dict[str, float]:
    """Ajusta uma lei de potência à cauda ``k >= k_min`` da distribuição de graus.

    O expoente vem do estimador de máxima verossimilhança para dados discretos
    (aproximação de Clauset et al., 2009, eq. 3.7):

    $$\\hat\\alpha = 1 + n \\Big/ \\sum_i \\ln \\frac{k_i}{k_{\\min} - 1/2}$$

    Sem ``k_min``, testa cada grau observado (com pelo menos ``min_tail``
    vértices na cauda) e fica com o que minimiza a distância de
    Kolmogorov–Smirnov ``ks`` entre a cauda observada e a ajustada. ``ks``
    pequeno (digamos < 0,05) é compatível com lei de potência; não é um teste
    formal, que exigiria o bootstrap de Clauset et al.
    """
    k = np.sort(np.asarray([d for d in degrees if d > 0], dtype=float))
    if k.size < min_tail:
        raise ValueError(f"poucos vértices com grau > 0 ({k.size}) para ajustar a cauda")
    candidates = [k_min] if k_min is not None else np.unique(k)
    best = None
    for kmin in candidates:
        tail = k[k >= kmin]
        if tail.size < min_tail and k_min is None:
            break
        alpha = 1.0 + tail.size / np.log(tail / (kmin - 0.5)).sum()
        values = np.unique(tail)
        empirical = 1.0 - np.searchsorted(tail, values, side="left") / tail.size  # P(K >= k)
        model = ((values - 0.5) / (kmin - 0.5)) ** (1.0 - alpha)
        ks = float(np.abs(empirical - model).max())
        if best is None or ks < best["ks"]:
            best = {"alpha": float(alpha), "k_min": int(kmin), "ks": ks,
                    "n_cauda": int(tail.size), "fracao_cauda": tail.size / k.size}
    return best


def giant_component(graph: nx.Graph, strong: bool = False) -> set:
    """Vértices da maior componente: fraca (ignora o sentido) ou forte (segue o sentido)."""
    if not graph.is_directed():
        return max(nx.connected_components(graph), key=len, default=set())
    components = nx.strongly_connected_components(graph) if strong else nx.weakly_connected_components(graph)
    return max(components, key=len, default=set())


def component_summary(graph: nx.DiGraph) -> pd.Series:
    """Componentes fracas e fortes e o tamanho relativo da componente gigante de cada tipo.

    Numa rede de Pix a componente gigante **fraca** costuma ter quase todas as
    contas; a **forte** (dá para ir e voltar seguindo o dinheiro) é menor, porque
    muitas contas só pagam (vítimas) ou só recebem (comércios, coletoras).
    """
    n = graph.number_of_nodes()
    weak = list(nx.weakly_connected_components(graph))
    strong = list(nx.strongly_connected_components(graph))
    return pd.Series({
        "vertices": n,
        "isolados": nx.number_of_isolates(graph),
        "componentes_fracas": len(weak),
        "gigante_fraca": max(map(len, weak), default=0) / n if n else 0.0,
        "componentes_fortes": len(strong),
        "gigante_forte": max(map(len, strong), default=0) / n if n else 0.0,
    })


def compare_network_models(graph: nx.Graph, seed: int = 0, distance_sample: int = 200) -> pd.DataFrame:
    """A rede ao lado de um Erdős–Rényi e de um Barabási–Albert com o mesmo nº de vértices e arestas.

    Todas as redes são tratadas como não direcionadas e simples (os modelos
    clássicos são assim). Colunas: grau médio e máximo, expoente e ``ks`` da
    lei de potência, agrupamento médio, fração na componente gigante e
    distância média (estimada a partir de ``distance_sample`` origens).
    """
    simple = nx.Graph(graph)
    simple.remove_edges_from(nx.selfloop_edges(simple))
    n, m = simple.number_of_nodes(), simple.number_of_edges()
    models = {
        "rede analisada": simple,
        "Erdős–Rényi": nx.gnm_random_graph(n, m, seed=seed),
        "Barabási–Albert": nx.barabasi_albert_graph(n, max(1, round(m / n)), seed=seed),
    }
    rows = {}
    for name, g in models.items():
        degrees = degree_sequence(g)
        fit = fit_power_law(degrees)
        rows[name] = {
            "vertices": g.number_of_nodes(),
            "arestas": g.number_of_edges(),
            "grau_medio": degrees.mean(),
            "grau_maximo": int(degrees.max()),
            "alpha": fit["alpha"],
            "k_min": fit["k_min"],
            "ks": fit["ks"],
            "agrupamento_medio": nx.average_clustering(g),
            "gigante": len(giant_component(g)) / g.number_of_nodes(),
            "distancia_media": _mean_distance(g, distance_sample, seed),
        }
    return pd.DataFrame(rows).T


def _mean_distance(graph: nx.Graph, sample: int, seed: int) -> float:
    """Distância média na componente gigante, a partir de ``sample`` origens sorteadas."""
    giant = graph.subgraph(giant_component(graph))
    nodes = list(giant)
    rng = np.random.default_rng(seed)
    sources = rng.choice(len(nodes), size=min(sample, len(nodes)), replace=False)
    total = pairs = 0
    for i in sources:
        lengths = nx.single_source_shortest_path_length(giant, nodes[i])
        total += sum(lengths.values())
        pairs += len(lengths) - 1
    return total / pairs if pairs else float("nan")


def random_walk(
    graph: nx.DiGraph,
    start,
    max_steps: int = 20,
    weight: str | None = "amount",
    rng: np.random.Generator | int | None = None,
) -> list:
    """Um passeio aleatório que segue o dinheiro a partir de ``start``.

    A cada passo, sai por um dos Pix enviados pela conta atual, com
    probabilidade proporcional a ``weight`` (``None``: todos iguais). Para ao
    chegar numa conta que não pagou ninguém (um sorvedouro) ou depois de
    ``max_steps`` passos. Devolve a lista de contas visitadas, com ``start``.
    """
    rng = np.random.default_rng(rng)
    path = [start]
    for _ in range(max_steps):
        out = list(graph.out_edges(path[-1], data=weight if weight else False, default=1.0))
        if not out:
            break
        if weight:
            p = np.array([w for _, _, w in out], dtype=float)
            p = p / p.sum()
        else:
            p = None
        path.append(out[rng.choice(len(out), p=p)][1])
    return path


def random_walk_visits(
    graph: nx.DiGraph,
    starts: Iterable,
    walks_per_start: int = 20,
    max_steps: int = 20,
    weight: str | None = "amount",
    seed: int = 0,
) -> pd.DataFrame:
    """Faz ``walks_per_start`` passeios a partir de cada conta de ``starts``.

    Devolve, por conta, a fração dos passeios que passou por ela (``visitas``,
    sem contar o ponto de partida) e a fração que terminou nela (``destino``).
    Partindo das vítimas, as coletoras aparecem no topo de ``destino``: é
    para onde o dinheiro do golpe escorre.
    """
    rng = np.random.default_rng(seed)
    visits: dict = {}
    ends: dict = {}
    n_walks = 0
    for start in starts:
        if start not in graph:
            continue
        for _ in range(walks_per_start):
            path = random_walk(graph, start, max_steps, weight, rng)
            n_walks += 1
            for v in set(path[1:]):
                visits[v] = visits.get(v, 0) + 1
            ends[path[-1]] = ends.get(path[-1], 0) + 1
    if not n_walks:
        raise ValueError("nenhuma conta de partida está no grafo")
    table = pd.DataFrame({"visitas": pd.Series(visits, dtype=float), "destino": pd.Series(ends, dtype=float)})
    return (table.fillna(0.0) / n_walks).sort_values(["destino", "visitas"], ascending=False)
