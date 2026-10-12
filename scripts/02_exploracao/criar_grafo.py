"""Cria, resume e salva grafos sem precisar escrever código.

O formato de saída vem da extensão: .png/.svg/.pdf (imagem), .html (interativo,
abre no navegador) ou .gexf/.graphml (para o Gephi).

Exemplos:
    # padrões de fraude prontos (fan_in, fan_out, chain, cycle, scatter_gather, mule_ring)
    python scripts/02_exploracao/criar_grafo.py padrao mule_ring --saida reports/estudos/anel.png
    python scripts/02_exploracao/criar_grafo.py padrao chain --tamanho 6 --saida reports/estudos/cadeia.html

    # qualquer CSV de transações (colunas de origem, destino e, opcionalmente, valor)
    python scripts/02_exploracao/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --contas estudos/dados/exemplo_contas.csv --saida reports/estudos/exemplo.png

    # o caminho do dinheiro em volta de uma conta do dataset sintético
    python scripts/02_exploracao/criar_grafo.py csv data/synthetic/transactions.csv --conta C000167 --saltos 2 --direcao tras --saida reports/estudos/trilha.html

    # só os Pix em ordem cronológica, com no máximo 2h de espera em cada conta
    python scripts/02_exploracao/criar_grafo.py csv data/synthetic/transactions.csv --conta C000167 --temporal --espera 2h --saltos 4 --saida trilha_temporal.png

    # cores pelos grupos (comunidades de Louvain) em vez dos papéis
    python scripts/02_exploracao/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --cor grupo --saida grupos.png

    # fluxo máximo e o que bloquear entre contas de origem e um destino
    python scripts/02_exploracao/criar_grafo.py fluxo estudos/dados/exemplo_transacoes.csv --de carla fabio --para conta_z --saida fluxo.png
"""  # noqa: E501 (exemplos de comando ficam numa linha só, para copiar e colar)

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud.communities import detect_communities  # noqa: E402
from pixfraud.flow import blocking_accounts, blocking_cut, max_money_flow, relevant_accounts  # noqa: E402
from pixfraud.graph import describe, graph_from_csv, money_trail  # noqa: E402
from pixfraud.patterns import PATTERNS  # noqa: E402
from pixfraud.temporal import temporal_trail  # noqa: E402
from pixfraud.visualization import save_graph  # noqa: E402

