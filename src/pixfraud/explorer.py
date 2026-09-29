"""Explorador interativo da rede inteira: uma página HTML com sigma.js (WebGL).

Mostra todas as contas e Pix de uma vez, com ferramentas dinâmicas: busca de
conta, filtro por papel, cor por papel / risco / comunidade, clique para ver a
vizinhança e os detalhes de uma conta, e uma linha do tempo que mostra a rede
crescendo dia a dia (com botão de "tocar").

O posicionamento é calculado em Python (``community_layout``): cada
comunidade (Louvain) é desenhada separadamente e as comunidades são dispostas
em espiral, com as contas da quadrilha (laranjas, intermediários e coletoras)
juntas no centro. As relações são setas de quem pagou para quem recebeu. O navegador só desenha, o que mantém a página leve mesmo com
dezenas de milhares de arestas.

Uso típico::

    save_network_explorer("reports/estudos/rede.html", graph, transactions=tx,
                          roles=papel, risk=escores)

A página abre em qualquer navegador e precisa de internet para carregar as
bibliotecas (sigma.js e graphology, via cdnjs).
"""

from __future__ import annotations

import html
import json
import math
from collections.abc import Iterable
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from pixfraud.communities import detect_communities, undirected_simple

SIGMA_URL = "https://cdnjs.cloudflare.com/ajax/libs/sigma.js/2.4.0/sigma.min.js"
GRAPHOLOGY_URL = "https://cdnjs.cloudflare.com/ajax/libs/graphology/0.25.4/graphology.umd.min.js"
GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))
CENTER_ROLES = ("laranja", "intermediario", "coletor")  # contas da quadrilha, desenhadas no centro


def community_layout(graph: nx.Graph, communities: pd.Series, seed: int = 42, center: Iterable = ()) -> dict:
    """Posições que deixam as comunidades visíveis.

    Cada comunidade recebe um disco de raio proporcional à raiz do seu tamanho
    e é desenhada por dentro com o layout de molas (spring). Os discos são
    dispostos numa espiral de girassol (ângulo áureo), do maior para o menor,
    sem se sobrepor.

    ``center``: contas que saem das suas comunidades e ficam juntas num disco no
    centro, com folga (por exemplo, as contas das quadrilhas). Assim o dinheiro
    que chega a elas aparece como setas convergindo para o meio, em vez de
    riscos cruzando a rede de um lado a outro.
    """
    simple = undirected_simple(graph)
    center = [v for v in center if v in communities.index]
    rest = communities.drop(center)
    groups = sorted(rest.groupby(rest).groups.items(), key=lambda kv: -len(kv[1]))
    radii = [math.sqrt(len(members)) for _, members in groups]
    spacing = 2.4 * max(radii, default=1.0)
    positions, placed = {}, []
    if center:
        hub_radius = _place_center(simple.subgraph(center), spacing, positions, seed)
        placed.append((np.zeros(2), hub_radius))
    for i, ((_, members), radius) in enumerate(zip(groups, radii)):
        spot = _free_spot(placed, radius, spacing, i + (1 if center else 0))
        placed.append((spot, radius))
        sub = simple.subgraph(members)
        local = nx.spring_layout(sub, seed=seed) if len(members) > 1 else {m: np.zeros(2) for m in members}
        for v, xy in local.items():
            positions[v] = spot + radius * np.asarray(xy)
    return positions


def _place_center(sub: nx.Graph, spacing: float, positions: dict, seed: int) -> float:
    """Põe cada grupo ligado de ``sub`` (uma quadrilha, em geral) num círculo em volta da origem.

    Cada quadrilha é desenhada por dentro com o layout de molas, afastada das
    outras, para que as setas entre as contas dela fiquem legíveis. Devolve o
    raio ocupado, para os outros grupos ficarem em volta.
    """
    parts = sorted(nx.connected_components(sub), key=len, reverse=True)
    part_radius = [0.22 * spacing * math.sqrt(len(p)) / 2 for p in parts]
    ring = 0.0 if len(parts) == 1 else 1.4 * max(part_radius) / math.sin(math.pi / len(parts))
    for k, (part, radius) in enumerate(zip(parts, part_radius)):
        angle = 2 * math.pi * k / len(parts)
        spot = np.array([ring * math.cos(angle), ring * math.sin(angle)])
        local = nx.spring_layout(sub.subgraph(part), seed=seed) if len(part) > 1 else {v: np.zeros(2) for v in part}
        for v, xy in local.items():
            positions[v] = spot + radius * np.asarray(xy)
    return ring + max(part_radius, default=0.0)


