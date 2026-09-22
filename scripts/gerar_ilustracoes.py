"""Gera as ilustrações do README: os padrões de fraude e a animação de uma quadrilha.

São figuras explicativas (não resultados): saem do gerador sintético e dos padrões de
``pixfraud.patterns``, com a mesma semente, então podem ser refeitas a qualquer momento.

Uso:
    python scripts/gerar_ilustracoes.py
    python scripts/gerar_ilustracoes.py --saida reports/figures

Saídas em reports/figures/:
    padroes_de_fraude.png   os seis padrões lado a lado
    quadrilha.gif           o dinheiro percorrendo uma quadrilha, hora a hora
    rede_exemplo.png        um recorte da rede sintética, colorido pelo papel de cada conta
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from pixfraud.graph import build_graph  # noqa: E402
from pixfraud.patterns import PATTERNS  # noqa: E402
from pixfraud.simulation import SimulationConfig, generate_dataset  # noqa: E402
from pixfraud.visualization import ROLE_COLORS, SURFACE, draw_graph  # noqa: E402

TITULOS = {
    "fan_in": "fan-in: várias vítimas, uma laranja",
    "fan_out": "fan-out: a laranja pulveriza",
    "chain": "cadeia: o dinheiro passa de conta em conta",
    "cycle": "ciclo: o dinheiro volta à origem",
    "scatter_gather": "espalha e junta",
    "mule_ring": "quadrilha completa",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera as ilustrações do README.")
    parser.add_argument("--saida", default="reports/figures")
    args = parser.parse_args()
    figuras = Path(args.saida)
    figuras.mkdir(parents=True, exist_ok=True)

    _padroes(figuras / "padroes_de_fraude.png")
    _rede_exemplo(figuras / "rede_exemplo.png")
    _animacao(figuras / "quadrilha.gif")


def _legenda(papeis) -> list:
    """Itens de legenda só dos papéis que aparecem no desenho, na ordem de ROLE_COLORS."""
    return [plt.Line2D([], [], marker="o", linestyle="", markersize=9, color=cor, label=nome)
            for nome, cor in ROLE_COLORS.items() if nome in papeis]


def _padroes(path: Path) -> None:
    """Os seis padrões de fraude de ``pixfraud.patterns``, lado a lado."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    papeis = set()
    for ax, (nome, criar) in zip(axes.flat, PATTERNS.items()):
        padrao = criar()
        draw_graph(padrao, layout="auto", edge_labels=None, node_labels=False, ax=ax, title=TITULOS[nome])
        papeis |= {dados.get("role") for _, dados in padrao.nodes(data=True)}
        if ax.get_legend():  # uma legenda por painel seria repetição; a da figura basta
            ax.get_legend().remove()
        ax.set_axis_off()
    fig.legend(handles=_legenda(papeis), loc="lower center", ncols=len(papeis), frameon=False, fontsize=10)
    fig.suptitle("Padrões de fraude que o gerador injeta na rede (pixfraud.patterns)", fontsize=13)
    fig.savefig(path, dpi=130, facecolor=SURFACE)
    plt.close(fig)
    print(f"{path} ({path.stat().st_size // 1024} KB)")


def _dataset_pequeno():
    """Dataset com uma única quadrilha, pequeno o bastante para desenhar."""
    cfg = SimulationConfig(n_people=120, n_merchants=6, n_days=3, n_rings=1, mules_per_ring=2,
                           victims_per_ring=5, chain_length=2, p_chain=1.0, seed=7)
    return generate_dataset(cfg)


