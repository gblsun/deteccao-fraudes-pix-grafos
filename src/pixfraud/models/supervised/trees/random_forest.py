"""Random Forest (Breiman, 2001): muitas árvores de decisão, cada uma vendo uma amostra das contas, votam."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from pixfraud.models.supervised.cross_validation import known_fraud_out_of_fold, out_of_fold_scores


def make_random_forest(
    n_estimators: int = 300,
    max_depth: int | None = None,
    min_samples_leaf: int = 1,
    max_features: float | str = "sqrt",
    seed: int = 42,
) -> RandomForestClassifier:
    """O classificador, com as fraudes (raras) pesando mais em cada árvore (``balanced_subsample``)."""
    return RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, min_samples_leaf=min_samples_leaf,
                                  max_features=max_features, class_weight="balanced_subsample", random_state=seed,
                                  n_jobs=-1)


def random_forest_scores(features: pd.DataFrame, labels: pd.Series, seed: int = 42, folds: int = 5,
                         **params) -> pd.Series:
    """Probabilidade de fraude por Random Forest, em validação cruzada (ver ``out_of_fold_scores``).

    ``params`` vão para ``make_random_forest``: ``n_estimators``, ``max_depth``
    (profundidade máxima de cada árvore; ``None`` = sem limite),
    ``min_samples_leaf`` (contas mínimas por folha) e ``max_features`` (atributos
    sorteados a cada corte).
    """
    return out_of_fold_scores(make_random_forest(seed=seed, **params), features, labels, seed, folds)


def random_forest_known_fraud_scores(features: pd.DataFrame, known: list, seed: int = 42, folds: int = 5,
                                     **params) -> pd.Series:
    """Random Forest treinado só com as fraudes **já conhecidas** (ver ``known_fraud_out_of_fold``).

    É o par tabular de ``graphsage.sage_known_fraud_scores``, com a mesma divisão.
    """
    return known_fraud_out_of_fold(lambda: make_random_forest(seed=seed, **params), features, known, seed, folds)
