"""Atributos por conta usados pelos detectores de anomalia.

Os atributos são separados em grupos para permitir a comparação entre a
abordagem tabular e a abordagem baseada em grafos:

* tabulares: agregados das transações de cada conta, sem olhar para a
  estrutura da rede;
* temporais: velocidade de repasse e picos de recebimento (``pixfraud.temporal``);
* de grafo: métricas estruturais clássicas calculadas sobre o grafo;
* estruturais avançados: k-núcleo, participação entre comunidades e OddBall
  (``pixfraud.communities``).
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from pixfraud.communities import STRUCTURAL_EXTRA, structural_features
from pixfraud.temporal import temporal_features

TABULAR_FEATURES = [
    "account_age_days",
    "n_sent",
    "n_received",
    "amount_sent",
    "amount_received",
    "max_amount_received",
    "pass_through",
    "night_ratio",
]
GRAPH_FEATURES = [
    "in_degree",
    "out_degree",
    "pagerank",
    "betweenness",
    "clustering",
    "avg_neighbor_degree",
]
TEMPORAL_FEATURES = ["dwell_time_min", "max_daily_in_degree"]
FEATURE_SETS = {
    "tabular": TABULAR_FEATURES,
    "grafo": GRAPH_FEATURES,
    "combinado": TABULAR_FEATURES + GRAPH_FEATURES,
    "temporal": TEMPORAL_FEATURES,
    "grafo_avancado": GRAPH_FEATURES + STRUCTURAL_EXTRA,
    "completo": TABULAR_FEATURES + TEMPORAL_FEATURES + GRAPH_FEATURES + STRUCTURAL_EXTRA,
}


def tabular_features(transactions: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    """Agregados por conta, calculados diretamente da tabela de transações."""
    sent = transactions.groupby("sender")["amount"].agg(n_sent="size", amount_sent="sum")
    received = transactions.groupby("receiver")["amount"].agg(
        n_received="size", amount_received="sum", max_amount_received="max"
    )
    # Fração das transações da conta (enviadas ou recebidas) feitas entre 0h e 6h.
    night = transactions["timestamp"].dt.hour < 6
    parties = pd.concat([
        pd.DataFrame({"account_id": transactions["sender"], "night": night}),
        pd.DataFrame({"account_id": transactions["receiver"], "night": night}),
    ])
    night_ratio = parties.groupby("account_id")["night"].mean().rename("night_ratio")

    df = accounts.set_index("account_id")[["account_age_days"]].join([sent, received, night_ratio])
    df = df.fillna(0.0)
    # Fração do dinheiro que "atravessa" a conta: perto de 1 quando quase tudo
    # o que entra volta a sair, como numa conta laranja.
    flow_max = np.maximum(df["amount_sent"], df["amount_received"])
    flow_min = np.minimum(df["amount_sent"], df["amount_received"])
    df["pass_through"] = (flow_min / flow_max.where(flow_max > 0)).fillna(0.0)
    return df[TABULAR_FEATURES]


def graph_features(graph: nx.DiGraph, betweenness_k: int | None = 500, seed: int = 42) -> pd.DataFrame:
    """Métricas estruturais de cada vértice do grafo de transações.

    ``betweenness_k`` limita o cálculo da intermediação a ``k`` vértices de
    origem sorteados (aproximação de Brandes); ``None`` calcula o valor exato,
    que fica lento em grafos grandes.
    """
    undirected = graph.to_undirected(as_view=True)
    if betweenness_k is not None and betweenness_k >= graph.number_of_nodes():
        betweenness_k = None
    df = pd.DataFrame({
        # grau: nº de contas distintas das quais recebe / para as quais envia
        "in_degree": dict(graph.in_degree()),
        "out_degree": dict(graph.out_degree()),
        # centralidade: PageRank ponderado pelo valor transferido
        "pagerank": nx.pagerank(graph, weight="amount"),
        # intermediação: quanto a conta está no caminho do dinheiro entre outras
        "betweenness": nx.betweenness_centrality(graph, k=betweenness_k, seed=seed),
        # agrupamento: se os parceiros da conta também transacionam entre si
        "clustering": nx.clustering(undirected),
        "avg_neighbor_degree": nx.average_neighbor_degree(undirected),
    })
    return df[GRAPH_FEATURES]


def build_features(
    transactions: pd.DataFrame,
    accounts: pd.DataFrame,
    graph: nx.DiGraph,
    betweenness_k: int | None = 500,
    seed: int = 42,
) -> pd.DataFrame:
    """Tabela com todos os atributos (de todos os grupos), indexada por conta."""
    tabular = tabular_features(transactions, accounts)
    temporal = temporal_features(transactions, accounts)
    structural = graph_features(graph, betweenness_k=betweenness_k, seed=seed)
    extra = structural_features(graph, seed=seed)
    return tabular.join([temporal, structural, extra]).fillna(0.0)
