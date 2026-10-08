"""Isolation Forest (Liu, Ting e Zhou, 2008): a conta isolada com poucos cortes aleatórios é anômala."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

from pixfraud.models.base import Detection, detection, prepare_matrix


def isolation_forest(
    features: pd.DataFrame,
    n_estimators: int = 300,
    contamination: float | str = "auto",
    max_samples: int | float | str = "auto",
    max_features: float = 1.0,
    seed: int = 42,
) -> Detection:
    """Isolation Forest: contas isoladas com poucas partições aleatórias são anômalas.

    Cada árvore sorteia um atributo e um ponto de corte, repetidamente, até
    isolar cada conta; a conta rara precisa de poucos cortes. ``max_samples`` é
    quantas contas cada árvore vê (``"auto"`` = até 256) e ``max_features``, a
    fração de atributos sorteada por árvore.
    """
    X = prepare_matrix(features)
    model = IsolationForest(n_estimators=n_estimators, contamination=contamination, max_samples=max_samples,
                            max_features=max_features, random_state=seed).fit(X)
    return detection(-model.score_samples(X), model.predict(X) == -1, features.index)
