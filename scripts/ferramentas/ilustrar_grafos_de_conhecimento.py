"""Desenha os dois grafos de conhecimento do repositório para o README.

São figuras explicativas (não resultados da pesquisa):

- o grafo de notas do Obsidian (docs/grafo-de-notas.json), com as mesmas cores da aba
  Grafo do Obsidian (lidas de .obsidian/graph.json);
- o mapa do código do Graphify (graphify-out/graph.json), resumido por arquivo: cada nó é
  um arquivo .py e cada aresta junta as chamadas e imports de um arquivo para outro.

Rode antes `python scripts/ferramentas/exportar_grafo_de_notas.py` e `graphify update .` para que os
dois JSON estejam atualizados (ver docs/obsidian.md).

Uso:
    python scripts/ferramentas/ilustrar_grafos_de_conhecimento.py
    python scripts/ferramentas/ilustrar_grafos_de_conhecimento.py --saida reports/ilustracoes

Saídas:
    grafo_de_notas.png    notas e links, coloridos pelo tipo de nota
    grafo_do_codigo.png   arquivos .py e as dependências entre eles
"""

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

from pixfraud.visualization import INK, INK_SECONDARY, SURFACE  # noqa: E402

ROOT = Path(__file__).parents[2]
SEM_GRUPO = "#c8c7c2"
PASTAS_DO_CODIGO = {"src/pixfraud": "#2a78d6", "scripts": "#eb6834", "app": "#1baf7a", "tests": "#8a8a8a"}


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Desenha o grafo de notas e o mapa do código para o README.")
    parser.add_argument("--saida", type=Path, default=ROOT / "reports" / "ilustracoes")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    _grafo_de_notas(args.saida / "grafo_de_notas.png")
    _grafo_do_codigo(args.saida / "grafo_do_codigo.png")


def _grupos_do_obsidian() -> list[tuple[str, list[str], str]]:
    """Os grupos de cor de .obsidian/graph.json como (nome, condições, cor em hex)."""
    config = json.loads((ROOT / ".obsidian" / "graph.json").read_text(encoding="utf-8"))
    return [(g["query"], g["query"].split(" OR "), f"#{g['color']['rgb']:06x}") for g in config["colorGroups"]]


def _rotulo(consulta: str) -> str:
    """"tag:diario OR tag:ata" -> "diario / ata", para a legenda."""
    return consulta.replace("tag:", "").replace("path:", "").replace(" OR ", " / ")


def _cor_da_nota(no: dict, grupos) -> str:
    """Primeiro grupo que casa com a nota, como no Obsidian ("tag:x" ou "path:pasta")."""
    for _, condicoes, cor in grupos:
        for condicao in condicoes:
            tipo, valor = condicao.split(":", 1)
            if (tipo == "tag" and valor in no["tags"]) or (tipo == "path" and no["caminho"].startswith(valor)):
                return cor
    return SEM_GRUPO


def _grafo_de_notas(destino: Path) -> None:
    """Desenha o grafo de notas do Obsidian, com as cores dos grupos do cofre."""
    dados = json.loads((ROOT / "docs" / "grafo-de-notas.json").read_text(encoding="utf-8"))
    grafo = nx.Graph()
    grafo.add_nodes_from(n["caminho"] for n in dados["nos"])
    grafo.add_edges_from((a["de"], a["para"]) for a in dados["arestas"] if a["tipo"] == "nota")
    grupos = _grupos_do_obsidian()
    cores = {n["caminho"]: _cor_da_nota(n, grupos) for n in dados["nos"]}
    grau = dict(grafo.degree())
    pos = nx.spring_layout(grafo, seed=7, k=0.35, iterations=200)

    fig, ax = plt.subplots(figsize=(11, 8), facecolor=SURFACE)
    nx.draw_networkx_edges(grafo, pos, ax=ax, edge_color=INK_SECONDARY, alpha=0.18, width=0.6)
    nx.draw_networkx_nodes(grafo, pos, ax=ax, node_color=[cores[n] for n in grafo],
                           node_size=[25 + 12 * grau[n] for n in grafo], edgecolors=SURFACE, linewidths=0.8)
    principais = sorted(grafo, key=grau.get, reverse=True)[:8]
    nx.draw_networkx_labels(grafo, pos, ax=ax, labels={n: Path(n).stem for n in principais},
                            font_size=8, font_color=INK, verticalalignment="bottom")
    usados = Counter(cores.values())
    legenda = [plt.Line2D([], [], marker="o", linestyle="", markersize=8, color=cor, label=_rotulo(nome))
               for nome, _, cor in grupos if usados[cor]]
    ax.legend(handles=legenda, loc="lower left", fontsize=8, frameon=False, ncol=2)
    ax.set_title(f"Grafo de notas do Obsidian: {grafo.number_of_nodes()} notas, "
                 f"{grafo.number_of_edges()} ligações", color=INK, fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _pasta(arquivo: str) -> str | None:
    """A pasta de código de um arquivo .py (ou ``None`` fora delas)."""
    if not arquivo.endswith(".py"):
        return None
    return next((p for p in PASTAS_DO_CODIGO if arquivo.startswith(p + "/")), None)


def _grafo_do_codigo(destino: Path) -> None:
    """Desenha o mapa do código: arquivos e as ligações entre pastas, pelo Graphify."""
    dados = json.loads((ROOT / "graphify-out" / "graph.json").read_text(encoding="utf-8"))
    arquivo_do_no = {n["id"]: n.get("source_file") or "" for n in dados["nodes"]}
    pesos = Counter()
    for aresta in dados["links"]:
        de, para = arquivo_do_no.get(aresta["source"], ""), arquivo_do_no.get(aresta["target"], "")
        if de != para and _pasta(de) and _pasta(para) and _pasta(de) != "tests":
            pesos[de, para] += 1
    grafo = nx.DiGraph()
    grafo.add_weighted_edges_from((de, para, peso) for (de, para), peso in pesos.items())
    grau = dict(grafo.degree(weight="weight"))
    pos = nx.kamada_kawai_layout(grafo.to_undirected())

    fig, ax = plt.subplots(figsize=(11, 8), facecolor=SURFACE)
    nx.draw_networkx_edges(grafo, pos, ax=ax, edge_color=INK_SECONDARY, alpha=0.3, arrowsize=8,
                           width=[0.4 + 0.25 * d["weight"] for *_, d in grafo.edges(data=True)],
                           connectionstyle="arc3,rad=0.08", node_size=300)
    nx.draw_networkx_nodes(grafo, pos, ax=ax, node_color=[PASTAS_DO_CODIGO[_pasta(n)] for n in grafo],
                           node_size=[60 + 10 * grau[n] for n in grafo], edgecolors=SURFACE, linewidths=0.8)
    nx.draw_networkx_labels(grafo, pos, ax=ax, labels={n: Path(n).stem for n in grafo if _pasta(n) != "tests"},
                            font_size=7, font_color=INK, verticalalignment="bottom")
    legenda = [plt.Line2D([], [], marker="o", linestyle="", markersize=8, color=cor, label=pasta)
               for pasta, cor in PASTAS_DO_CODIGO.items() if pasta != "tests"]
    ax.legend(handles=legenda, loc="lower left", fontsize=8, frameon=False)
    ax.set_title(f"Mapa do código (Graphify): {grafo.number_of_nodes()} arquivos, "
                 f"{sum(pesos.values())} chamadas e imports entre eles", color=INK, fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(destino, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
