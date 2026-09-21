"""Modelagem das transações como grafo: contas são vértices e transferências são arestas."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx
import pandas as pd


def build_graph(transactions: pd.DataFrame, accounts: Iterable[str] | None = None) -> nx.DiGraph:
    """Monta o grafo direcionado de transações.

    Todas as transferências de um mesmo par (pagador, recebedor) são agregadas
    em uma única aresta direcionada, com os atributos ``amount`` (valor total)
    e ``count`` (número de transferências). Se ``accounts`` for informado,
    contas sem nenhuma transação também entram no grafo, como vértices isolados.
    """
    edges = transactions.groupby(["sender", "receiver"], as_index=False).agg(
        amount=("amount", "sum"), count=("amount", "size")
    )
    graph = nx.from_pandas_edgelist(
        edges, "sender", "receiver", edge_attr=["amount", "count"], create_using=nx.DiGraph
    )
    if accounts is not None:
        graph.add_nodes_from(accounts)
    return graph
