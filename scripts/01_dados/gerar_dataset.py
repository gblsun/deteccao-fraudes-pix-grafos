"""Gera o dataset sintético de transações PIX.

Cada execução sorteia uma semente nova, então o dataset muda a cada vez. A semente usada
é impressa e gravada em ``dataset_meta.json`` na pasta de saída; ``--seed N`` refaz
exatamente aquele dataset. A ``seed`` de ``simulacao`` no YAML não é usada aqui.

Uso:
    python scripts/01_dados/gerar_dataset.py                  # dataset novo, semente sorteada
    python scripts/01_dados/gerar_dataset.py --seed 42        # o dataset dos resultados em reports/
    python scripts/01_dados/gerar_dataset.py --aleatorio      # sorteia nº de quadrilhas, laranjas, vítimas, comércios
    python scripts/01_dados/gerar_dataset.py --config configs/experimento.yaml --saida data/synthetic
"""

import argparse
import secrets
from dataclasses import asdict, replace
from pathlib import Path

from pixfraud.experiment import save_metadata
from pixfraud.simulation import generate_dataset, load_config, save_dataset, structure_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o dataset sintético de transações PIX.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--saida", default="data/synthetic")
    parser.add_argument("--seed", type=int, default=None,
                        help="semente do gerador; sem ela, sorteia uma nova a cada execução")
    parser.add_argument("--aleatorio", action="store_true",
                        help="sorteia a estrutura (estrutura_aleatoria): os valores do YAML viram médias")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else secrets.randbelow(2**32)
    cfg = replace(load_config(args.config), seed=seed)
    if args.aleatorio:
        cfg = replace(cfg, estrutura_aleatoria=True)
    accounts, transactions = generate_dataset(cfg)
    save_dataset(accounts, transactions, args.saida)
    structure = structure_summary(cfg)
    save_metadata(Path(args.saida) / "dataset_meta.json", asdict(cfg), seed=seed, estrutura=structure)

    print(f"{len(accounts)} contas e {len(transactions)} transações salvas em {args.saida}")
    print(f"semente: {seed} (reproduza com --seed {seed})")
    print(f"contas fraudulentas: {accounts['is_fraud'].sum()} ({accounts['is_fraud'].mean():.2%})")
    print(f"transações fraudulentas: {transactions['is_fraud'].sum()} ({transactions['is_fraud'].mean():.2%})")
    if cfg.estrutura_aleatoria:
        print(f"estrutura sorteada: {len(structure['quadrilhas'])} quadrilhas, {structure['n_comercios']} comércios")
        for i, ring in enumerate(structure["quadrilhas"], 1):
            print(f"  quadrilha {i}: {ring}")
    print("\npapéis:\n" + accounts["role"].value_counts().to_string())
    print("\ncenários:\n" + transactions["scenario"].value_counts().to_string())


if __name__ == "__main__":
    main()
