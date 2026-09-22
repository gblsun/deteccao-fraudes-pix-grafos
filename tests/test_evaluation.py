import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from pixfraud.evaluation import recall_by_group  # noqa: E402
from pixfraud.visualization import DIVERGING_CMAP, plot_value_matrix  # noqa: E402


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
