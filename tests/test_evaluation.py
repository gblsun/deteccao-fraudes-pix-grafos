"""Testes de `evaluation.recall_by_group` e `visualization.plot_value_matrix`."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from pixfraud.evaluation import ranking_metrics, recall_by_group  # noqa: E402
from pixfraud.visualization import (  # noqa: E402
    DIVERGING_CMAP,
    format_ci,
    format_number,
    model_label,
    plot_differences,
    plot_model_intervals,
    plot_value_matrix,
)


def test_recall_by_group():
    scores = pd.Series({"a": 0.9, "b": 0.8, "c": 0.1, "d": 0.7, "e": 0.0})
    members = pd.DataFrame({
        "account_id": ["a", "c", "b", "d", "fora"],
        "typology": ["ciclo", "ciclo", "leque", "leque", "leque"],
    })
    table = recall_by_group(members, scores, k=3).set_index("typology")
    assert table.loc["ciclo", "recall_at_k"] == pytest.approx(0.5)  # "a" está no top 3, "c" não
    assert table.loc["leque", "recall_at_k"] == 1.0 and table.loc["leque", "contas"] == 2  # "fora" é ignorada


def test_plot_value_matrix():
    matrix = pd.DataFrame([[0.5, -0.9], [np.nan, 0.0]], index=["x", "y"], columns=["c1", "c2"])
    fig, ax = plt.subplots()
    plot_value_matrix(matrix, DIVERGING_CMAP, vmin=-1, vmax=1, fmt="{:+.2f}", ax=ax)
    texts = {t.get_text(): t.get_color() for t in ax.texts}
    assert set(texts) == {"+0,50", "-0,90", "+0,00"}  # a célula vazia fica sem texto
    assert texts["-0,90"] == "#ffffff"  # célula escura, texto branco
    assert [t.get_text() for t in ax.get_yticklabels()] == ["x", "y"]
    plt.close(fig)


def test_ranking_metrics():
    labels = pd.Series([True, False, True, False, False], index=list("abcde"))
    perfect = ranking_metrics(labels, pd.Series({"a": 0.9, "c": 0.8, "b": 0.2, "d": 0.1}))  # "e" sem escore
    assert perfect == {"average_precision": 1.0, "roc_auc": 1.0, "precision_at_k": 1.0}
    worst = ranking_metrics(labels, pd.Series({"a": 0.0, "c": 0.1, "b": 0.9, "d": 0.8, "e": 0.7}))
    assert worst["precision_at_k"] == 0.0 and worst["roc_auc"] == 0.0


def test_formatters_use_decimal_comma():
    assert format_number(0.5812) == "0,58"
    assert format_ci(0.58, 0.52, 0.63) == "0,58 [0,52; 0,63]"
    assert format_ci(0.58, np.nan, np.nan) == "0,58" and format_ci(np.nan, 0, 1) == "—"
    assert model_label("one_class_svm") == "One-Class SVM" and model_label("novo_modelo") == "novo modelo"


def test_standard_result_figures():
    summary = pd.DataFrame({"mean": [0.6, 0.3, 0.9], "ic_inferior": [0.5, -0.1, 0.8], "ic_superior": [0.7, 0.5, 1.2]},
                           index=["dbscan", "ecod", "random_forest"])
    fig, (left, right) = plt.subplots(1, 2)
    plot_model_intervals(summary, left, baseline=0.01,
                         groups={"dbscan": "não supervisionado", "ecod": "não supervisionado",
                                 "random_forest": "teto"})
    assert [t.get_text() for t in left.get_yticklabels()] == ["DBSCAN", "ECOD", "Random Forest"]
    assert any(t.get_text() == "teto" for t in left.texts)
    comparisons = pd.DataFrame({
        "comparação": ["ecod - dbscan", "random_forest - dbscan"], "diferença média": [-0.3, 0.3],
        "ic_inferior": [-0.4, 0.2], "ic_superior": [-0.2, 0.4], "a vence em": [0, 10], "n": [10, 10],
        "p Wilcoxon (Holm)": [0.004, 0.2],
    })
    plot_differences(comparisons, right)
    colors = [line.get_color() for line in right.lines if line.get_marker() == "o"]
    assert colors == ["#a82f2f", "#9aa7a4"]  # só a diferença significativa (Holm < 0,05) ganha cor
    assert any("vence em 10 de 10" in t.get_text() for t in right.texts)
    plt.close(fig)
