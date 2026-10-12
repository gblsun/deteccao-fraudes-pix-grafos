"""Visualizações dos grafos.

* ``draw_graph``, ``to_html`` e ``save_graph``: desenhar e exportar grafos
  pequenos (estudo, padrões de fraude, vizinhança de uma conta);
* ``plot_heat_graph`` e ``plot_risk_heatmap``: interpretar os resultados dos
  detectores. Os escores de modelos diferentes têm escalas diferentes, por
  isso as cores usam o percentil do risco (0 = menos suspeita, 1 = mais);
* ``plot_value_matrix``: tabela colorida de resultados (conjunto de atributos
  × cenário, tipologia × modelo...), com o valor escrito em cada célula.
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

# Figuras de resultados: rampa sequencial azul (magnitude) e par divergente
# azul/vermelho com meio cinza (sinal de um efeito). Tinta e superfície neutras.
SEQUENTIAL_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "sequencial", ["#f0efec", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
DIVERGING_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "divergente", ["#184f95", "#6da7ec", "#f0efec", "#ec8a89", "#a82f2f"]
)
INK, INK_SECONDARY, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

# Uma cor por modelo, a mesma em todas as figuras. Famílias próximas têm tons
# próximos: os detectores de densidade em azul, os de fronteira/reconstrução em
# verde, os de grafo em roxo, a propagação em laranja e os tetos supervisionados em cinza.
MODEL_COLORS = {
    "isolation_forest": "#e45756",
    "dbscan": "#256abf",
    "local_outlier_factor": "#6da7ec",
    "ecod": "#b8860b",
    "one_class_svm": "#54a24b",
    "autoencoder": "#88c77f",
    "knn": "#0b3d7a",
    "kmeans": "#2a9d8f",
    "pca": "#3c7a36",
    "fraudar": "#7a5cc7",
    "node2vec_if": "#b279a2",
    "dominant": "#d4a6e8",
    "propagacao": "#f58518",
    "propagacao_relativa": "#f58518",
    "label_spreading": "#ffbf79",
    "combinado": "#c4661f",
    "label_spreading_combinado": "#e8a33d",
    "random_forest": "#52514e",
    "gradient_boosting": "#8a8a8a",
    "graphsage": "#0b0b0b",
}


MODEL_LABELS = {
    "isolation_forest": "Isolation Forest",
    "dbscan": "DBSCAN",
    "local_outlier_factor": "LOF",
    "ecod": "ECOD",
    "one_class_svm": "One-Class SVM",
    "autoencoder": "Autoencoder",
    "knn": "kNN",
    "kmeans": "k-means",
    "pca": "PCA",
    "fraudar": "FRAUDAR",
    "node2vec_if": "node2vec + IF",
    "propagacao": "PageRank personalizado",
    "propagacao_relativa": "PageRank relativo",
    "label_spreading": "Label spreading",
    "combinado": "PageRank + DBSCAN",
    "label_spreading_combinado": "Label spreading + DBSCAN",
    "random_forest": "Random Forest",
    "gradient_boosting": "Gradient boosting",
    "graphsage": "GraphSAGE",
    "graphsage_propria": "GraphSAGE (própria)",
    "dominant": "DOMINANT",
}


def model_color(model: str) -> str:
    """Cor fixa de um modelo nas figuras (cinza-médio para um modelo sem cor definida)."""
    return MODEL_COLORS.get(model, "#9aa7a4")


def model_label(model: str) -> str:
    """Nome legível de um modelo, o mesmo em todas as figuras e tabelas."""
    return MODEL_LABELS.get(model, model.replace("_", " "))


def format_number(value: float, digits: int = 2) -> str:
    """Número com vírgula decimal, como no resto da documentação (``0,58``)."""
    return f"{value:.{digits}f}".replace(".", ",")


def format_ci(mean: float, low: float, high: float, digits: int = 2) -> str:
    """Média e intervalo de confiança no formato único dos resultados: ``0,58 [0,52; 0,63]``."""
    if pd.isna(mean):
        return "—"
    if pd.isna(low) or pd.isna(high):
        return format_number(mean, digits)
    return f"{format_number(mean, digits)} [{format_number(low, digits)}; {format_number(high, digits)}]"


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
    valores; o tamanho do vértice é proporcional ao grau. Para a rede inteira
    (milhares de contas), use ``pixfraud.explorer``.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph_html(graph, color_by=color_by, title=title, cmap=cmap), encoding="utf-8")
    return path


def graph_html(graph: nx.Graph, color_by="role", title: str = "Grafo de transações", cmap: str = CMAP) -> str:
    """O HTML interativo de ``to_html`` como texto (para embutir, por exemplo, no app Streamlit)."""
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
    return page


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
  .legend i { display: inline-block; width: 11px; height: 11px; border-radius: 50%;
              margin-right: 5px; vertical-align: -1px; }
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


def explain_account(
    graph: nx.DiGraph,
    features: pd.DataFrame,
    risk: pd.Series,
    account,
    fraud: pd.Series | None = None,
    max_neighbors: int = 12,
    color_by="role",
) -> plt.Figure:
    """Ficha da conta: por que ela foi considerada suspeita?

    * à esquerda, a vizinhança (as ``max_neighbors`` contas com quem ela mais
      movimentou dinheiro);
    * à direita, o percentil de cada atributo da conta em relação a todas as
      contas (barras perto de 0 ou de 1 são os valores extremos que chamaram
      a atenção do detector);
    * embaixo, a posição da conta no ranking de risco.
    """
    volume: dict = {}
    for u, _, data in graph.in_edges(account, data=True):
        volume[u] = volume.get(u, 0.0) + data.get("amount", 1.0)
    for _, v, data in graph.out_edges(account, data=True):
        volume[v] = volume.get(v, 0.0) + data.get("amount", 1.0)
    keep = sorted(volume, key=volume.get, reverse=True)[:max_neighbors]
    neighborhood = graph.subgraph([account, *keep])

    fig = plt.figure(figsize=(13, 6.5), layout="constrained")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[4, 1])
    ax_graph, ax_bars, ax_text = fig.add_subplot(grid[:, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, 1])

    has_roles = any("role" in data for _, data in neighborhood.nodes(data=True))
    draw_graph(
        neighborhood, color_by=color_by if has_roles else risk.rank(pct=True).rename("percentil de risco"),
        layout="kamada_kawai", edge_labels="amount", ax=ax_graph,
        title=f"Vizinhança de {account} ({len(keep)} de {len(volume)} contas)",
    )

    percentile = features.rank(pct=True).loc[account].sort_values()
    colormap = plt.get_cmap(CMAP)
    colors = [colormap(0.15 + 0.85 * abs(p - 0.5) * 2) for p in percentile]
    ax_bars.barh(percentile.index, percentile.to_numpy(), color=colors)
    ax_bars.axvline(0.5, color="#888888", lw=0.8, ls="--")
    ax_bars.set_xlim(0, 1)
    ax_bars.set_xlabel("percentil entre todas as contas (0 = menor valor, 1 = maior)")
    ax_bars.tick_params(axis="y", labelsize=8)
    ax_bars.set_title("Atributos: quanto mais longe de 0,5, mais incomum")

    position = int(risk.rank(ascending=False, method="min")[account])
    above = f"{(len(risk) - position) / len(risk):.1%}".replace(".", ",")  # .1%: a 9ª de 2.136 não é "100%"
    lines = [f"Posição no ranking de risco: {position}ª de {len(risk)} contas (mais suspeita que {above} das contas)"]
    if fraud is not None:
        lines.append("Rótulo verdadeiro: " + ("FRAUDE" if bool(fraud.get(account, False)) else "legítima"))
    ax_text.axis("off")
    ax_text.text(0, 0.6, "\n".join(lines), fontsize=10, va="center")
    return fig


def plot_value_matrix(
    matrix: pd.DataFrame,
    cmap=SEQUENTIAL_CMAP,
    vmin: float = 0.0,
    vmax: float = 1.0,
    fmt: str = "{:.2f}",
    ax: plt.Axes | None = None,
):
    """Matriz de resultados: uma célula colorida por valor, com o número escrito nela.

    As células têm 2px de respiro entre si; o texto fica branco nas células
    escuras. Os rótulos vêm do índice (linhas) e das colunas de ``matrix``
    (troque-os depois com ``ax.set_xticks`` se precisar). Devolve a malha,
    para a barra de cores.
    """
    ax = ax or plt.gca()
    values = matrix.to_numpy(dtype=float)
    mesh = ax.pcolormesh(values, cmap=cmap, vmin=vmin, vmax=vmax, edgecolors=SURFACE, linewidth=2)
    for (i, j), value in np.ndenumerate(values):
        if np.isnan(value):
            continue
        r, g, b = mcolors.to_rgb(cmap((value - vmin) / (vmax - vmin)))
        dark = 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5
        ax.text(j + 0.5, i + 0.5, fmt.format(value).replace(".", ","), ha="center", va="center",
                fontsize=8, color="#ffffff" if dark else INK)
    ax.set_xticks(np.arange(values.shape[1]) + 0.5, [str(c) for c in matrix.columns], fontsize=8)
    ax.set_yticks(np.arange(values.shape[0]) + 0.5, [str(i) for i in matrix.index], fontsize=8)
    ax.set_ylim(values.shape[0], 0)  # primeira linha em cima (sem inverter: eixos compartilhados inverteriam de novo)
    ax.set_facecolor(SURFACE)
    ax.tick_params(length=0, colors=INK_SECONDARY)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return mesh


def plot_model_intervals(
    summary: pd.DataFrame,
    ax: plt.Axes,
    baseline: float | None = None,
    groups: dict[str, str] | None = None,
    xlabel: str = "average precision (média e IC 95%)",
    xlim: tuple[float, float] = (0.0, 1.0),
    group_labels: bool = True,
) -> None:
    """Um modelo por linha: média e IC 95%, na cor fixa do modelo, de cima para baixo.

    ``summary`` tem os índices = modelos (na ordem desejada) e as colunas
    ``mean``, ``ic_inferior`` e ``ic_superior`` (a saída de
    ``stats.summarize_runs``). ``baseline`` desenha a linha "ao acaso" (a taxa de
    fraude: uma ordenação aleatória tem AP igual a ela). ``groups`` (modelo ->
    família) separa as famílias com faixas de fundo alternadas e o nome da
    família à direita. É o formato padrão dos resultados de modelos.
    """
    models = list(summary.index)
    y = np.arange(len(models))[::-1]
    if groups:
        families = [groups.get(m, "") for m in models]
        start = 0
        for i in range(1, len(models) + 1):
            if i == len(models) or families[i] != families[start]:
                top, bottom = y[start] + 0.5, y[i - 1] - 0.5
                if len(dict.fromkeys(families[:start])) % 2 == 0:
                    ax.axhspan(bottom, top, color="#f0efec", zorder=0)
                if group_labels:
                    ax.text(1.01, (top + bottom) / 2, families[start], transform=ax.get_yaxis_transform(),
                            va="center", ha="left", fontsize=8, color=INK_SECONDARY)
                start = i
    for yi, model in zip(y, models):
        row = summary.loc[model]
        # o IC t pode passar de [0, 1] com poucas sementes; a AP não passa
        low = row["mean"] - max(row["ic_inferior"], xlim[0])
        high = min(row["ic_superior"], xlim[1]) - row["mean"]
        xerr = None if pd.isna(low) else [[max(low, 0)], [max(high, 0)]]
        ax.errorbar(row["mean"], yi, xerr=xerr, fmt="o", ms=5, capsize=2.5, color=model_color(model), zorder=3)
        ax.text(row["mean"], yi + 0.28, format_number(row["mean"]), ha="center", va="bottom", fontsize=7,
                color=INK_SECONDARY)
    if baseline is not None:
        ax.axvline(baseline, color=INK_SECONDARY, linestyle="--", linewidth=0.9, zorder=1)
        ax.text(baseline, y.max() + 0.55, " ao acaso", fontsize=7, color=INK_SECONDARY, va="bottom")
    ax.set_yticks(y, [model_label(m) for m in models], fontsize=8)
    ax.set_ylim(-0.6, len(models) - 0.4)
    ax.set_xlim(*xlim)
    ax.set_xlabel(xlabel, fontsize=8, color=INK_SECONDARY)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def plot_critical_difference(ranks: pd.DataFrame, critical: float, ax: plt.Axes, between: str = "modelo") -> None:
    """Postos médios do teste de Friedman com a diferença crítica de Nemenyi.

    ``ranks`` é a tabela de postos de ``stats.friedman_models`` (um grupo).
    Cada modelo é um ponto no seu posto médio (1 = melhor), com uma barra de
    ± CD/2: **dois modelos cujas barras não se tocam diferem**; os que se tocam
    não se distinguem com estas sementes. Ganham cor os modelos que não se
    distinguem do primeiro colocado.
    """
    table = ranks.sort_values("posto médio").reset_index(drop=True)
    best = table["posto médio"].iloc[0]
    y = np.arange(len(table))[::-1]
    for yi, (_, row) in zip(y, table.iterrows()):
        rank = row["posto médio"]
        tied = rank - best < critical
        color = model_color(row[between]) if tied else "#c4cbc9"
        ax.plot([rank - critical / 2, rank + critical / 2], [yi, yi], color=color, linewidth=3, alpha=0.45,
                solid_capstyle="round", zorder=2)
        ax.plot(rank, yi, "o", ms=6, color=color if tied else "#9aa7a4", zorder=3)
        ax.text(1.01, yi, f"posto {format_number(rank, 2)}", transform=ax.get_yaxis_transform(), va="center",
                fontsize=7, color=INK_SECONDARY)
    ax.axvspan(best, best + critical, color="#2e8540", alpha=0.06, zorder=1)
    ax.set_yticks(y, [model_label(m) for m in table[between]], fontsize=8)
    ax.set_ylim(-0.6, len(table) - 0.4)
    ax.set_xlabel(f"posto médio (1 = melhor); barra = diferença crítica {format_number(critical, 2)}",
                  fontsize=8, color=INK_SECONDARY)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def plot_differences(
    comparisons: pd.DataFrame,
    ax: plt.Axes,
    xlabel: str = "diferença de AP (A − B), IC 95%",
    alpha: float = 0.05,
) -> None:
    """Gráfico de diferenças: uma comparação "A − B" por linha, com IC 95% e o placar.

    ``comparisons`` é a saída de ``stats.compare_runs`` (uma métrica). Verde:
    A melhor; vermelho: B melhor; cinza: sem diferença clara. Só ganha cor a
    diferença com p de Wilcoxon corrigido por Holm abaixo de ``alpha`` (com
    poucas sementes, nada ganha cor, e isso é o certo). À direita, "vence em X
    de N" e o p. É o formato padrão dos comparativos em todos os estudos.
    """
    table = comparisons.reset_index(drop=True)
    y = np.arange(len(table))[::-1]
    for yi, (_, row) in zip(y, table.iterrows()):
        p_holm = row.get("p Wilcoxon (Holm)", np.nan)
        if pd.isna(p_holm) or p_holm >= alpha:
            color = "#9aa7a4"
        else:
            color = "#2e8540" if row["diferença média"] > 0 else "#a82f2f"
        ax.errorbar(row["diferença média"], yi,
                    xerr=[[row["diferença média"] - row["ic_inferior"]], [row["ic_superior"] - row["diferença média"]]],
                    fmt="o", ms=5, capsize=2.5, color=color, zorder=3)
        p = row.get("p Wilcoxon (Holm)", np.nan)
        placar = f"vence em {int(row['a vence em'])} de {int(row['n'])}"
        if not pd.isna(p):
            placar += f" · p = {format_number(p, 3)}"
        ax.text(1.01, yi, placar, transform=ax.get_yaxis_transform(), va="center", fontsize=7, color=INK_SECONDARY)
    labels = []
    for text in table["comparação"]:
        a, b = text.split(" - ")
        labels.append(f"{model_label(a)} − {model_label(b)}")
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks(y, labels, fontsize=8)
    ax.set_ylim(-0.6, len(table) - 0.4)
    ax.set_xlabel(xlabel, fontsize=8, color=INK_SECONDARY)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
