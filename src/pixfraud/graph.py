"""Criação e manipulação dos grafos: contas são vértices e transferências são arestas."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import networkx as nx
import pandas as pd

DIRECTIONS = ("forward", "backward", "both")


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


def graph_from_edges(
    edges: Iterable[tuple], directed: bool = True, multigraph: bool = False
) -> nx.Graph:
    """Cria um grafo a partir de uma lista de arestas; prático para exemplos e exercícios.

    Cada aresta é ``(origem, destino)`` ou ``(origem, destino, valor)``; o valor
    vira o atributo ``amount`` (1 quando omitido). Sem ``multigraph``, arestas
    repetidas entre o mesmo par são somadas em uma só, e ``count`` guarda
    quantas eram. Com ``multigraph=True``, cada uma vira uma aresta paralela.

    >>> G = graph_from_edges([("ana", "bia", 50), ("bia", "caio", 20), ("ana", "bia", 30)])
    >>> G["ana"]["bia"]
    {'amount': 80.0, 'count': 2}
    """
    rows = [(u, v, float(rest[0]) if rest else 1.0) for u, v, *rest in edges]
    if multigraph:
        graph = nx.MultiDiGraph() if directed else nx.MultiGraph()
        for u, v, amount in rows:
            graph.add_edge(u, v, amount=amount, count=1)
        return graph
    graph = nx.DiGraph() if directed else nx.Graph()
    for u, v, amount in rows:
        if graph.has_edge(u, v):
            graph[u][v]["amount"] += amount
            graph[u][v]["count"] += 1
        else:
            graph.add_edge(u, v, amount=amount, count=1)
    return graph


def graph_from_csv(
    path: str | Path,
    source: str = "sender",
    target: str = "receiver",
    amount: str = "amount",
    aggregate: bool = True,
    **read_csv_kwargs,
) -> nx.DiGraph | nx.MultiDiGraph:
    """Lê uma tabela de transações em CSV e monta o grafo.

    ``source``, ``target`` e ``amount`` são os nomes das colunas de origem,
    destino e valor (sem coluna de valor, cada linha vale 1). Com
    ``aggregate=True`` devolve um ``DiGraph`` com uma aresta por par, como
    ``build_graph``. Com ``aggregate=False`` devolve um ``MultiDiGraph`` com uma
    aresta por linha, mantendo as demais colunas (ex.: ``timestamp``) como
    atributos da aresta.
    """
    df = pd.read_csv(path, **read_csv_kwargs)
    df = df.rename(columns={source: "sender", target: "receiver", amount: "amount"})
    if "amount" not in df:
        df["amount"] = 1.0
    if aggregate:
        return build_graph(df)
    return nx.from_pandas_edgelist(df, "sender", "receiver", edge_attr=True, create_using=nx.MultiDiGraph)


def adjacency_matrix(graph: nx.Graph, weight: str | None = None) -> pd.DataFrame:
    """Matriz de adjacência rotulada: linha = origem, coluna = destino.

    Com ``weight=None`` cada célula vale 1 se a aresta existe (num multigrafo,
    o número de arestas paralelas); com ``weight="amount"``, o valor total.
    """
    return nx.to_pandas_adjacency(graph, weight=weight, dtype=float)


def money_trail(graph: nx.DiGraph, account, max_hops: int = 3, direction: str = "forward") -> nx.DiGraph:
    """Subgrafo das contas alcançáveis a partir de ``account`` em até ``max_hops`` saltos.

    ``direction="forward"`` segue o dinheiro (para onde ele foi),
    ``"backward"`` volta à origem (de onde ele veio) e ``"both"`` faz os dois.
    O subgrafo é induzido: inclui todas as arestas entre as contas alcançadas.
    """
    if direction not in DIRECTIONS:
        raise ValueError(f"direction deve ser um de {DIRECTIONS}")
    reached = {account}
    if direction in ("forward", "both"):
        reached |= set(nx.single_source_shortest_path_length(graph, account, cutoff=max_hops))
    if direction in ("backward", "both"):
        reached |= set(nx.single_source_shortest_path_length(graph.reverse(copy=False), account, cutoff=max_hops))
    return graph.subgraph(reached).copy()


def describe(graph: nx.Graph) -> pd.Series:
    """Resumo das propriedades básicas do grafo (útil para conferir exercícios)."""
    n, m = graph.number_of_nodes(), graph.number_of_edges()
    info = {
        "vértices": n,
        "arestas": m,
        "direcionado": graph.is_directed(),
        "multigrafo": graph.is_multigraph(),
        "densidade": nx.density(graph) if n > 1 else 0.0,
        "grau médio": 2 * m / n if n else 0.0,
        "laços": nx.number_of_selfloops(graph),
    }
    if graph.is_directed():
        simple = nx.DiGraph(graph)
        info["componentes fracamente conexas"] = nx.number_weakly_connected_components(graph)
        info["componentes fortemente conexas"] = nx.number_strongly_connected_components(graph)
        info["reciprocidade"] = nx.reciprocity(simple) if m else 0.0
        info["acíclico (DAG)"] = nx.is_directed_acyclic_graph(graph)
    else:
        info["componentes conexas"] = nx.number_connected_components(graph)
    return pd.Series(info, dtype=object)
