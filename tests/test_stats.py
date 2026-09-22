"""Testes de `pixfraud.stats`: tamanho de efeito, correções, bootstrap, testes pareados e modelo nulo."""

import networkx as nx
import numpy as np
import pandas as pd
import pytest

from pixfraud.stats import (
    bootstrap_metric,
    cliffs_delta,
    compare_groups,
    compare_runs,
    contingency_test,
    effect_size_label,
    holm_correction,
    null_model_test,
    paired_comparison,
    summarize_runs,
)


def test_cliffs_delta_and_labels():
    assert cliffs_delta([5, 6, 7], [1, 2, 3]) == 1.0
    assert cliffs_delta([1, 2, 3], [1, 2, 3]) == 0.0
    assert effect_size_label(0.1) == "desprezível" and effect_size_label(-0.6) == "grande"


def test_holm_correction():
    assert holm_correction([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def test_compare_groups_finds_the_separating_feature():
    rng = np.random.default_rng(0)
    labels = pd.Series([True] * 30 + [False] * 300)
    features = pd.DataFrame({
        "separa": np.r_[rng.normal(5, 1, 30), rng.normal(0, 1, 300)],
        "ruido": rng.normal(0, 1, 330),
    })
    table = compare_groups(features, labels)
    assert table.index[0] == "separa"
    assert table.loc["separa", "efeito"] == "grande"
    assert table.loc["separa", "p ajustado (Holm)"] < 1e-10
    assert table.loc["ruido", "p ajustado (Holm)"] > 0.01


def test_bootstrap_metric_perfect_ranking():
    labels = pd.Series([True] * 5 + [False] * 50)
    scores = pd.Series(np.r_[np.ones(5), np.zeros(50)])
    result = bootstrap_metric(labels, scores, n_boot=200)
    assert result == {"estimativa": 1.0, "ic_inferior": 1.0, "ic_superior": 1.0}


def test_paired_comparison_and_summary():
    rng = np.random.default_rng(1)
    b = pd.Series(rng.uniform(0.3, 0.5, 10))
    a = b + 0.1 + rng.normal(0, 0.01, 10)
    result = paired_comparison(a, b)
    assert result["diferença média"] == pytest.approx(0.1, abs=0.02)
    assert result["ic_inferior"] > 0 and result["p Wilcoxon"] < 0.01 and result["a vence em"] == 10
    runs = pd.DataFrame({"atributos": ["x"] * 10 + ["y"] * 10, "modelo": "m", "ap": np.r_[a, b]})
    summary = summarize_runs(runs, "ap")
    assert summary.index[0] == ("x", "m") and summary["count"].tolist() == [10, 10]


def test_compare_runs_and_summary_by_scenario():
    rng = np.random.default_rng(3)
    rows = []
    for cenario, gap in [("facil", 0.2), ("dificil", 0.0)]:
        for seed in range(1, 11):
            base = rng.uniform(0.3, 0.5)
            for atributos, value in [("tabular", base), ("grafo", base + gap + rng.normal(0, 0.01))]:
                rows.append({"cenario": cenario, "semente": seed, "atributos": atributos, "modelo": "m", "ap": value})
    runs = pd.DataFrame(rows)

    table = compare_runs(runs, [("grafo", "tabular")], ["ap"], by=["cenario"]).set_index("cenario")
    assert table.loc["facil", "comparação"] == "grafo - tabular"
    assert table.loc["facil", "diferença média"] == pytest.approx(0.2, abs=0.02)
    assert table.loc["facil", "a vence em"] == 10 and table.loc["facil", "p Wilcoxon (Holm)"] < 0.01
    assert table.loc["dificil", "p Wilcoxon"] > 0.05

    summary = summarize_runs(runs, "ap", by=["cenario"])
    assert summary.index.names == ["cenario", "atributos", "modelo"]
    assert summary.index.get_level_values("cenario").unique().tolist() == ["facil", "dificil"]
    assert summary.loc["facil"].index[0] == ("grafo", "m")  # ordenado pela média dentro do cenário


def test_null_model_detects_excess_reciprocity():
    graph = nx.gnm_random_graph(60, 120, seed=2, directed=True)
    graph.add_edges_from([(v, u) for u, v in list(graph.edges())[:60]])  # muitas relações de ida e volta
    result = null_model_test(graph, nx.reciprocity, n_samples=30)
    assert result["z"] > 5 and result["p empírico"] < 0.05


def test_contingency_test():
    fraud = pd.Series([True] * 40 + [False] * 160)
    night = pd.Series([True] * 30 + [False] * 10 + [True] * 10 + [False] * 150)
    result = contingency_test(fraud, night)
    assert result["p-valor"] < 1e-6 and result["V de Cramér"] > 0.5
    assert result["tabela"].loc[True, True] == 30
