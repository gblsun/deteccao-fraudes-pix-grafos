"""Gera o dataset sintético de transações PIX.

Uso:
    python scripts/gerar_dataset.py --config configs/experimento.yaml --saida data/synthetic
"""

import argparse

from pixfraud.simulation import generate_dataset, load_config, save_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o dataset sintético de transações PIX.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--saida", default="data/synthetic")
    args = parser.parse_args()

    accounts, transactions = generate_dataset(load_config(args.config))
    save_dataset(accounts, transactions, args.saida)

    print(f"{len(accounts)} contas e {len(transactions)} transações salvas em {args.saida}")
    print(f"contas fraudulentas: {accounts['is_fraud'].sum()} ({accounts['is_fraud'].mean():.2%})")
    print(f"transações fraudulentas: {transactions['is_fraud'].sum()} ({transactions['is_fraud'].mean():.2%})")
    print("\npapéis:\n" + accounts["role"].value_counts().to_string())
    print("\ncenários:\n" + transactions["scenario"].value_counts().to_string())


if __name__ == "__main__":
    main()
