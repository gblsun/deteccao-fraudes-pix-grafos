"""Testes de `pixfraud.stats`: efeito, correções, bootstrap, testes pareados, modelo nulo, Kruskal-Wallis,
Dunn, Friedman e testes contra o acaso."""

import networkx as nx
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from pixfraud.stats import (
    bootstrap_metric,
    cliffs_delta,
    compare_groups,
    compare_runs,
    contingency_test,
    dunn_posthoc,
    effect_size_label,
    friedman_models,
    holm_correction,
    kruskal_groups,
    null_model_test,
    paired_comparison,
    permutation_test_metric,
    summarize_runs,
    topk_hypergeom,
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


def test_compare_runs_between_models():
    rng = np.random.default_rng(4)
    rows = []
    for seed in range(1, 11):
        base = rng.uniform(0.3, 0.5)
        for modelo, value in [("dbscan", base), ("ecod", base - 0.15), ("autoencoder", base + rng.normal(0, 0.02))]:
            rows.append({"semente": seed, "atributos": "completo", "modelo": modelo, "ap": value})
    runs = pd.DataFrame(rows)
    pairs = [("ecod", "dbscan"), ("autoencoder", "dbscan"), ("graphsage", "dbscan")]  # graphsage não rodou
    table = compare_runs(runs, pairs, ["ap"], between="modelo").set_index("comparação")
    assert list(table.index) == ["ecod - dbscan", "autoencoder - dbscan"]  # o par ausente é pulado
    assert (table["atributos"] == "completo").all()
    assert table.loc["ecod - dbscan", "diferença média"] == pytest.approx(-0.15)
    assert table.loc["ecod - dbscan", "a vence em"] == 0
    assert table.loc["autoencoder - dbscan", "p Wilcoxon (Holm)"] > 0.05


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
    # 2×2: Fisher exato e razão de chances = (30 × 150) / (10 × 10)
    assert result["razão de chances"] == pytest.approx(45.0) and result["p Fisher"] < 1e-10


def _roles_sample():
    rng = np.random.default_rng(1)
    roles = pd.Series(["normal"] * 200 + ["laranja"] * 30 + ["coletor"] * 10)
    features = pd.DataFrame({
        "separa": np.r_[rng.normal(0, 1, 200), rng.normal(3, 1, 30), rng.normal(6, 1, 10)],
        "ruido": rng.normal(0, 1, 240),
    })
    return features, roles


def test_kruskal_groups_matches_scipy_and_ranks_by_effect():
    features, roles = _roles_sample()
    table = kruskal_groups(features, roles)
    expected = stats.kruskal(*[features.loc[roles == r, "separa"] for r in ("normal", "laranja", "coletor")])
    assert table.loc["separa", "H"] == pytest.approx(expected.statistic)
    assert table.loc["separa", "ε²"] == pytest.approx(expected.statistic / 239)
    assert table.index[0] == "separa" and table.loc["separa", "efeito"] == "grande"
    assert table.loc["separa", "maior mediana"] == "coletor"
    assert table.loc["ruido", "p ajustado (Holm)"] > 0.01


def test_dunn_posthoc_finds_the_pairs_that_differ():
    rng = np.random.default_rng(2)
    roles = pd.Series(["a"] * 50 + ["b"] * 50 + ["c"] * 50)
    values = pd.Series(np.r_[rng.normal(0, 1, 50), rng.normal(0, 1, 50), rng.normal(3, 1, 50)])
    table = dunn_posthoc(values, roles).set_index(["grupo a", "grupo b"])
    assert len(table) == 3
    assert table.loc[("a", "b"), "p ajustado (Holm)"] > 0.05
    assert table.loc[("a", "c"), "p ajustado (Holm)"] < 1e-6 and table.loc[("a", "c"), "postos médios a - b"] < 0


def test_friedman_models_matches_scipy_and_gives_the_critical_difference():
    rng = np.random.default_rng(3)
    rows = [{"cenario": "base", "semente": s, "modelo": m, "average_precision": base + rng.normal(0, 0.02)}
            for s in range(10) for m, base in (("bom", 0.8), ("medio", 0.5), ("ruim", 0.2), ("ruim2", 0.21))]
    runs = pd.DataFrame(rows)
    tests, ranks = friedman_models(runs, "average_precision", by=["cenario"])
    wide = runs.pivot(index="semente", columns="modelo", values="average_precision")
    expected = stats.friedmanchisquare(*(wide[c] for c in wide.columns))
    row = tests.iloc[0]
    assert row["qui-quadrado"] == pytest.approx(expected.statistic) and row["p-valor"] < 1e-4
    assert (row["k"], row["N"]) == (4, 10)
    assert row["diferença crítica"] == pytest.approx(2.569 * np.sqrt(4 * 5 / 60), abs=1e-3)  # q(0,05; k=4) de Demšar
    assert ranks["modelo"].iloc[0] == "bom" and ranks["posto médio"].iloc[0] == 1.0


def test_permutation_and_hypergeometric_tests_against_chance():
    labels = pd.Series([True] * 10 + [False] * 190)
    perfect = pd.Series(np.r_[np.ones(10), np.zeros(190)] + np.linspace(0, 0.1, 200))
    result = permutation_test_metric(labels, perfect, n_perm=199)
    assert result["estimativa"] == 1.0 and result["p permutação"] == pytest.approx(1 / 200)
    noise = pd.Series(np.random.default_rng(4).random(200))
    assert permutation_test_metric(labels, noise, n_perm=199)["p permutação"] > 0.05
    top = topk_hypergeom(labels, perfect)
    assert top["fraudes no top-k"] == 10 and top["esperado ao acaso"] == pytest.approx(0.5)
    assert top["p hipergeométrico"] == pytest.approx(stats.hypergeom.pmf(10, 200, 10, 10))