def explorer_payload(
    graph: nx.DiGraph,
    transactions: pd.DataFrame | None = None,
    roles: pd.Series | None = None,
    risk: pd.Series | None = None,
    communities: pd.Series | None = None,
    positions: dict | None = None,
    seed: int = 42,
    center_roles: Iterable[str] = CENTER_ROLES,
) -> dict:
    """Dados compactos (listas de números) que a página do explorador consome.

    As contas com papel em ``center_roles`` (as da quadrilha) ficam no centro do
    desenho (ver ``community_layout``); passe ``()`` para desligar.
    """
    if communities is None:
        communities = detect_communities(graph, seed=seed)
    if positions is None:
        center = [v for v in graph.nodes if roles is not None and roles.get(v) in set(center_roles)]
        positions = community_layout(graph, communities, seed=seed, center=center)
    nodes = list(graph.nodes)
    index = {v: i for i, v in enumerate(nodes)}
    xy = np.array([positions[v] for v in nodes], dtype=float)
    xy = (xy - xy.mean(axis=0)) / (np.abs(xy - xy.mean(axis=0)).max() or 1.0) * 100

    first_day, days = _first_days(graph, transactions)
    edge_fraud = {}
    if transactions is not None and "is_fraud" in transactions:
        fraud_pairs = transactions.loc[transactions["is_fraud"].astype(bool), ["sender", "receiver"]]
        edge_fraud = {tuple(p) for p in fraud_pairs.itertuples(index=False)}

    percentile = risk.rank(pct=True) if risk is not None else None
    node_rows = []
    for i, v in enumerate(nodes):
        degree = graph.in_degree(v) + graph.out_degree(v)
        node_rows.append({
            "id": str(v),
            "x": round(float(xy[i, 0]), 2),
            "y": round(float(xy[i, 1]), 2),
            "s": round(1.0 + 0.75 * math.log2(1 + degree), 2),
            "r": str(roles.get(v, "?")) if roles is not None else "?",
            "k": round(float(percentile[v]), 3) if percentile is not None and v in percentile.index else None,
            "c": int(communities.get(v, -1)),
            "i": graph.in_degree(v),
            "o": graph.out_degree(v),
            "ai": round(float(graph.in_degree(v, weight="amount")), 2),
            "ao": round(float(graph.out_degree(v, weight="amount")), 2),
        })
    edges = {"s": [], "t": [], "a": [], "n": [], "d": [], "f": []}
    node_day = [len(days) - 1 if days else 0] * len(nodes)
    for u, v, data in graph.edges(data=True):
        day = first_day.get((u, v), 0)
        edges["s"].append(index[u])
        edges["t"].append(index[v])
        edges["a"].append(round(float(data.get("amount", 1.0)), 2))
        edges["n"].append(int(data.get("count", 1)))
        edges["d"].append(day)
        edges["f"].append(1 if (u, v) in edge_fraud else 0)
        node_day[index[u]] = min(node_day[index[u]], day)
        node_day[index[v]] = min(node_day[index[v]], day)
    for row, day in zip(node_rows, node_day):
        row["d"] = day
    return {
        "nodes": node_rows,
        "edges": edges,
        "days": days,
        "hasRisk": percentile is not None,
        "hasFraudEdges": bool(edge_fraud),
        "communities": int(communities.nunique()),
    }


def network_explorer_html(
    graph: nx.DiGraph,
    transactions: pd.DataFrame | None = None,
    roles: pd.Series | None = None,
    risk: pd.Series | None = None,
    communities: pd.Series | None = None,
    title: str = "Rede Pix",
    subtitle: str = "",
    positions: dict | None = None,
    seed: int = 42,
    center_roles: Iterable[str] = CENTER_ROLES,
) -> str:
    """Página HTML completa do explorador (ver ``save_network_explorer``)."""
    payload = explorer_payload(graph, transactions, roles, risk, communities, positions, seed, center_roles)
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = _TEMPLATE
    for key, value in {
        "__TITLE__": html.escape(title),
        "__SUBTITLE__": html.escape(subtitle),
        "__SIGMA__": SIGMA_URL,
        "__GRAPHOLOGY__": GRAPHOLOGY_URL,
        "__DATA__": data,
    }.items():
        page = page.replace(key, value)
    return page


