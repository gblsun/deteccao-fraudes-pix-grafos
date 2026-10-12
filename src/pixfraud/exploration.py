"""O que o explorador interativo (``app/explorador.py``) e a página da rede precisam calcular.

Fica no pacote, e não no app, para poder ser testado sem o Streamlit:

* ``generate_network``: gera e prepara a rede de uma semente e um cenário;
* ``all_model_scores``: o escore de risco de **todos** os modelos, não
  supervisionados e supervisionados;
* ``rank_models``: a nota (AP e precision@k) de cada modelo, ordenada dentro do grupo;
* ``network_summary``: os números que resumem a rede (contas, quadrilhas,
  valor dos golpes, componente gigante...);
* ``top_k_outcome``: o que o modelo acertou e errou entre as ``k`` contas mais suspeitas.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import networkx as nx
import pandas as pd

from pixfraud import gnn
from pixfraud.evaluation import ranking_metrics
from pixfraud.experiment import SUPERVISED_MODELS, Prepared, load_scenarios, prepare, supervised_scores
from pixfraud.models import DETECTORS, GRAPH_DETECTORS
from pixfraud.network import component_summary
from pixfraud.simulation import generate_dataset, load_config, with_overrides
from pixfraud.visualization import model_label

UNSUPERVISED = "Não supervisionados"
SUPERVISED = "Supervisionados (usam os rótulos)"
OUTCOMES = {"achou": "fraude no top-k", "alarme_falso": "legítima no top-k", "perdeu": "fraude fora do top-k",
            "resto": "legítima fora do top-k"}


def generate_network(scenario: str, seed: int, config: dict, config_path: str | Path,
                     scenarios_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, Prepared]:
    """Contas, Pix e a rede preparada (grafo, atributos, rótulos) de ``seed`` no ``scenario``.

    O mesmo caminho dos estudos (``scripts/03_modelos/avaliar_modelos.py``): o gerador de
    ``config_path`` com os parâmetros do cenário trocados, e a semente trocada.
    """
    scenarios = load_scenarios(scenarios_path)
    if scenario not in scenarios:
        raise ValueError(f"cenário desconhecido: {scenario} (use um de {list(scenarios)})")
    simulation = replace(with_overrides(load_config(config_path), scenarios[scenario]), seed=int(seed))
    accounts, transactions = generate_dataset(simulation)
    return accounts, transactions, prepare(accounts, transactions, config)


def all_model_scores(prepared: Prepared, columns: list, config: dict, seed: int,
                     progress: Callable[[str, float], None] | None = None) -> dict[str, tuple[str, pd.Series]]:
    """Escores de cada modelo: ``{nome: (grupo, escores)}``.

    ``grupo`` é ``UNSUPERVISED`` ou ``SUPERVISED``; os supervisionados são
    pontuados em validação cruzada (cada conta pelo modelo que não viu o
    rótulo dela). As redes neurais para grafos entram só com o extra ``gnn``.
    Um modelo que falha (ex.: o DOMINANT recusa redes muito grandes) é pulado,
    para não perder o resto. ``progress(nome, segundos)`` é chamado depois de
    cada modelo.
    """
    features, graph, labels, models = prepared.features[columns], prepared.graph, prepared.labels, config["modelos"]
    jobs = [(m, UNSUPERVISED, lambda d=d, m=m: d(features, **models.get(m, {})).scores) for m, d in DETECTORS.items()]
    jobs += [(m, UNSUPERVISED, lambda d=d, m=m: d(graph, **models.get(m, {})).scores)
             for m, d in GRAPH_DETECTORS.items()]
    if gnn.torch is not None:
        jobs.append(("dominant", UNSUPERVISED, lambda: gnn.dominant_scores(graph, features, seed=seed)))
    jobs += [(m, SUPERVISED, lambda m=m: supervised_scores(features, labels, seed=seed, model=m, **models.get(m, {})))
             for m in SUPERVISED_MODELS]
    if gnn.torch is not None:
        jobs.append(("graphsage_propria", SUPERVISED,
                     lambda: gnn.sage_supervised_scores(graph, features, labels, seed=seed)))
    if gnn.available():
        jobs.append(("graphsage", SUPERVISED, lambda: gnn.graphsage_scores(graph, features, labels, seed=seed)))

    scores = {}
    for name, group, run in jobs:
        began = time.time()
        try:
            scores[name] = (group, run())
        except (ImportError, MemoryError, ValueError):
            continue
        if progress is not None:
            progress(name, time.time() - began)
    return scores


def rank_models(scores: dict[str, tuple[str, pd.Series]], labels: pd.Series, k: int | None = None) -> pd.DataFrame:
    """Uma linha por modelo: grupo, nome legível, AP, ROC-AUC e precision@k.

    Ordenada pelo grupo (não supervisionados primeiro) e, dentro dele, da maior
    AP para a menor; a coluna ``posicao`` é a colocação dentro do grupo.
    """
    rows = []
    for name, (group, score) in scores.items():
        metrics = ranking_metrics(labels.reindex(score.index).astype(bool), score, k)
        rows.append({"modelo": name, "nome": model_label(name), "grupo": group, **metrics})
    table = pd.DataFrame(rows)
    table["_supervisionado"] = table["grupo"] != UNSUPERVISED
    table = table.sort_values(["_supervisionado", "average_precision"], ascending=[True, False])
    table["posicao"] = table.groupby("grupo").cumcount() + 1
    return table.drop(columns="_supervisionado").reset_index(drop=True)


def picker_entries(scores: dict[str, tuple[str, pd.Series]], ranking: pd.DataFrame) -> tuple[dict, dict]:
    """``risk`` e ``risk_groups`` para ``explorer.network_explorer_html``, na ordem de ``ranking``.

    Cada modelo aparece no seletor como "1º PCA · AP 0,81", agrupado em não
    supervisionados e supervisionados.
    """
    risk, groups = {}, {}
    for row in ranking.itertuples():
        label = f"{row.posicao}º {row.nome} · AP {row.average_precision:.2f}".replace(".", ",")
        risk[label], groups[label] = scores[row.modelo][1], row.grupo
    return risk, groups


def network_summary(accounts: pd.DataFrame, transactions: pd.DataFrame, graph: nx.DiGraph) -> dict:
    """Os números que resumem uma rede, para os cartões do explorador.

    Uma quadrilha = uma conta coletora (o gerador cria uma por quadrilha). O
    valor dos golpes soma os Pix de fraude pagos pelas vítimas; os repasses
    dentro da quadrilha não entram, para não contar o mesmo dinheiro duas vezes.
    """
    roles = accounts.set_index("account_id")["role"]
    fraud_accounts = accounts["is_fraud"].astype(bool)
    victims = set(accounts.loc[accounts["is_victim"].astype(bool), "account_id"])
    scams = transactions[transactions["is_fraud"].astype(bool) & transactions["sender"].isin(victims)]
    components = component_summary(graph)
    first, last = transactions["timestamp"].min().normalize(), transactions["timestamp"].max().normalize()
    return {
        "contas": len(accounts),
        "pix": len(transactions),
        "valor_total": float(transactions["amount"].sum()),
        "dias": int((last - first).days) + 1,  # dias do calendário, do primeiro ao último Pix
        "quadrilhas": int((roles == "coletor").sum()),
        "contas_fraudulentas": int(fraud_accounts.sum()),
        "taxa_fraude": float(fraud_accounts.mean()),
        "vitimas": len(victims),
        "golpes": len(scams),
        "valor_golpes": float(scams["amount"].sum()),
        "relacoes": graph.number_of_edges(),
        "gigante_fraca": float(components["gigante_fraca"]),
        "gigante_forte": float(components["gigante_forte"]),
    }


def top_k_outcome(scores: pd.Series, labels: pd.Series, k: int) -> pd.Series:
    """Para cada conta: ``achou``, ``alarme_falso``, ``perdeu`` ou ``resto`` (ver ``OUTCOMES``).

    O top-k são as ``k`` contas de maior escore, a fila que um analista olharia primeiro.
    """
    y = labels.reindex(scores.index).astype(bool)
    top = scores.index.isin(scores.nlargest(k).index)
    outcome = pd.Series("resto", index=scores.index, name="resultado")
    outcome[top & y] = "achou"
    outcome[top & ~y] = "alarme_falso"
    outcome[~top & y] = "perdeu"
    return outcome
