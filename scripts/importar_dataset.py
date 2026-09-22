"""Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.

Depois de importar, o mesmo pipeline roda sobre os dados externos:

    python scripts/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --dias 3
    python scripts/rodar_experimento.py --dados data/external/amlworld --saida reports/amlworld
    python scripts/visualizar_rede.py --dados data/external/amlworld --saida reports/amlworld/rede.html

Os arquivos originais precisam ser baixados à mão do Kaggle (ver data/README.md).
"""

import argparse

from pixfraud.external import load_amlworld, load_paysim
from pixfraud.simulation import save_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa um dataset público para o formato do projeto.")
    parser.add_argument("fonte", choices=["amlworld", "paysim"])
    parser.add_argument("arquivo", help="CSV original baixado do Kaggle")
    parser.add_argument("--saida", help="pasta de saída (padrão: data/external/<fonte>)")
    parser.add_argument("--linhas", type=int, help="lê só as primeiras N linhas do arquivo")
    parser.add_argument("--dias", type=int, help="AMLworld: mantém só os primeiros N dias")
    parser.add_argument("--moeda", default="US Dollar", help="AMLworld: moeda mantida ('todas' para não filtrar)")
    args = parser.parse_args()

    if args.fonte == "amlworld":
        currency = None if args.moeda == "todas" else args.moeda
        accounts, transactions = load_amlworld(args.arquivo, currency=currency, days=args.dias, nrows=args.linhas)
    else:
        accounts, transactions = load_paysim(args.arquivo, nrows=args.linhas)
    out = args.saida or f"data/external/{args.fonte}"
    save_dataset(accounts, transactions, out)
    print(f"{len(accounts):,} contas e {len(transactions):,} transações salvas em {out}".replace(",", "."))
    print(f"contas marcadas como fraude: {accounts['is_fraud'].sum()} ({accounts['is_fraud'].mean():.3%})")
    print(f"transações marcadas como fraude: {transactions['is_fraud'].sum()} ({transactions['is_fraud'].mean():.3%})")


if __name__ == "__main__":
    main()
