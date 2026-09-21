"""Visualizações dos grafos.

* ``draw_graph``, ``to_html`` e ``save_graph``: desenhar e exportar grafos
  pequenos (estudo, padrões de fraude, vizinhança de uma conta);
* ``plot_heat_graph`` e ``plot_risk_heatmap``: interpretar os resultados dos
  detectores. Os escores de modelos diferentes têm escalas diferentes, por
  isso as cores usam o percentil do risco (0 = menos suspeita, 1 = mais).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

CMAP = "YlOrRd"
ROLE_COLORS = {
    "normal": "#b0b0b0",
    "comercio": "#4c78a8",
    "vitima": "#54a24b",
    "laranja": "#f58518",
    "intermediario": "#b279a2",
    "coletor": "#e45756",
}
LAYOUTS = ("auto", "flow", "spring", "circular", "kamada_kawai", "shell")
VIS_NETWORK_URL = "https://cdn.jsdelivr.net/npm/vis-network@9.1.9/standalone/umd/vis-network.min.js"


def flow_layout(graph: nx.DiGraph) -> dict:
    """Posiciona os vértices da esquerda para a direita, no sentido do dinheiro.

    Só vale para grafos direcionados acíclicos: cada coluna é uma "geração"
    topológica (quem só envia fica à esquerda, quem só recebe à direita).
    """
    if not (graph.is_directed() and nx.is_directed_acyclic_graph(graph)):
        raise ValueError("o layout 'flow' só funciona em grafos direcionados acíclicos")
    layers = [sorted(nodes, key=str) for nodes in nx.topological_generations(graph)]
    position = {}

    def reorder(k: int, neighbors) -> None:
        # Heurística do baricentro: cada vértice vai para perto da posição
        # média dos seus vizinhos na coluna ao lado, o que reduz cruzamentos.
        def barycenter(v):
            near = [position[u] for u in neighbors(v) if u in position]
            return sum(near) / len(near) if near else position.get(v, 0.0)

        layers[k].sort(key=barycenter)
        position.update({v: i / max(len(layers[k]) - 1, 1) for i, v in enumerate(layers[k])})

    for k in range(len(layers)):
        position.update({v: i / max(len(layers[k]) - 1, 1) for i, v in enumerate(layers[k])})
    for _ in range(2):
        for k in range(1, len(layers)):
            reorder(k, graph.predecessors)
        for k in range(len(layers) - 2, -1, -1):
            reorder(k, graph.successors)

    # Coluna k no eixo x; dentro da coluna, de cima para baixo, centralizado.
    return {
        v: (1.5 * k, (len(nodes) - 1) / 2 - i)
        for k, nodes in enumerate(layers)
        for i, v in enumerate(nodes)
    }


def _layout(graph: nx.Graph, layout, seed: int) -> dict:
    if isinstance(layout, dict):
        return layout
    if layout not in LAYOUTS:
        raise ValueError(f"layout deve ser um de {LAYOUTS} ou um dicionário de posições")
    if layout == "auto":
        layout = "flow" if graph.is_directed() and nx.is_directed_acyclic_graph(graph) else "kamada_kawai"
    if layout == "flow":
        return flow_layout(graph)
    if layout == "spring":
        return nx.spring_layout(graph, seed=seed)
    if layout == "kamada_kawai":
        return nx.kamada_kawai_layout(nx.Graph(graph)) if graph.number_of_nodes() > 1 else nx.circular_layout(graph)
    return getattr(nx, f"{layout}_layout")(graph)


def _node_colors(graph: nx.Graph, color_by, cmap: str = CMAP) -> tuple[dict, dict]:
    """Cor (hex) de cada vértice e itens de legenda ``{categoria: cor}``.

    ``color_by`` pode ser ``None``, o nome de um atributo categórico dos
    vértices (ex.: ``"role"``) ou uma ``pd.Series`` numérica indexada pelos
    vértices (escala contínua, sem legenda).
    """
    nodes = list(graph.nodes)
    if color_by is None:
        return dict.fromkeys(nodes, "#9ecae1"), {}
    if isinstance(color_by, pd.Series):
        values = color_by.reindex(nodes).fillna(color_by.min())
        norm = mcolors.Normalize(values.min(), values.max())
        colormap = plt.get_cmap(cmap)
        return {v: mcolors.to_hex(colormap(norm(values[v]))) for v in nodes}, {}
    categories = {v: str(graph.nodes[v].get(color_by, "?")) for v in nodes}
    palette = dict(ROLE_COLORS)
    new = [c for c in dict.fromkeys(categories.values()) if c not in palette]
    palette |= {c: mcolors.to_hex(rgb) for c, rgb in zip(new, plt.get_cmap("tab10").colors)}
    colors = {v: palette.get(c, "#999999") for v, c in categories.items()}
    return colors, {c: palette.get(c, "#999999") for c in dict.fromkeys(categories.values())}


def _format_amount(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def draw_graph(
    graph: nx.Graph,
    color_by="role",
    layout="auto",
    edge_labels: str | None = "amount",
    node_labels: bool = True,
    ax: plt.Axes | None = None,
    seed: int = 42,
    cmap: str = CMAP,
    title: str | None = None,
) -> plt.Axes:
    """Desenho estático pensado para grafos pequenos (até ~100 vértices).

    ``color_by``: nome de um atributo categórico dos vértices (``"role"`` usa
    as cores de ``ROLE_COLORS``), uma ``pd.Series`` numérica indexada pelos
    vértices (ex.: um escore de risco) ou ``None``.
    ``layout``: ``"auto"`` (fluxo da esquerda para a direita se o grafo for
    acíclico, senão Kamada-Kawai), ``"flow"``, ``"spring"``, ``"circular"``,
    ``"kamada_kawai"``, ``"shell"`` ou um dicionário ``{vértice: (x, y)}``.
    ``edge_labels``: atributo das arestas escrito sobre elas (ex.:
    ``"amount"``), ou ``None``.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))
    pos = _layout(graph, layout, seed)
    colors, legend = _node_colors(graph, color_by, cmap)
    nodes = list(graph.nodes)
    directed = graph.is_directed()
    # Arestas levemente curvas separam Pix de ida e de volta entre o mesmo par.
    style = "arc3,rad=0.12" if directed else "arc3"
    nx.draw_networkx_nodes(
        graph, pos, ax=ax, nodelist=nodes, node_color=[colors[v] for v in nodes],
        node_size=500, edgecolors="#333333", linewidths=0.8,
    )
    arrow_kwargs = {"arrowsize": 14, "node_size": 500, "connectionstyle": style} if directed else {}
    nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="#666666", arrows=directed, width=1.2, **arrow_kwargs)
    if node_labels:
        # Rótulos logo abaixo de cada vértice, para nomes longos não cobrirem o desenho.
        for v, (x, y) in pos.items():
            ax.annotate(str(v), (x, y), xytext=(0, -13), textcoords="offset points",
                        ha="center", va="top", fontsize=8)
    ax.margins(0.1)
    if edge_labels:
        if graph.is_multigraph():
            totals: dict = {}
            for u, v, value in graph.edges(data=edge_labels, default=0):
                totals[(u, v)] = totals.get((u, v), 0) + value
        else:
            totals = {(u, v): value for u, v, value in graph.edges(data=edge_labels) if value is not None}
        nx.draw_networkx_edge_labels(
            graph if not graph.is_multigraph() else nx.DiGraph(graph) if directed else nx.Graph(graph),
            pos, ax=ax, edge_labels={e: _format_amount(x) for e, x in totals.items()},
            font_size=7, connectionstyle=style, bbox={"alpha": 0.7, "color": "white", "lw": 0},
        )
    if isinstance(color_by, pd.Series):
        values = color_by.reindex(nodes)
        scale = plt.cm.ScalarMappable(norm=mcolors.Normalize(values.min(), values.max()), cmap=cmap)
        ax.figure.colorbar(scale, ax=ax, shrink=0.8, label=color_by.name or "")
    elif legend.keys() - {"?"}:
        handles = [Line2D([], [], marker="o", ls="", markersize=9, color=c, label=k) for k, c in legend.items()]
        ax.legend(handles=handles, loc="best", fontsize=8, frameon=False)
    if title:
        ax.set_title(title)
    ax.set_axis_off()
    return ax


