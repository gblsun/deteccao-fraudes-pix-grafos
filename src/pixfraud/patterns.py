"""Padrões de fraude como pequenos grafos, para estudo e para injetar em redes maiores.

Cada função devolve um ``nx.DiGraph`` em que as arestas têm ``amount`` (valor)
e ``count`` (nº de Pix) e os vértices têm ``role``: ``vitima`` para contas
honestas que pagaram um golpe, ou um dos papéis de fraude (``laranja``,
``intermediario``, ``coletor``). Os formatos seguem os padrões clássicos de
lavagem de dinheiro (fan-in, fan-out, cadeia, ciclo, scatter-gather; ver
``altman2023realistic`` em ``docs/referencias.bib``).
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from pixfraud.simulation import FRAUD_ROLES


def _add(graph: nx.DiGraph, u: str, v: str, amount: float) -> None:
    graph.add_edge(u, v, amount=round(float(amount), 2), count=1)


def fan_in(n_sources: int = 5, amount: float = 500.0) -> nx.DiGraph:
    """Várias vítimas pagam a mesma conta laranja (muitos -> um)."""
    graph = nx.DiGraph()
    graph.add_node("laranja", role="laranja")
    for i in range(n_sources):
        graph.add_node(f"vitima_{i}", role="vitima")
        _add(graph, f"vitima_{i}", "laranja", amount)
    return graph


def fan_out(n_targets: int = 5, amount: float = 2500.0) -> nx.DiGraph:
    """Pulverização: a laranja divide o valor entre várias contas (um -> muitos)."""
    graph = nx.DiGraph()
    graph.add_node("laranja", role="laranja")
    for i in range(n_targets):
        graph.add_node(f"intermediario_{i}", role="intermediario")
        _add(graph, "laranja", f"intermediario_{i}", amount / n_targets)
    return graph


def chain(length: int = 4, amount: float = 1000.0, fee: float = 0.03) -> nx.DiGraph:
    """Lavagem em cadeia: laranja -> intermediários -> coletor, com comissão ``fee`` a cada salto.

    ``length`` é o número de contas na cadeia (no mínimo 2).
    """
    if length < 2:
        raise ValueError("a cadeia precisa de pelo menos 2 contas")
    names = ["laranja"] + [f"intermediario_{i}" for i in range(1, length - 1)] + ["coletor"]
    graph = nx.DiGraph()
    for name in names:
        graph.add_node(name, role=name.split("_")[0])
    for u, v in zip(names[:-1], names[1:]):
        _add(graph, u, v, amount)
        amount *= 1 - fee
    return graph


def cycle(length: int = 4, amount: float = 1000.0, fee: float = 0.0) -> nx.DiGraph:
    """Ciclo (*round-tripping*): o dinheiro passa por várias contas e volta à primeira."""
    if length < 2:
        raise ValueError("o ciclo precisa de pelo menos 2 contas")
    names = [f"intermediario_{i}" for i in range(length)]
    graph = nx.DiGraph()
    graph.add_nodes_from(names, role="intermediario")
    for u, v in zip(names, names[1:] + names[:1]):
        _add(graph, u, v, amount)
        amount *= 1 - fee
    return graph


def scatter_gather(n_middle: int = 4, amount: float = 1000.0, fee: float = 0.02) -> nx.DiGraph:
    """Espalha e junta: laranja -> vários intermediários -> coletor."""
    graph = nx.DiGraph()
    graph.add_node("laranja", role="laranja")
    graph.add_node("coletor", role="coletor")
    part = amount / n_middle
    for i in range(n_middle):
        middle = f"intermediario_{i}"
        graph.add_node(middle, role="intermediario")
        _add(graph, "laranja", middle, part)
        _add(graph, middle, "coletor", part * (1 - fee))
    return graph


def mule_ring(
    n_victims: int = 6,
    n_mules: int = 2,
    chain_length: int = 2,
    amount: float = 800.0,
    fee: float = 0.03,
) -> nx.DiGraph:
    """Quadrilha completa: vítimas -> laranjas -> cadeia de intermediários -> coletor.

    É o mesmo formato usado pelo gerador do dataset sintético. As vítimas são
    distribuídas entre as laranjas em rodízio.
    """
    graph = nx.DiGraph()
    mules = [f"laranja_{j}" for j in range(n_mules)]
    middle = [f"intermediario_{k}" for k in range(chain_length)]
    graph.add_nodes_from(mules, role="laranja")
    graph.add_nodes_from(middle, role="intermediario")
    graph.add_node("coletor", role="coletor")
    received = dict.fromkeys(mules, 0.0)
    for i in range(n_victims):
        victim, mule = f"vitima_{i}", mules[i % n_mules]
        graph.add_node(victim, role="vitima")
        _add(graph, victim, mule, amount)
        received[mule] += amount
    for mule, total in received.items():
        if total:
            _add(graph, mule, (middle or ["coletor"])[0], total * (1 - fee))
    path = middle + ["coletor"]
    total = sum(received.values()) * (1 - fee)
    for u, v in zip(path[:-1], path[1:]):
        total *= 1 - fee
        _add(graph, u, v, total)
    return graph


PATTERNS = {
    "fan_in": fan_in,
    "fan_out": fan_out,
    "chain": chain,
    "cycle": cycle,
    "scatter_gather": scatter_gather,
    "mule_ring": mule_ring,
}


def inject(
    graph: nx.DiGraph,
    pattern: nx.DiGraph,
    prefix: str = "padrao",
    camouflage: int = 2,
    seed: int | None = None,
) -> nx.DiGraph:
    """Copia ``pattern`` para dentro de ``graph`` e devolve o novo grafo (o original não muda).

    * vértices com papel ``vitima`` são associados a contas já existentes,
      sorteadas, que passam a ter ``role="vitima"``;
    * os demais viram contas novas, chamadas ``{prefix}_{nome no padrão}``;
    * cada conta nova faz ``camouflage`` Pix pequenos para contas existentes
      sorteadas, para não ficar isolada do resto da rede;
    * vértices do grafo original sem papel recebem ``role="normal"``.
    """
    rng = np.random.default_rng(seed)
    existing = list(graph.nodes)
    victims = [v for v, role in pattern.nodes(data="role") if role == "vitima"]
    if len(victims) > len(existing):
        raise ValueError("o grafo tem menos contas do que o padrão tem vítimas")

    result = graph.copy()
    for v in result:
        result.nodes[v].setdefault("role", "normal")
    chosen = rng.choice(len(existing), size=len(victims), replace=False)
    mapping = {v: existing[i] for v, i in zip(victims, chosen)}
    mapping |= {v: f"{prefix}_{v}" for v in pattern if v not in mapping}

    for v, data in pattern.nodes(data=True):
        if mapping[v] in result and data.get("role") != "vitima":
            raise ValueError(f"já existe uma conta chamada {mapping[v]!r}; use outro prefix")
        result.add_node(mapping[v], **data)
    for u, v, data in pattern.edges(data=True):
        _merge_edge(result, mapping[u], mapping[v], data["amount"], data.get("count", 1))
    for v in pattern:
        if pattern.nodes[v].get("role") != "vitima":
            for i in rng.choice(len(existing), size=min(camouflage, len(existing)), replace=False):
                _merge_edge(result, mapping[v], existing[i], round(float(rng.lognormal(4.0, 1.0)), 2), 1)
    return result


def fraud_nodes(graph: nx.Graph) -> list:
    """Vértices cujo ``role`` é um papel de fraude (laranja, intermediário ou coletor)."""
    return [v for v, role in graph.nodes(data="role") if role in FRAUD_ROLES]


def _merge_edge(graph: nx.DiGraph, u, v, amount: float, count: int) -> None:
    if graph.has_edge(u, v):
        graph[u][v]["amount"] = graph[u][v].get("amount", 0.0) + amount
        graph[u][v]["count"] = graph[u][v].get("count", 0) + count
    else:
        graph.add_edge(u, v, amount=amount, count=count)