DIRECTIONS = {"frente": "forward", "tras": "backward", "ambos": "both"}
MAX_NODES_IMAGE = 300


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Cria, resume e salva grafos de transações.")
    sub = parser.add_subparsers(dest="fonte", required=True)

    padrao = sub.add_parser("padrao", help="gera um padrão de fraude pronto")
    padrao.add_argument("nome", choices=sorted(PATTERNS))
    padrao.add_argument("--tamanho", type=int, help="nº de vítimas, contas na cadeia etc. (depende do padrão)")

    csv = sub.add_parser("csv", help="monta o grafo a partir de um CSV de transações")
    csv.add_argument("arquivo")
    csv.add_argument("--origem", default="sender", help="coluna da conta pagadora")
    csv.add_argument("--destino", default="receiver", help="coluna da conta recebedora")
    csv.add_argument("--valor", default="amount", help="coluna do valor (opcional)")
    csv.add_argument("--contas", help="CSV com account_id e role, para colorir por papel "
                     "(padrão: accounts.csv na mesma pasta, se existir)")
    csv.add_argument("--conta", help="recorta o grafo em volta desta conta")
    csv.add_argument("--saltos", type=int, default=2, help="alcance do recorte (padrão: 2)")
    csv.add_argument("--direcao", choices=sorted(DIRECTIONS), default="ambos",
                     help="frente = para onde o dinheiro foi; tras = de onde veio")
    csv.add_argument("--temporal", action="store_true",
                     help="com --conta: só segue Pix em ordem cronológica (precisa da coluna timestamp)")
    csv.add_argument("--espera", help="com --temporal: tempo máximo parado em cada conta, ex.: 30min, 2h, 1D")
    csv.add_argument("--cor", choices=["papel", "grupo"], default="papel",
                     help="papel (padrão) ou grupo = comunidades de Louvain")

    fluxo = sub.add_parser("fluxo", help="fluxo máximo, corte mínimo e contas a bloquear")
    fluxo.add_argument("arquivo")
    fluxo.add_argument("--de", nargs="+", required=True, help="conta(s) de origem")
    fluxo.add_argument("--para", required=True, help="conta de destino")
    fluxo.add_argument("--contas", help="CSV com account_id e role, para colorir por papel")

    for p in (padrao, csv, fluxo):
        p.add_argument("--saida", help="arquivo de saída (.png, .svg, .pdf, .html, .gexf, .graphml)")
    args = parser.parse_args()
    color_by = "role"

    if args.fonte == "padrao":
        make = PATTERNS[args.nome]
        graph = make(args.tamanho) if args.tamanho else make()
        title = f"Padrão: {args.nome}"
    elif args.fonte == "fluxo":
        graph = graph_from_csv(args.arquivo)
        _attach_roles(graph, args.contas, Path(args.arquivo))
        missing = [a for a in [*args.de, args.para] if a not in graph]
        if missing:
            parser.error(f"contas que não aparecem no arquivo: {', '.join(missing)}")
        value, _ = max_money_flow(graph, args.de, args.para)
        cut_value, cut = blocking_cut(graph, args.de, args.para)
        to_block = blocking_accounts(graph, args.de, args.para)
        print(f"fluxo máximo: R$ {value:,.2f} | corte mínimo: R$ {cut_value:,.2f}")
        print("Pix do corte mínimo:", ", ".join(f"{u} -> {v} (R$ {a:,.2f})" for u, v, a in cut) or "nenhum")
        blocked = "impossível (pagamento direto)" if to_block is None else (", ".join(to_block) or "nenhuma")
        print("contas a bloquear:", blocked)
        graph = graph.subgraph(relevant_accounts(graph, args.de, args.para) or set(args.de)).copy()
        title = f"Fluxo de {', '.join(args.de)} até {args.para}: R$ {value:,.0f}".replace(",", ".")
        print()
    else:
        graph = graph_from_csv(args.arquivo, source=args.origem, target=args.destino, amount=args.valor)
        _attach_roles(graph, args.contas, Path(args.arquivo))
        if args.cor == "grupo":
            groups = detect_communities(graph)
            nx.set_node_attributes(graph, {v: f"grupo {c}" for v, c in groups.items()}, "grupo")
            color_by = "grupo"
        title = Path(args.arquivo).name
        if args.conta:
            if args.conta not in graph:
                parser.error(f"a conta {args.conta} não aparece no arquivo")
            if args.temporal:
                tx = pd.read_csv(args.arquivo, parse_dates=["timestamp"]).rename(
                    columns={args.origem: "sender", args.destino: "receiver", args.valor: "amount"})
                direction = "backward" if args.direcao == "tras" else "forward"
                trail = temporal_trail(tx, args.conta, direction=direction, max_hops=args.saltos, max_delay=args.espera)
                trail.add_node(args.conta)
                if trail.edges:
                    graph = graph.subgraph(trail.nodes).edge_subgraph(trail.edges).copy()
                else:
                    graph = graph.subgraph([args.conta]).copy()
                title = f"{args.conta}: trilha temporal ({'para trás' if direction == 'backward' else 'para frente'})"
            else:
                graph = money_trail(graph, args.conta, args.saltos, DIRECTIONS[args.direcao])
                title = f"{args.conta}: {args.saltos} saltos ({args.direcao})"

    print(describe(graph).to_string())
    if args.saida:
        suffix = Path(args.saida).suffix.lower()
        if suffix in (".png", ".svg", ".pdf") and graph.number_of_nodes() > MAX_NODES_IMAGE:
            parser.error(
                f"o grafo tem {graph.number_of_nodes()} vértices: grande demais para uma imagem legível. "
                "Use --conta para recortar, ou salve em .html/.gexf."
            )
        kwargs = {"title": title, "color_by": color_by} if suffix in (".png", ".svg", ".pdf", ".html") else {}
        print(f"\nsalvo em {save_graph(graph, args.saida, **kwargs)}")


def _attach_roles(graph: nx.DiGraph, accounts_path: str | None, transactions_path: Path) -> None:
    """Copia o papel de cada conta (de accounts.csv) para os vértices do grafo, se houver."""
    path = Path(accounts_path) if accounts_path else transactions_path.with_name("accounts.csv")
    if not path.exists():
        return
    accounts = pd.read_csv(path)
    if {"account_id", "role"} <= set(accounts.columns):
        roles = accounts.set_index("account_id")["role"]
        if "is_victim" in accounts.columns:
            roles = roles.where(~accounts.set_index("account_id")["is_victim"], "vitima")
        roles = roles.to_dict()
        nx.set_node_attributes(graph, {v: roles[v] for v in graph if v in roles}, "role")
        print(f"papéis das contas lidos de {path}\n")


if __name__ == "__main__":
    main()
