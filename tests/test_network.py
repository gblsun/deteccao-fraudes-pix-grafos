"""Testes de `pixfraud.network`: lei de potência, componente gigante e passeios aleatórios."""

from dataclasses import replace

import networkx as nx
import numpy as np
import pytest

from pixfraud.graph import build_graph, graph_from_edges
from pixfraud.network import (
    compare_network_models,
    component_summary,
    degree_sequence,
    fit_power_law,
    giant_component,
    random_walk,
    random_walk_visits,
)
from pixfraud.simulation import SimulationConfig, generate_dataset


def test_degree_sequence_counts_distinct_partners():
    graph = graph_from_edges([("a", "b"), ("b", "a"), ("a", "c"), ("a", "c")])
    assert sorted(degree_sequence(graph, "total")) == [1, 1, 2]
    assert sorted(degree_sequence(graph, "out")) == [0, 1, 2]
    with pytest.raises(ValueError):
        degree_sequence(graph, "lado")


def test_power_law_fit_recovers_exponent():
    rng = np.random.default_rng(0)
    # amostra contínua de Pareto com alpha = 2,5, arredondada para graus inteiros
    degrees = np.floor(5 * (1 - rng.random(20000)) ** (-1 / 1.5)).astype(int)
    fit = fit_power_law(degrees)  # escolhe k_min: a aproximação discreta tem viés com k_min pequeno
    assert fit["alpha"] == pytest.approx(2.5, abs=0.1)
    assert fit["ks"] < 0.02
    assert fit_power_law(degrees, k_min=5)["k_min"] == 5


def test_barabasi_albert_is_more_heavy_tailed_than_erdos_renyi():
    ba = fit_power_law(degree_sequence(nx.barabasi_albert_graph(3000, 3, seed=1)))
    er = fit_power_law(degree_sequence(nx.gnm_random_graph(3000, 9000, seed=1)))
    assert 2 < ba["alpha"] < 3.5
    assert er["alpha"] > ba["alpha"]  # a cauda do ER cai rápido: expoente "aparente" grande


def test_giant_component_weak_and_strong():
    graph = graph_from_edges([("a", "b"), ("b", "c"), ("c", "a"), ("c", "d"), ("x", "y")])
    graph.add_node("solo")
    assert giant_component(graph) == {"a", "b", "c", "d"}
    assert giant_component(graph, strong=True) == {"a", "b", "c"}
    summary = component_summary(graph)
    assert summary["isolados"] == 1
    assert summary["gigante_fraca"] == pytest.approx(4 / 7)
    assert summary["gigante_forte"] == pytest.approx(3 / 7)


def test_random_walk_follows_money_until_a_sink():
    graph = graph_from_edges([("v", "l", 100), ("l", "c", 95), ("v", "loja", 1e-9)])
    path = random_walk(graph, "v", rng=0)
    assert path == ["v", "l", "c"]  # a aresta de valor ~0 quase nunca é escolhida
    assert random_walk(graph, "c") == ["c"]
    assert len(random_walk(graph_from_edges([("a", "b"), ("b", "a")]), "a", max_steps=5)) == 6


def test_walks_from_victims_end_at_collectors():
    cfg = SimulationConfig(n_people=300, n_merchants=10, n_days=5, n_rings=2, victims_per_ring=10,
                           camouflage_tx=0)
    accounts, tx = generate_dataset(cfg)
    graph = build_graph(tx, accounts["account_id"])
    victims = accounts.loc[accounts["is_victim"], "account_id"]
    collectors = set(accounts.loc[accounts["role"] == "coletor", "account_id"])
    table = random_walk_visits(graph, victims, walks_per_start=10, seed=0)
    assert set(table["destino"].head(2).index) == collectors
    assert table["destino"].sum() == pytest.approx(1.0)
    # quando a coletora esvazia o dinheiro, ela deixa de ser o fim do passeio e vira passagem
    accounts, tx = generate_dataset(replace(cfg, collector_payouts=10))
    graph = build_graph(tx, accounts["account_id"])
    victims = accounts.loc[accounts["is_victim"], "account_id"]
    collectors = list(accounts.loc[accounts["role"] == "coletor", "account_id"])
    table = random_walk_visits(graph, victims, walks_per_start=10, seed=0)
    assert table.loc[collectors, "destino"].sum() < 0.05
    assert table.loc[collectors, "visitas"].sum() > 0.3


def test_compare_network_models():
    graph = nx.barabasi_albert_graph(500, 2, seed=0)
    table = compare_network_models(graph, distance_sample=50)
    assert list(table.index) == ["rede analisada", "Erdős–Rényi", "Barabási–Albert"]
    assert table.loc["Erdős–Rényi", "arestas"] == graph.number_of_edges()
    assert table.loc["rede analisada", "gigante"] == 1.0