def save_network_explorer(path: str | Path, graph: nx.DiGraph, **kwargs) -> Path:
    """Salva o explorador em ``path`` (.html). Aceita os parâmetros de ``network_explorer_html``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(network_explorer_html(graph, **kwargs), encoding="utf-8")
    return path


def _free_spot(placed: list, radius: float, spacing: float, i: int) -> np.ndarray:
    """Primeiro ponto da espiral de girassol em que um disco de ``radius`` não encosta nos já colocados."""
    step = i
    while True:
        r = 0.55 * spacing * math.sqrt(step)
        candidate = np.array([r * math.cos(step * GOLDEN_ANGLE), r * math.sin(step * GOLDEN_ANGLE)])
        if all(np.linalg.norm(candidate - c) >= 1.15 * (radius + rc) for c, rc in placed):
            return candidate
        step += 1


def _first_days(graph: nx.DiGraph, transactions: pd.DataFrame | None) -> tuple[dict, list]:
    """Dia (índice) do primeiro Pix de cada aresta e a lista de dias do período."""
    if transactions is None or "timestamp" not in transactions:
        return {}, []
    stamps = pd.to_datetime(transactions["timestamp"]).dt.normalize()
    start = stamps.min()
    day_index = (stamps - start).dt.days
    first = day_index.groupby([transactions["sender"], transactions["receiver"]]).min()
    days = [d.strftime("%d/%m") for d in pd.date_range(start, stamps.max(), freq="D")]
    return {pair: int(d) for pair, d in first.items() if graph.has_edge(*pair)}, days


_TEMPLATE = r"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  :root {
    --ground: #f3f6f5;
    --surface: #ffffff;
    --ink: #172221;
    --muted: #5b6b68;
    --line: #d4dedb;
    --accent: #0f766e;
    --accent-soft: #d5ede9;
    --canvas: #fbfcfc;
    --edge: rgb(62, 84, 80);
    --edge-strong: #0f766e;
    --edge-in: #1d4ed8;
    --edge-out: #c2410c;
    --fade: #dfe6e4;
    --warn: #b42318;
    --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ground: #0d1413;
      --surface: #151f1e;
      --ink: #e2ebe9;
      --muted: #93a4a0;
      --line: #283634;
      --accent: #2dd4bf;
      --accent-soft: #123b37;
      --canvas: #101918;
      --edge: rgb(176, 206, 200);
      --edge-strong: #2dd4bf;
      --edge-in: #60a5fa;
      --edge-out: #fb923c;
      --fade: #22302e;
      --warn: #f97066;
    }
  }
  :root[data-theme="dark"] {
    --ground: #0d1413;
    --surface: #151f1e;
    --ink: #e2ebe9;
    --muted: #93a4a0;
    --line: #283634;
    --accent: #2dd4bf;
    --accent-soft: #123b37;
    --canvas: #101918;
    --edge: rgb(176, 206, 200);
    --edge-strong: #2dd4bf;
    --edge-in: #60a5fa;
    --edge-out: #fb923c;
    --fade: #22302e;
    --warn: #f97066;
  }
  html, body { height: 100%; }
  body {
    margin: 0;
    background: var(--ground);
    color: var(--ink);
    font: 14px/1.45 var(--sans);
    padding-inline: 16px;
    padding-block: 12px;
    box-sizing: border-box;
  }
  .app { display: grid; grid-template-rows: auto 1fr; gap: 12px; height: 100%; max-width: 1600px; margin: 0 auto; }
  header { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 24px; }
  h1 { font-size: 20px; font-weight: 600; margin: 0; letter-spacing: -0.01em; text-wrap: balance; }
  .sub { color: var(--muted); margin: 2px 0 0; }
  .stats { display: flex; flex-wrap: wrap; gap: 6px 20px; font-variant-numeric: tabular-nums; }
  .stat b { display: block; font: 500 18px/1.1 var(--mono); }
  .stat span { color: var(--muted); font-size: 12px; letter-spacing: 0.03em; text-transform: uppercase; }
  .main { display: grid; grid-template-columns: 260px minmax(0, 1fr) 280px; gap: 12px; min-height: 0; }
  .panel {
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px; overflow: auto; display: flex; flex-direction: column; gap: 16px; min-height: 0;
  }
  .panel h2 { font-size: 12px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); margin: 0 0 6px; }
  .field { display: flex; flex-direction: column; gap: 6px; }
  label { cursor: pointer; }
  input[type="search"], select {
    font: inherit; color: var(--ink); background: var(--canvas); border: 1px solid var(--line);
    border-radius: 6px; padding: 6px 8px; width: 100%; box-sizing: border-box;
  }
  input:focus-visible, select:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .segmented { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
  .segmented button { font: inherit; border: 0; background: var(--canvas); color: var(--ink); padding: 6px 4px; cursor: pointer; }
  .segmented button + button { border-left: 1px solid var(--line); }
  .segmented button[aria-pressed="true"] { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
  .roles { display: grid; gap: 4px; }
  .role { display: flex; align-items: center; gap: 8px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
  .count { margin-left: auto; color: var(--muted); font: 12px var(--mono); }
  .timeline { display: grid; grid-template-columns: auto 1fr; gap: 8px; align-items: center; }
  .timeline button {
    font: 600 13px var(--sans); border: 1px solid var(--accent); color: var(--accent); background: transparent;
    border-radius: 6px; padding: 5px 10px; cursor: pointer;
  }
  input[type="range"] { width: 100%; accent-color: var(--accent); }
  .day { font: 500 13px var(--mono); color: var(--muted); }
  .hint { color: var(--muted); font-size: 12px; margin: 0; }
  .stage { position: relative; background: var(--canvas); border: 1px solid var(--line); border-radius: 10px; min-height: 0; overflow: hidden; }
  #sigma { position: absolute; inset: 0; }
  .legend { position: absolute; left: 12px; bottom: 10px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 6px 10px; font-size: 12px; display: flex; flex-wrap: wrap; gap: 4px 12px; max-width: calc(100% - 24px); }
  .legend .item { display: flex; align-items: center; gap: 6px; }
  .swatch { width: 22px; height: 3px; border-radius: 2px; flex: none; position: relative; }
  .swatch::after { content: ""; position: absolute; right: -4px; top: -3px; border: 4.5px solid transparent; border-left: 6px solid; border-left-color: inherit; }
  .legend .arrow { color: var(--muted); }
  .gradient { width: 120px; height: 8px; border-radius: 4px; background: linear-gradient(90deg, #ffe08a, #f58518, #b3001b); }
  .error { position: absolute; inset: 0; display: grid; place-items: center; padding: 24px; text-align: center; color: var(--warn); }
  .details dl { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin: 0; font-variant-numeric: tabular-nums; }
  .details dt { color: var(--muted); }
  .details dd { margin: 0; font-family: var(--mono); text-align: right; }
  .account { font: 600 16px var(--mono); }
  .pill { display: inline-block; border-radius: 999px; padding: 1px 8px; font-size: 12px; font-weight: 600; color: #fff; }
  .neighbors { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
  .neighbors button {
    width: 100%; display: flex; justify-content: space-between; gap: 8px; font: 12px var(--mono);
    background: transparent; color: var(--ink); border: 0; border-radius: 4px; padding: 3px 4px; cursor: pointer; text-align: left;
  }
  .neighbors button:hover { background: var(--accent-soft); }
  .empty { color: var(--muted); }
  @media (max-width: 1100px) {
    .main { grid-template-columns: 240px minmax(0, 1fr); }
    .details { grid-column: 1 / -1; }
  }
  @media (max-width: 720px) {
    html, body { height: auto; }
    .app { height: auto; }
    .main { grid-template-columns: 1fr; }
    .stage { height: 65vh; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="app">
  <header>
    <div>
      <h1>__TITLE__</h1>
      <p class="sub">__SUBTITLE__</p>
    </div>
    <div class="stats" aria-live="polite">
      <div class="stat"><b id="stat-nodes">–</b><span>contas visíveis</span></div>
      <div class="stat"><b id="stat-edges">–</b><span>relações visíveis</span></div>
      <div class="stat"><b id="stat-amount">–</b><span>valor visível</span></div>
      <div class="stat"><b id="stat-day">–</b><span>até o dia</span></div>
    </div>
  </header>

  <div class="main">
    <aside class="panel" aria-label="Controles">
      <div class="field">
        <h2><label for="search">Buscar conta</label></h2>
        <input id="search" type="search" list="accounts" placeholder="ex.: C000333" autocomplete="off">
        <datalist id="accounts"></datalist>
      </div>
      <div class="field">
        <h2>Cor das contas</h2>
        <div class="segmented" role="group" aria-label="Cor das contas">
          <button id="mode-role" type="button" data-mode="role" aria-pressed="true">Papel</button>
          <button id="mode-risk" type="button" data-mode="risk" aria-pressed="false">Risco</button>
          <button id="mode-community" type="button" data-mode="community" aria-pressed="false">Grupo</button>
        </div>
      </div>
      <div class="field">
        <h2>Papéis</h2>
        <div class="roles" id="roles"></div>
      </div>
      <div class="field">
        <h2><label for="day">Linha do tempo</label></h2>
        <div class="timeline">
          <button id="play" type="button">Tocar</button>
          <input id="day" type="range" min="0" max="0" value="0">
        </div>
        <span class="day" id="day-label"></span>
      </div>
      <div class="field">
        <h2><label for="min-amount">Valor mínimo da relação</label></h2>
        <select id="min-amount">
          <option value="0">qualquer valor</option>
          <option value="100">R$ 100 ou mais</option>
          <option value="1000">R$ 1.000 ou mais</option>
          <option value="5000">R$ 5.000 ou mais</option>
        </select>
      </div>
      <div class="field">
        <h2><label for="edge-scale">Espessura das setas</label></h2>
        <input id="edge-scale" type="range" min="0.5" max="3" step="0.25" value="1">
        <h2><label for="normal-alpha">Movimento normal</label></h2>
        <input id="normal-alpha" type="range" min="0" max="0.5" step="0.02" value="0.12" aria-describedby="normal-alpha-hint">
        <span class="hint" id="normal-alpha-hint">à esquerda some; à direita aparece todo o Pix que não é da quadrilha</span>
        <label class="role" for="only-fraud"><input id="only-fraud" type="checkbox"> Só Pix de fraude (rótulo)</label>
      </div>
      <p class="hint">Cada seta vai de quem pagou para quem recebeu. Passe o mouse ou clique numa conta para ver as entradas (azul) e as saídas (laranja). Arraste para mover e use a roda do mouse (ou o gesto de pinça) para dar zoom. Clique no fundo para limpar.</p>
    </aside>

    <section class="stage" aria-label="Rede de transações">
      <div id="sigma"></div>
      <div class="legend" id="legend"></div>
    </section>

    <aside class="panel details" id="details" aria-label="Detalhes da conta" aria-live="polite">
      <div><h2>Conta selecionada</h2><p class="empty">Nenhuma. Clique numa conta ou use a busca.</p></div>
    </aside>
  </div>
</div>

<script src="__GRAPHOLOGY__"></script>
<script src="__SIGMA__"></script>
<script>
(function () {
  const DATA = __DATA__;
  const ROLE_COLORS = { normal: "#9aa7a4", comercio: "#4c78a8", vitima: "#54a24b", laranja: "#f58518", intermediario: "#b279a2", coletor: "#e45756", "?": "#8f9a98" };
  const ROLE_NAMES = { normal: "normal", comercio: "comércio", vitima: "vítima", laranja: "laranja", intermediario: "intermediário", coletor: "coletor", "?": "sem papel" };
  const ROLE_ORDER = ["coletor", "intermediario", "laranja", "vitima", "comercio", "normal", "?"];
  const $ = (id) => document.getElementById(id);
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  // Cores do tema lidas uma vez (e de novo quando o tema muda), não a cada vértice desenhado.
  let theme = {};
  function readTheme() {
    theme = { ink: css("--ink"), surface: css("--surface"), line: css("--line"), fade: css("--fade"), edge: css("--edge"), edgeStrong: css("--edge-strong"), edgeIn: css("--edge-in"), edgeOut: css("--edge-out"), canvas: css("--canvas") };
  }
  readTheme();
  const money = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");
  const nodes = DATA.nodes, E = DATA.edges, nDays = Math.max(DATA.days.length, 1);

  const state = { mode: "role", day: nDays - 1, minAmount: 0, onlyFraud: false, normalAlpha: 0.12, edgeScale: 1, hovered: null, roles: new Set(), selected: null, neighbors: new Set() };
  const FRAUD_ROLES = new Set(["laranja", "intermediario", "coletor"]);
  // Cor das setas do dinheiro da quadrilha, pelo papel de quem pagou (mais saturadas que as dos nós).
  const FLOW_COLORS = { vitima: "#2f9e44", laranja: "#f76707", intermediario: "#ae3ec9", coletor: "#e03131" };
  const FLOW_NAMES = [["vitima", "golpe: vítima → laranja"], ["laranja", "repasse da laranja"],
                      ["intermediario", "repasse do intermediário"], ["coletor", "saída da coletora"]];
  nodes.forEach((n) => state.roles.add(n.r));

  // ---- controles ----
  const roleCounts = {};
  nodes.forEach((n) => { roleCounts[n.r] = (roleCounts[n.r] || 0) + 1; });
  // Papéis fora da lista conhecida (ex.: "suspeita" nos datasets externos) ganham cor e entram nos filtros.
  const EXTRA = ["#d4a017", "#2a9d8f", "#7a5195", "#ef5675", "#3d5a80"];
  Object.keys(roleCounts).filter((r) => !ROLE_ORDER.includes(r)).forEach((r, k) => {
    ROLE_ORDER.splice(ROLE_ORDER.length - 1, 0, r);
    ROLE_COLORS[r] = EXTRA[k % EXTRA.length];
    ROLE_NAMES[r] = r;
  });
  const rolesBox = $("roles");
  ROLE_ORDER.filter((r) => roleCounts[r]).forEach((r) => {
    const id = "role-" + (r === "?" ? "none" : r);
    const row = document.createElement("label");
    row.className = "role";
    row.htmlFor = id;
    row.innerHTML = '<input type="checkbox" checked id="' + id + '"><span class="dot" style="background:' + ROLE_COLORS[r] + '"></span>' + ROLE_NAMES[r] + '<span class="count">' + roleCounts[r].toLocaleString("pt-BR") + "</span>";
    row.querySelector("input").addEventListener("change", (e) => { e.target.checked ? state.roles.add(r) : state.roles.delete(r); update(); });
    rolesBox.appendChild(row);
  });
  const list = $("accounts");
  nodes.forEach((n) => { const o = document.createElement("option"); o.value = n.id; list.appendChild(o); });
  const idIndex = new Map(nodes.map((n, i) => [n.id, i]));

  if (!DATA.hasRisk) { $("mode-risk").disabled = true; $("mode-risk").title = "Nenhum escore de risco foi fornecido"; }
  if (!DATA.hasFraudEdges) { $("only-fraud").disabled = true; }
  document.querySelectorAll(".segmented button").forEach((b) => b.addEventListener("click", () => {
    state.mode = b.dataset.mode;
    document.querySelectorAll(".segmented button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    update();
  }));
  const slider = $("day");
  slider.max = String(nDays - 1);
  slider.value = String(state.day);
  slider.addEventListener("input", () => { state.day = +slider.value; update(); });
  $("min-amount").addEventListener("change", (e) => { state.minAmount = +e.target.value; update(); });
  $("only-fraud").addEventListener("change", (e) => { state.onlyFraud = e.target.checked; update(); });
  $("normal-alpha").addEventListener("input", (e) => { state.normalAlpha = +e.target.value; update(); });
  $("edge-scale").addEventListener("input", (e) => { state.edgeScale = +e.target.value; update(); });
  let timer = null;
  $("play").addEventListener("click", () => {
    if (timer) { stop(); return; }
    if (state.day >= nDays - 1) { state.day = 0; }
    $("play").textContent = "Pausar";
    timer = setInterval(() => {
      state.day += 1; slider.value = String(state.day); update();
      if (state.day >= nDays - 1) stop();
    }, 700);
  });
  function stop() { clearInterval(timer); timer = null; $("play").textContent = "Tocar"; }

  // ---- cores ----
  function lerp(a, b, t) { return Math.round(a + (b - a) * t); }
  function hex(h) { return [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)); }
  const RISK = ["#ffe08a", "#f58518", "#b3001b"].map(hex);
  function riskColor(k) {
    if (k === null || k === undefined) return "#8f9a98";
    const [a, b, t] = k < 0.5 ? [RISK[0], RISK[1], k / 0.5] : [RISK[1], RISK[2], (k - 0.5) / 0.5];
    return "rgb(" + lerp(a[0], b[0], t) + "," + lerp(a[1], b[1], t) + "," + lerp(a[2], b[2], t) + ")";
  }
  function groupColor(c) {
    // matiz pelo ângulo áureo (grupos vizinhos na numeração ficam com cores distantes); sigma só entende rgb/hex
    const h = ((c * 137.508) % 360) / 60, s = 0.58, l = 0.52;
    const chroma = (1 - Math.abs(2 * l - 1)) * s, x = chroma * (1 - Math.abs((h % 2) - 1)), m = l - chroma / 2;
    const [r, g, b] = h < 1 ? [chroma, x, 0] : h < 2 ? [x, chroma, 0] : h < 3 ? [0, chroma, x] : h < 4 ? [0, x, chroma] : h < 5 ? [x, 0, chroma] : [chroma, 0, x];
    return "rgb(" + Math.round((r + m) * 255) + "," + Math.round((g + m) * 255) + "," + Math.round((b + m) * 255) + ")";
  }
  function withAlpha(color, alpha) {
    const [r, g, b] = color.startsWith("#") ? hex(color) : color.match(/\d+/g).map(Number);
    return "rgba(" + r + "," + g + "," + b + "," + alpha + ")";
  }
  // Papel de quem pagou, quando a seta é dinheiro da quadrilha; null no movimento normal.
  function flowRole(j) {
    const payer = nodes[E.s[j]];
    if (FRAUD_ROLES.has(payer.r)) return payer.r;
    return E.f[j] && payer.r === "vitima" ? "vitima" : null;
  }
  // Mistura opaca de duas cores (o sigma 2 desenha nós translúcidos com cores erradas).
  function mix(color, other, t) {
    const rgb = (c) => c.startsWith("#") ? hex(c) : c.match(/\d+/g).map(Number);
    const [a, b] = [rgb(color), rgb(other)];
    return "rgb(" + lerp(a[0], b[0], t) + "," + lerp(a[1], b[1], t) + "," + lerp(a[2], b[2], t) + ")";
  }
  function nodeColor(n) {
    if (state.mode === "risk") return riskColor(n.k);
    if (state.mode === "community") return groupColor(n.c);
    return ROLE_COLORS[n.r] || ROLE_COLORS["?"];
  }

  function arrowItem(color, text) {
    return '<span class="item"><span class="swatch" style="background:' + color + ";border-left-color:" + color + '"></span>' + text + "</span>";
  }
  function legend() {
    const box = $("legend");
    if (state.selected !== null) {
      box.innerHTML = arrowItem(theme.edgeIn, "entrada: pagou a esta conta") + arrowItem(theme.edgeOut, "saída: esta conta pagou");
      return;
    }
    const direction = '<span class="item arrow">seta: quem paga → quem recebe; mais grossa = mais dinheiro</span>';
    if (state.mode === "risk") {
      box.innerHTML = '<span class="item">menos suspeita <span class="gradient"></span> mais suspeita</span>' + direction;
    } else if (state.mode === "community") {
      box.innerHTML = '<span class="item">' + DATA.communities + " grupos detectados pelo algoritmo de Louvain; cada cor é um grupo</span>" + direction;
    } else {
      box.innerHTML = ROLE_ORDER.filter((r) => roleCounts[r]).map((r) =>
        '<span class="item"><span class="dot" style="background:' + ROLE_COLORS[r] + '"></span>' + ROLE_NAMES[r] + "</span>").join("") +
        FLOW_NAMES.filter(([r]) => roleCounts[r]).map(([r, text]) => arrowItem(FLOW_COLORS[r], text)).join("") + direction;
    }
  }

  // ---- visibilidade ----
  function nodeVisible(i) { const n = nodes[i]; return state.roles.has(n.r) && n.d <= state.day; }
  function edgeVisible(j) {
    if (E.d[j] > state.day || E.a[j] < state.minAmount) return false;
    if (state.onlyFraud && !E.f[j]) return false;
    return nodeVisible(E.s[j]) && nodeVisible(E.t[j]);
  }

  // ---- grafo e renderização ----
  if (!window.graphology || !window.Sigma) {
    $("sigma").innerHTML = '<div class="error">Não foi possível carregar as bibliotecas de visualização. Verifique a conexão com a internet e recarregue a página.</div>';
    return;
  }
  const graph = new graphology.Graph({ type: "directed", multi: false, allowSelfLoops: false });
  nodes.forEach((n, i) => graph.addNode(String(i), { x: n.x, y: -n.y, size: n.s, label: n.id }));
  for (let j = 0; j < E.s.length; j++) {
    graph.addEdgeWithKey("e" + j, String(E.s[j]), String(E.t[j]), { size: Math.min(4.5, 1 + Math.log10(1 + E.a[j]) / 2), j: j });
  }

  let renderer;
  try {
    renderer = new Sigma(graph, $("sigma"), {
      defaultEdgeType: "arrow",
      labelRenderedSizeThreshold: 9,
      labelFont: "IBM Plex Mono, monospace",
      labelSize: 11,
      labelColor: { color: theme.ink },
      zIndex: true,
      // Rótulo da conta sob o mouse com as cores do tema (o padrão do sigma é uma caixa branca).
      hoverRenderer: (context, data, settings) => {
        const size = settings.labelSize, label = data.label || "";
        context.font = "600 " + size + "px " + settings.labelFont;
        const w = context.measureText(label).width + 12, h = size + 10;
        const x = data.x + data.size + 4, y = data.y - h / 2;
        context.fillStyle = theme.surface;
        context.strokeStyle = theme.line;
        context.lineWidth = 1;
        context.beginPath();
        context.rect(x, y, w, h);
        context.fill();
        context.stroke();
        context.fillStyle = theme.ink;
        context.fillText(label, x + 6, data.y + size / 3);
      },
      minCameraRatio: 0.02,
      maxCameraRatio: 3,
      nodeReducer: (key, attrs) => {
        const i = +key;
        const n = nodes[i];
        const out = Object.assign({}, attrs);
        if (!nodeVisible(i)) { out.hidden = true; return out; }
        out.color = nodeColor(n);
        if (state.selected !== null) {
          if (i === state.selected) { out.forceLabel = true; out.zIndex = 2; out.size = attrs.size * 1.6; }
          else if (state.neighbors.has(i)) { out.zIndex = 1; out.forceLabel = true; }
          else { out.color = theme.fade; out.label = ""; out.zIndex = 0; }
        } else if (FRAUD_ROLES.has(n.r)) {
          out.zIndex = 1;
          if (state.mode === "role") out.size = attrs.size * 1.8 + 2;  // poucas e decisivas: maiores
        } else if (state.mode === "role" && n.r !== "vitima") {
          // com o movimento normal apagado, as contas normais também recuam para o fundo
          out.color = mix(out.color, theme.canvas, Math.max(0, 0.6 - 2 * state.normalAlpha));
        }
        return out;
      },
      edgeReducer: (key, attrs) => {
        const j = attrs.j;
        const out = Object.assign({}, attrs);
        if (!edgeVisible(j)) { out.hidden = true; return out; }
        out.size = attrs.size * state.edgeScale;
        // clicar tem prioridade; sem clique, a conta sob o mouse ganha o mesmo destaque
        const focus = state.selected !== null ? state.selected : state.hovered;
        if (focus !== null) {
          // entradas e saídas em cores diferentes: o sentido do dinheiro fica evidente
          const incoming = E.t[j] === focus, outgoing = E.s[j] === focus;
          if (incoming || outgoing) {
            out.color = incoming ? theme.edgeIn : theme.edgeOut;
            out.size += 1.2 * state.edgeScale;
            out.zIndex = 2;
            return out;
          }
          if (state.selected !== null) { out.hidden = true; return out; }
          out.color = withAlpha(theme.edge, 0.06);  // passando o mouse: o resto recua, mas não some
          out.zIndex = 0;
          return out;
        }
        const role = flowRole(j);
        if (role && (state.mode === "role" || state.onlyFraud)) {
          // o dinheiro da quadrilha leva a cor de quem pagou: a vítima (golpe), a laranja, o intermediário...
          out.color = withAlpha(FLOW_COLORS[role], 0.9);
          out.size = Math.max(out.size + 0.8 * state.edgeScale, 2 * state.edgeScale);
          out.zIndex = 1;
        } else if (state.onlyFraud) {
          out.color = theme.edgeStrong;
        } else if (state.normalAlpha <= 0) {
          out.hidden = true;
        } else {
          out.color = withAlpha(theme.edge, state.normalAlpha);
          out.zIndex = 0;
        }
        return out;
      },
    });
  } catch (err) {
    $("sigma").innerHTML = '<div class="error">O navegador não conseguiu iniciar o WebGL, necessário para desenhar a rede.</div>';
    return;
  }

  function select(i, focus) {
    state.selected = i;
    state.neighbors = new Set();
    if (i !== null) {
      graph.forEachNeighbor(String(i), (k) => state.neighbors.add(+k));
      if (focus) {
        const d = renderer.getNodeDisplayData(String(i));
        if (d) renderer.getCamera().animate({ x: d.x, y: d.y, ratio: 0.7 }, { duration: 500 });
      }
    }
    details();
    update();
  }
  renderer.on("clickNode", ({ node }) => select(+node, false));
  renderer.on("enterNode", ({ node }) => { state.hovered = +node; renderer.refresh(); });
  renderer.on("leaveNode", () => { state.hovered = null; renderer.refresh(); });
  renderer.on("clickStage", () => select(null, false));
  $("search").addEventListener("change", (e) => {
    const i = idIndex.get(e.target.value.trim());
    if (i === undefined) return;
    const role = nodes[i].r;
    if (!state.roles.has(role)) {  // a conta buscada estava escondida pelo filtro de papel
      state.roles.add(role);
      const box = $("role-" + (role === "?" ? "none" : role));
      if (box) box.checked = true;
    }
    if (nodes[i].d > state.day) { state.day = nDays - 1; slider.value = String(state.day); }
    select(i, true);
  });

  function details() {
    const box = $("details");
    if (state.selected === null) {
      box.innerHTML = '<div><h2>Conta selecionada</h2><p class="empty">Nenhuma. Clique numa conta ou use a busca.</p></div>';
      return;
    }
    const i = state.selected, n = nodes[i];
    const incoming = [], outgoing = [];
    for (let j = 0; j < E.s.length; j++) {
      if (E.t[j] === i) incoming.push(j);
      if (E.s[j] === i) outgoing.push(j);
    }
    const top = (ids, other) => ids.sort((a, b) => E.a[b] - E.a[a]).slice(0, 8).map((j) => {
      const k = other(j);
      return '<li><button type="button" data-node="' + k + '"><span><span class="dot" style="display:inline-block;background:' + (ROLE_COLORS[nodes[k].r] || "#999") + '"></span> ' + nodes[k].id + "</span><span>" + money(E.a[j]) + "</span></button></li>";
    }).join("") || '<li class="empty">nenhum</li>';
    const color = ROLE_COLORS[n.r] || ROLE_COLORS["?"];
    box.innerHTML =
      '<div><h2>Conta selecionada</h2><div class="account">' + n.id + '</div>' +
      '<span class="pill" style="background:' + color + '">' + (ROLE_NAMES[n.r] || n.r) + "</span></div>" +
      "<dl>" +
      "<dt>recebeu de</dt><dd>" + n.i + " contas</dd>" +
      "<dt>pagou a</dt><dd>" + n.o + " contas</dd>" +
      "<dt>recebeu</dt><dd>" + money(n.ai) + "</dd>" +
      "<dt>enviou</dt><dd>" + money(n.ao) + "</dd>" +
      (n.k !== null ? "<dt>percentil de risco</dt><dd>" + (n.k * 100).toFixed(0) + "%</dd>" : "") +
      "<dt>grupo (Louvain)</dt><dd>" + n.c + "</dd>" +
      (DATA.days.length ? "<dt>primeiro Pix</dt><dd>" + DATA.days[n.d] + "</dd>" : "") +
      "</dl>" +
      '<div><h2>Maiores pagadores</h2><ul class="neighbors">' + top(incoming, (j) => E.s[j]) + "</ul></div>" +
      '<div><h2>Maiores recebedores</h2><ul class="neighbors">' + top(outgoing, (j) => E.t[j]) + "</ul></div>";
    box.querySelectorAll("button[data-node]").forEach((b) => b.addEventListener("click", () => select(+b.dataset.node, true)));
  }

  function stats() {
    let nv = 0, ev = 0, amount = 0;
    for (let i = 0; i < nodes.length; i++) if (nodeVisible(i)) nv++;
    for (let j = 0; j < E.s.length; j++) if (edgeVisible(j)) { ev++; amount += E.a[j]; }
    $("stat-nodes").textContent = nv.toLocaleString("pt-BR");
    $("stat-edges").textContent = ev.toLocaleString("pt-BR");
    $("stat-amount").textContent = money(amount);
    $("stat-day").textContent = DATA.days.length ? DATA.days[state.day] : "–";
    $("day-label").textContent = DATA.days.length ? "dia " + (state.day + 1) + " de " + nDays + " (" + DATA.days[state.day] + ")" : "sem datas";
  }

  function update() { legend(); stats(); renderer.refresh(); }

  function retheme() { readTheme(); renderer.setSetting("labelColor", { color: theme.ink }); renderer.refresh(); }
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", retheme);

  update();
})();
</script>
"""