def to_html(
    graph: nx.Graph,
    path: str | Path,
    color_by="role",
    title: str = "Grafo de transações",
    cmap: str = CMAP,
) -> Path:
    """Salva uma visualização interativa em HTML (arrastar, zoom, passar o mouse).

    Abre em qualquer navegador; precisa de internet para carregar a biblioteca
    vis-network. Passe o mouse sobre um vértice para ver papel, graus e
    valores; o tamanho do vértice é proporcional ao grau.
    """
    colors, legend = _node_colors(graph, color_by, cmap)
    directed = graph.is_directed()
    nodes = []
    for v in graph.nodes:
        lines = [f"conta: {v}"]
        if "role" in graph.nodes[v]:
            lines.append(f"papel: {graph.nodes[v]['role']}")
        if isinstance(color_by, pd.Series) and v in color_by.index:
            lines.append(f"{color_by.name or 'valor'}: {color_by[v]:.4g}")
        if directed:
            lines += [
                f"grau de entrada: {graph.in_degree(v)} | saída: {graph.out_degree(v)}",
                f"recebeu: R$ {_format_amount(graph.in_degree(v, weight='amount'))}",
                f"enviou: R$ {_format_amount(graph.out_degree(v, weight='amount'))}",
            ]
        else:
            lines.append(f"grau: {graph.degree(v)}")
        nodes.append({
            "id": str(v), "label": str(v), "title": "\n".join(lines),
            "color": colors[v], "value": graph.degree(v),
        })
    edges = [
        {
            "from": str(u), "to": str(v),
            "title": f"R$ {_format_amount(data.get('amount', 0))} ({data.get('count', 1)} Pix)",
            "value": float(data.get("amount", 1.0)),
        }
        for u, v, data in graph.edges(data=True)
    ]
    legend_html = "".join(
        f'<span><i style="background:{c}"></i>{html.escape(k)}</span>' for k, c in legend.items()
    )
    page = _HTML_TEMPLATE
    replacements = {
        "__TITLE__": html.escape(title),
        "__SCRIPT__": VIS_NETWORK_URL,
        "__LEGEND__": legend_html,
        "__NODES__": json.dumps(nodes, ensure_ascii=False).replace("</", "<\\/"),
        "__EDGES__": json.dumps(edges, ensure_ascii=False).replace("</", "<\\/"),
        "__ARROWS__": "to" if directed else "",
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return path


def save_graph(graph: nx.Graph, path: str | Path, **draw_kwargs) -> Path:
    """Salva o grafo no formato indicado pela extensão do arquivo.

    * ``.png``, ``.svg``, ``.pdf``: desenho estático (``draw_graph``);
    * ``.html``: visualização interativa (``to_html``);
    * ``.gexf``, ``.graphml``: para abrir no Gephi ou em outras ferramentas.

    ``draw_kwargs`` são repassados a ``draw_graph`` ou ``to_html``.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix in (".png", ".svg", ".pdf"):
        n = graph.number_of_nodes()
        fig, ax = plt.subplots(figsize=(min(6 + 0.15 * n, 18), min(4.5 + 0.1 * n, 14)))
        draw_graph(graph, ax=ax, **draw_kwargs)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
    elif suffix == ".html":
        to_html(graph, path, **draw_kwargs)
    elif suffix in (".gexf", ".graphml"):
        exportable = graph.copy()
        for _, data in exportable.nodes(data=True):
            data.update({k: _serializable(x) for k, x in data.items()})
        for *_, data in exportable.edges(data=True):
            data.update({k: _serializable(x) for k, x in data.items()})
        (nx.write_gexf if suffix == ".gexf" else nx.write_graphml)(exportable, path)
    else:
        raise ValueError("extensões aceitas: .png, .svg, .pdf, .html, .gexf, .graphml")
    return path


def _serializable(value):
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, np.generic):
        return value.item()
    return str(value)


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<script src="__SCRIPT__"></script>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; background: #fafafa; color: #222; }
  header { padding: 10px 16px; border-bottom: 1px solid #ddd; background: #fff; }
  h1 { font-size: 16px; margin: 0 0 6px; }
  .legend span { margin-right: 14px; font-size: 13px; white-space: nowrap; }
  .legend i { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 5px; vertical-align: -1px; }
  #graph { width: 100%; height: calc(100vh - 70px); }
  div.vis-tooltip { white-space: pre-line; font-size: 13px; }
</style>
</head>
<body>
<header><h1>__TITLE__</h1><div class="legend">__LEGEND__</div></header>
<div id="graph"></div>
<script>
  const nodes = new vis.DataSet(__NODES__);
  const edges = new vis.DataSet(__EDGES__);
  new vis.Network(document.getElementById("graph"), { nodes, edges }, {
    nodes: { shape: "dot", scaling: { min: 8, max: 30 }, font: { size: 12 }, borderWidth: 1 },
    edges: { arrows: "__ARROWS__", color: { color: "#999", highlight: "#333" },
             scaling: { min: 1, max: 6 }, smooth: { type: "curvedCW", roundness: 0.15 } },
    physics: { stabilization: { iterations: 300 } },
    interaction: { hover: true, tooltipDelay: 100 },
  });
</script>
</body>
</html>
"""


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
