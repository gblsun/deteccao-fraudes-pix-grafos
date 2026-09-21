"""Cria, resume e salva grafos sem precisar escrever código.

O formato de saída vem da extensão: .png/.svg/.pdf (imagem), .html (interativo,
abre no navegador) ou .gexf/.graphml (para o Gephi).

Exemplos:
    # padrões de fraude prontos (fan_in, fan_out, chain, cycle, scatter_gather, mule_ring)
    python scripts/criar_grafo.py padrao mule_ring --saida reports/estudos/anel.png
    python scripts/criar_grafo.py padrao chain --tamanho 6 --saida reports/estudos/cadeia.html

    # qualquer CSV de transações (colunas de origem, destino e, opcionalmente, valor)
    python scripts/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --contas estudos/dados/exemplo_contas.csv --saida reports/estudos/exemplo.png

    # o caminho do dinheiro em volta de uma conta do dataset sintético
    python scripts/criar_grafo.py csv data/synthetic/transactions.csv --conta C000167 --saltos 2 --direcao tras --saida reports/estudos/trilha.html
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud.graph import describe, graph_from_csv, money_trail  # noqa: E402
from pixfraud.patterns import PATTERNS  # noqa: E402
from pixfraud.visualization import save_graph  # noqa: E402

DIRECTIONS = {"frente": "forward", "tras": "backward", "ambos": "both"}
MAX_NODES_IMAGE = 300


def main() -> None:
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

    for p in (padrao, csv):
        p.add_argument("--saida", help="arquivo de saída (.png, .svg, .pdf, .html, .gexf, .graphml)")
    args = parser.parse_args()

    if args.fonte == "padrao":
        make = PATTERNS[args.nome]
        graph = make(args.tamanho) if args.tamanho else make()
        title = f"Padrão: {args.nome}"
    else:
        graph = graph_from_csv(args.arquivo, source=args.origem, target=args.destino, amount=args.valor)
        _attach_roles(graph, args.contas, Path(args.arquivo))
        title = Path(args.arquivo).name
        if args.conta:
            if args.conta not in graph:
                parser.error(f"a conta {args.conta} não aparece no arquivo")
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
        kwargs = {"title": title} if suffix in (".png", ".svg", ".pdf", ".html") else {}
        print(f"\nsalvo em {save_graph(graph, args.saida, **kwargs)}")


def _attach_roles(graph: nx.DiGraph, accounts_path: str | None, transactions_path: Path) -> None:
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
