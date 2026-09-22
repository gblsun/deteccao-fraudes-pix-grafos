"""Gera o explorador interativo da rede inteira (HTML).

A página mostra todas as contas e relações, com busca, filtros por papel, cor
por papel / risco / grupo (Louvain), clique para ver a vizinhança e uma linha
do tempo dia a dia. O risco vem do detector e do conjunto de atributos
escolhidos (padrão: DBSCAN com o conjunto "completo").

Uso:
    python scripts/visualizar_rede.py
    python scripts/visualizar_rede.py --modelo isolation_forest --atributos grafo_avancado --saida reports/estudos/rede_if.html
"""

import argparse

from pixfraud.anomaly import DETECTORS
from pixfraud.experiment import load_experiment_config, prepare
from pixfraud.explorer import save_network_explorer
from pixfraud.features import FEATURE_SETS
from pixfraud.simulation import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o explorador interativo da rede inteira.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--modelo", choices=sorted(DETECTORS), default="dbscan")
    parser.add_argument("--atributos", choices=sorted(FEATURE_SETS), default="completo")
    parser.add_argument("--saida", default="reports/estudos/rede_completa.html")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    accounts, transactions = load_dataset(args.dados)
    prepared = prepare(accounts, transactions, config)
    detect = DETECTORS[args.modelo]
    risk = detect(prepared.features[FEATURE_SETS[args.atributos]], **config["modelos"][args.modelo]).scores

    info = accounts.set_index("account_id")
    roles = info["role"].where(~info["is_victim"], "vitima")
    start, end = transactions["timestamp"].min(), transactions["timestamp"].max()
    subtitle = (
        f"Dataset sintético: {len(accounts):,} contas e {len(transactions):,} Pix "
        f"de {start:%d/%m} a {end:%d/%m/%Y}. Risco: {args.modelo} com atributos '{args.atributos}'."
    ).replace(",", ".")
    path = save_network_explorer(
        args.saida, prepared.graph, transactions=transactions, roles=roles, risk=risk,
        title="Rede Pix sintética", subtitle=subtitle,
    )
    print(f"explorador salvo em {path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
