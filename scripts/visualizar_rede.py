"""Gera o explorador interativo da rede inteira (HTML).

A página mostra todas as contas e relações, com busca, filtros por papel, cor
por papel / risco / grupo (Louvain), clique para ver a vizinhança e uma linha
do tempo dia a dia. O risco de cada modelo da vitrine (``scripts/avaliar_modelos.py``:
não supervisionados, estrutura do grafo, semi-supervisionados e tetos
supervisionados) ganha uma aba, com a average precision e o precision@k no
próprio dataset; a página abre no DBSCAN. Os semi-supervisionados partem de 25%
das fraudes e 25% das contas legítimas já conhecidas (as mesmas para todos), e as
métricas de todas as abas são calculadas nas contas que nenhum modelo conhecia.

Uso:
    python scripts/visualizar_rede.py
    python scripts/visualizar_rede.py --modelos dbscan knn kmeans pca
    python scripts/visualizar_rede.py --modelos isolation_forest --atributos grafo_avancado --saida reports/estudos/rede_if.html
"""  # noqa: E501 (exemplos de comando ficam numa linha só, para copiar e colar)

import argparse

import numpy as np

from pixfraud import gnn
from pixfraud.evaluation import ranking_metrics
from pixfraud.experiment import (
    FAMILY_OF,
    MODEL_ORDER,
    all_model_scores,
    load_experiment_config,
    prepare,
    seeded_models,
)
from pixfraud.explorer import save_network_explorer
from pixfraud.features import FEATURE_SETS
from pixfraud.simulation import load_dataset
from pixfraud.visualization import model_color, model_label

KNOWN_FRACTION = 0.25  # a mesma fração de rótulos conhecidos de scripts/avaliar_modelos.py
REFERENCE = "dbscan"


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o explorador interativo da rede inteira.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--modelos", nargs="+", default=["todos"], choices=["todos", *MODEL_ORDER],
                        metavar="MODELO", help=f"uma aba por modelo (padrão: todos). Opções: {', '.join(MODEL_ORDER)}")
    parser.add_argument("--atributos", choices=sorted(FEATURE_SETS), default="completo")
    parser.add_argument("--sem-gnn", action="store_true", help="não roda GraphSAGE e DOMINANT mesmo se instaladas")
    parser.add_argument("--saida", default="reports/estudos/rede_completa.html")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    seed = config.get("simulacao", {}).get("seed", 42)
    accounts, transactions = load_dataset(args.dados)
    prepared = prepare(accounts, transactions, config)
    labels = prepared.labels
    fraud, legit = labels.index[labels], labels.index[~labels]
    rng = np.random.default_rng([seed, 2])
    known = list(rng.choice(fraud, size=max(1, round(KNOWN_FRACTION * len(fraud))), replace=False))
    known_legit = list(rng.choice(legit, size=round(KNOWN_FRACTION * len(legit)), replace=False))
    evaluated = labels.drop(known + known_legit)

    use_gnn = gnn.available() and not args.sem_gnn
    scores = all_model_scores(prepared, seeded_models(config["modelos"], seed), FEATURE_SETS[args.atributos],
                              known, known_legit, seed=seed, use_gnn=use_gnn, reference=REFERENCE)
    chosen = MODEL_ORDER if "todos" in args.modelos else args.modelos
    risk = {m: scores[m] for m in MODEL_ORDER if m in chosen and m in scores}
    missing = [m for m in chosen if m not in scores]
    if missing:
        print(f"aviso: sem o extra 'gnn' (PyTorch Geometric), ficam de fora: {', '.join(missing)}")
    semi = {m for m in risk if FAMILY_OF[m] == "semi-supervisionado"}
    models = {
        m: {
            "label": model_label(m),
            "family": FAMILY_OF[m],
            "color": model_color(m),
            "metrics": ranking_metrics(evaluated, score),
            "known": known + known_legit if m in semi else [],
        }
        for m, score in risk.items()
    }

    info = accounts.set_index("account_id")
    roles = info["role"].where(~info["is_victim"], "vitima")
    start, end = transactions["timestamp"].min(), transactions["timestamp"].max()
    subtitle = (
        f"Dataset sintético: {len(accounts):,} contas e {len(transactions):,} Pix "
        f"de {start:%d/%m} a {end:%d/%m/%Y}. Risco de {len(risk)} modelos (atributos '{args.atributos}'); "
        f"métricas nas {len(evaluated):,} contas cujo rótulo nenhum modelo viu."
    ).replace(",", ".")
    path = save_network_explorer(
        args.saida, prepared.graph, transactions=transactions, roles=roles, risk=risk, models=models,
        initial_model=REFERENCE, title="Rede Pix sintética", subtitle=subtitle,
    )
    print(f"explorador salvo em {path} ({path.stat().st_size / 1e6:.1f} MB), {len(risk)} modelos")


if __name__ == "__main__":
    main()
