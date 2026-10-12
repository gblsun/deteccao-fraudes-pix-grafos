"""Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.

Depois de importar, o mesmo pipeline roda sobre os dados externos:

    python scripts/01_dados/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --dias 3
    python scripts/03_modelos/rodar_experimento.py --dados data/external/amlworld --saida reports/amlworld
    python scripts/02_exploracao/visualizar_rede.py --dados data/external/amlworld --saida reports/amlworld/rede.html

Para a avaliação por janelas e por tipologia (scripts/04_avaliacao/avaliar_externo.py), importe
também o arquivo de padrões; --formatos ACH Wire mantém só as transferências
parecidas com o Pix:

    python scripts/01_dados/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv \\
        --padroes data/raw/HI-Small_Patterns.txt --formatos ACH Wire --saida data/external/amlworld_pix

Os arquivos originais vêm do Kaggle (ver data/README.md).
"""

import argparse
from pathlib import Path

from pixfraud.external import load_amlworld, load_amlworld_patterns, load_paysim, pattern_accounts
from pixfraud.simulation import save_dataset


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Importa um dataset público para o formato do projeto.")
    parser.add_argument("fonte", choices=["amlworld", "paysim"])
    parser.add_argument("arquivo", help="CSV original baixado do Kaggle")
    parser.add_argument("--saida", help="pasta de saída (padrão: data/external/<fonte>)")
    parser.add_argument("--linhas", type=int, help="lê só as primeiras N linhas do arquivo")
    parser.add_argument("--dias", type=int, help="AMLworld: mantém só os primeiros N dias")
    parser.add_argument("--moeda", default="US Dollar", help="AMLworld: moeda mantida ('todas' para não filtrar)")
    parser.add_argument("--formatos", nargs="+",
                        help="AMLworld: formas de pagamento mantidas (ex.: ACH Wire); padrão: todas")
    parser.add_argument("--padroes", help="AMLworld: arquivo *_Patterns.txt, salvo como patterns.csv")
    args = parser.parse_args()

    if args.fonte == "amlworld":
        currency = None if args.moeda == "todas" else args.moeda
        accounts, transactions = load_amlworld(args.arquivo, currency=currency, days=args.dias,
                                               nrows=args.linhas, formats=args.formatos)
    else:
        accounts, transactions = load_paysim(args.arquivo, nrows=args.linhas)
    out = Path(args.saida or f"data/external/{args.fonte}")
    save_dataset(accounts, transactions, out)
    print(f"{len(accounts):,} contas e {len(transactions):,} transações salvas em {out}".replace(",", "."))
    print(f"contas marcadas como fraude: {accounts['is_fraud'].sum()} ({accounts['is_fraud'].mean():.3%})")
    print(f"transações marcadas como fraude: {transactions['is_fraud'].sum()} ({transactions['is_fraud'].mean():.3%})")

    if args.padroes:
        members = pattern_accounts(load_amlworld_patterns(args.padroes))
        members = members[members["account_id"].isin(accounts.loc[accounts["is_fraud"], "account_id"])]
        members.to_csv(out / "patterns.csv", index=False)
        print("contas fraudulentas por tipologia:")
        print(members["typology"].value_counts().to_string())


if __name__ == "__main__":
    main()
