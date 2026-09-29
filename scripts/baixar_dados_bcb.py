"""Baixa estatísticas do PIX da API de dados abertos do Banco Central.

Exemplos:
    python scripts/baixar_dados_bcb.py fraudes 202506
    python scripts/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506"
    python scripts/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506" --top 1000 --tentativas 5

Erros passageiros do servidor (como o 504 frequente em ``transacoes``) são tentados de
novo com espera crescente entre as tentativas.
"""

import argparse
from pathlib import Path

from pixfraud.bcb import RESOURCES, fetch


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa estatísticas do PIX (dados abertos do BCB).")
    parser.add_argument("recurso", choices=sorted(RESOURCES))
    parser.add_argument("database", help="parâmetro obrigatório da API, ex.: 202506")
    parser.add_argument("--filtro", help="expressão OData $filter, ex.: \"AnoMes eq 202506\"")
    parser.add_argument("--top", type=int, help="limita o nº de linhas (a API não pagina)")
    parser.add_argument("--tentativas", type=int, default=3, help="tentativas em 502/503/504 ou falha de conexão")
    parser.add_argument("--espera", type=float, default=30, help="segundos antes da 2ª tentativa (dobra a cada nova)")
    parser.add_argument("--saida", default="data/bcb")
    args = parser.parse_args()

    df = fetch(args.recurso, args.database, filter=args.filtro, top=args.top, retries=args.tentativas,
               backoff=args.espera)
    out = Path(args.saida)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{args.recurso}_{args.database}.csv"
    df.to_csv(path, index=False)
    print(f"{len(df)} linhas salvas em {path}")


if __name__ == "__main__":
    main()