def _rede_exemplo(path: Path) -> None:
    """A quadrilha dentro do movimento normal: é isso que o detector precisa achar."""
    accounts, tx = _dataset_pequeno()
    info = accounts.set_index("account_id")
    papel = info["role"].where(~info["is_victim"], "vitima")
    grafo = build_graph(tx, accounts["account_id"])
    quadrilha = [c for c in papel.index if papel[c] in ("laranja", "intermediario", "coletor") and c in grafo]

    # a quadrilha, quem pagou a ela e os vizinhos imediatos dessas contas
    vizinhas = set(quadrilha)
    for conta in quadrilha:
        vizinhas |= set(grafo.predecessors(conta)) | set(grafo.successors(conta))
    for conta in list(vizinhas):
        vizinhas |= set(list(grafo.predecessors(conta))[:2]) | set(list(grafo.successors(conta))[:2])
    recorte = grafo.subgraph(vizinhas).copy()
    nx.set_node_attributes(recorte, papel.to_dict(), "role")

    fig, ax = plt.subplots(figsize=(10, 6.5), layout="constrained")
    draw_graph(recorte, color_by="role", layout="kamada_kawai", edge_labels=None, node_labels=False, ax=ax,
               title=f"Uma quadrilha dentro do movimento normal ({recorte.number_of_nodes()} contas em volta)")
    if ax.get_legend():
        ax.get_legend().remove()
    fig.legend(handles=_legenda(set(papel[list(recorte)])), loc="lower center",
               ncols=6, frameon=False, fontsize=10)
    ax.set_axis_off()
    fig.savefig(path, dpi=130, facecolor=SURFACE)
    plt.close(fig)
    print(f"{path} ({path.stat().st_size // 1024} KB)")


def _animacao(path: Path, intervalo_h: int = 2) -> None:
    """O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora."""
    accounts, tx = _dataset_pequeno()
    papel = accounts.set_index("account_id")["role"].where(~accounts.set_index("account_id")["is_victim"], "vitima")
    fraude = tx[tx["is_fraud"]].sort_values("timestamp").reset_index(drop=True)
    contas = sorted(set(fraude["sender"]) | set(fraude["receiver"]))
    grafo = build_graph(fraude, contas)
    posicao = nx.kamada_kawai_layout(nx.Graph(grafo))
    cores = [ROLE_COLORS.get(papel.get(v, "normal"), "#b0b0b0") for v in grafo]

    inicio, fim = fraude["timestamp"].min().floor("h"), fraude["timestamp"].max().ceil("h")
    instantes = pd.date_range(inicio, fim, freq=f"{intervalo_h}h")
    fig, ax = plt.subplots(figsize=(7.5, 5), layout="constrained")

    def quadro(i: int) -> None:
        agora = instantes[i]
        ate_agora = fraude[fraude["timestamp"] <= agora]
        ax.clear()
        ax.set_axis_off()
        nx.draw_networkx_nodes(grafo, posicao, ax=ax, node_color=cores, node_size=220,
                               edgecolors="#333333", linewidths=0.6)
        if len(ate_agora):
            arestas = build_graph(ate_agora, contas)
            recentes = ate_agora["timestamp"] > agora - pd.Timedelta(hours=intervalo_h)
            novas = set(map(tuple, ate_agora.loc[recentes, ["sender", "receiver"]].to_numpy()))
            nx.draw_networkx_edges(grafo, posicao, ax=ax, edgelist=list(arestas.edges), edge_color="#bbbbbb",
                                   width=1.0, arrows=True, arrowsize=9, node_size=220)
            if novas:
                nx.draw_networkx_edges(grafo, posicao, ax=ax, edgelist=list(novas), edge_color="#e45756",
                                       width=2.4, arrows=True, arrowsize=13, node_size=220)
        total = ate_agora.loc[ate_agora["scenario"].isin(["falso_suporte", "clonagem_whatsapp"]), "amount"].sum()
        ax.set_title(f"{agora:%d/%m %Hh} · R$ {total:,.0f} roubados das vítimas".replace(",", "."),
                     fontsize=11, loc="left")
        ax.margins(0.12)

    papeis = set(papel[list(grafo)])
    fig.legend(handles=_legenda(papeis), loc="lower center", ncols=len(papeis), frameon=False, fontsize=9)
    animacao = FuncAnimation(fig, quadro, frames=len(instantes), interval=420)
    animacao.save(path, writer=PillowWriter(fps=2.4), dpi=90, savefig_kwargs={"facecolor": SURFACE})
    plt.close(fig)
    print(f"{path} ({path.stat().st_size // 1024} KB, {len(instantes)} quadros)")


if __name__ == "__main__":
    main()
