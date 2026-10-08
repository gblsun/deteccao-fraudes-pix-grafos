"""PageRank personalizado ("culpa por associação"): a suspeita parte das fraudes já conhecidas."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import pandas as pd


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
