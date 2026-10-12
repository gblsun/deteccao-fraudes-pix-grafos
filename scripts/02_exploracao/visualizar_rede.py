"""Gera o explorador interativo da rede inteira (HTML).

A página mostra todas as contas e relações, com busca, filtros por papel, cor
por papel / risco / grupo (Louvain), clique para ver a vizinhança e uma linha
do tempo dia a dia. O risco vem de **todos os modelos**, e um seletor na página
escolhe qual deles pinta as contas, com a lista separada em não
supervisionados e supervisionados (os que usam os rótulos, com validação
cruzada: cada conta recebe o escore de um modelo treinado sem ela). Em cada
grupo, os modelos vêm do mais eficaz ao menos, pela average precision (AP)
que tiveram nesta rede, mostrada ao lado do nome. As redes
neurais para grafos (DOMINANT e GraphSAGE) entram só se o extra ``gnn``
estiver instalado. Com ``--modelo``, a página usa um detector só, como antes.

Uso:
    python scripts/02_exploracao/visualizar_rede.py
    python scripts/02_exploracao/visualizar_rede.py --modelo isolation_forest --atributos grafo_avancado --saida reports/estudos/rede_if.html
"""  # noqa: E501 (exemplos de comando ficam numa linha só, para copiar e colar)

import argparse

from pixfraud import gnn
from pixfraud.experiment import load_experiment_config, prepare
from pixfraud.exploration import all_model_scores, picker_entries, rank_models
from pixfraud.explorer import save_network_explorer
from pixfraud.features import FEATURE_SETS
from pixfraud.models import DETECTORS
from pixfraud.simulation import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o explorador interativo da rede inteira.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--modelo", choices=sorted(DETECTORS),
                        help="usa só este detector (padrão: todos os modelos, com seletor na página)")
    parser.add_argument("--atributos", choices=sorted(FEATURE_SETS), default="completo")
    parser.add_argument("--seed", type=int, default=42, help="semente dos modelos supervisionados e das GNN")
    parser.add_argument("--saida", default="reports/estudos/rede_completa.html")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    accounts, transactions = load_dataset(args.dados)
    prepared = prepare(accounts, transactions, config)
    columns = FEATURE_SETS[args.atributos]
    if args.modelo:
        detect = DETECTORS[args.modelo]
        risk = detect(prepared.features[columns], **config["modelos"].get(args.modelo, {})).scores
        groups, about = None, f"Risco: {args.modelo} com atributos '{args.atributos}'."
    else:
        scores = all_model_scores(prepared, columns, config, args.seed,
                                  progress=lambda name, seconds: print(f"  {name}: {seconds:.1f} s"))
        if gnn.torch is None:
            print('  DOMINANT e GraphSAGE pulados: instale o extra gnn (pip install -e ".[gnn]")')
        risk, groups = picker_entries(scores, rank_models(scores, prepared.labels))
        about = f"Risco: {len(risk)} modelos (escolha no seletor), atributos '{args.atributos}'."

    info = accounts.set_index("account_id")
    roles = info["role"].where(~info["is_victim"], "vitima")
    start, end = transactions["timestamp"].min(), transactions["timestamp"].max()
    subtitle = (
        f"Dataset sintético: {len(accounts):,} contas e {len(transactions):,} Pix "
        f"de {start:%d/%m} a {end:%d/%m/%Y}. "
    ).replace(",", ".") + about
    path = save_network_explorer(
        args.saida, prepared.graph, transactions=transactions, roles=roles, risk=risk, risk_groups=groups,
        labels=prepared.labels, title="Rede Pix sintética", subtitle=subtitle,
    )
    print(f"explorador salvo em {path} ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
