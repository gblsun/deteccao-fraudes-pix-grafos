"""Visualizações para interpretar os resultados: grafo de calor e heatmap de risco.

Os escores de modelos diferentes têm escalas diferentes, por isso as cores
usam o percentil do risco (0 = menos suspeita, 1 = mais suspeita).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

CMAP = "YlOrRd"


def plot_heat_graph(
    graph: nx.DiGraph,
    risk: pd.Series,
    top_k: int = 10,
    max_neighbors: int = 8,
    fraud: pd.Series | None = None,
    ax: plt.Axes | None = None,
    seed: int = 42,
) -> plt.Axes:
    """Grafo de calor: os ``top_k`` vértices mais suspeitos e sua vizinhança.

    A cor de cada vértice é o seu percentil de risco (vértices "quentes" em
    vermelho) e o tamanho é o grau no subgrafo desenhado. De cada vértice
    suspeito são mostrados no máximo ``max_neighbors`` vizinhos, os de maior
    risco. Se ``fraud`` (rótulos verdadeiros) for informado, as contas
    fraudulentas ganham contorno preto, o que ajuda a ver acertos e erros.
    """
    percentile = risk.rank(pct=True)
    hot = list(risk.nlargest(top_k).index)
    nodes = set(hot)
    for v in hot:
        neighbors = list(set(graph.predecessors(v)) | set(graph.successors(v)))
        nodes |= set(percentile.reindex(neighbors).fillna(0).nlargest(max_neighbors).index)
    sub = graph.subgraph(nodes)
    node_list = list(sub.nodes)

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(sub, seed=seed)
    is_fraud = [bool(fraud.get(v, False)) if fraud is not None else False for v in node_list]
    nx.draw_networkx_edges(sub, pos, ax=ax, edge_color="gray", alpha=0.4, arrowsize=8, width=0.8)
    artist = nx.draw_networkx_nodes(
        sub,
        pos,
        ax=ax,
        nodelist=node_list,
        node_color=percentile.reindex(node_list).fillna(0).to_numpy(),
        cmap=CMAP,
        vmin=0,
        vmax=1,
        node_size=60 + 30 * np.array([sub.degree(v) for v in node_list]),
        edgecolors=["black" if f else "lightgray" for f in is_fraud],
        linewidths=[1.8 if f else 0.8 for f in is_fraud],
    )
    nx.draw_networkx_labels(sub, pos, ax=ax, labels={v: v for v in hot}, font_size=7)
    ax.figure.colorbar(artist, ax=ax, label="percentil de risco", shrink=0.8)
    title = f"Grafo de calor: {top_k} contas mais suspeitas e vizinhança"
    if fraud is not None:
        title += "\n(contorno preto = conta fraudulenta)"
    ax.set_title(title)
    ax.set_axis_off()
    return ax


def plot_risk_heatmap(
    features: pd.DataFrame,
    risk: pd.Series,
    top_k: int = 25,
    fraud: pd.Series | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Heatmap de risco: por que cada conta foi considerada suspeita.

    As linhas são as ``top_k`` contas de maior risco (em ordem decrescente) e
    as colunas são os atributos, coloridos pelo percentil do valor em relação a
    todas as contas. Contas fraudulentas (se ``fraud`` for informado) são
    marcadas com ``*``.
    """
    top = risk.nlargest(top_k).index
    percentile = features.rank(pct=True).loc[top]
    if ax is None:
        _, ax = plt.subplots(figsize=(1.5 + 0.55 * features.shape[1], 1.5 + 0.28 * top_k))
    image = ax.imshow(percentile.to_numpy(), cmap=CMAP, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(features.shape[1]), features.columns, rotation=45, ha="right")
    labels = [f"{a} *" if fraud is not None and fraud.get(a, False) else a for a in top]
    ax.set_yticks(range(len(top)), labels, fontsize=7)
    ax.figure.colorbar(image, ax=ax, label="percentil do atributo", shrink=0.8)
    ax.set_title(f"Heatmap de risco: {top_k} contas mais suspeitas")
    return ax
