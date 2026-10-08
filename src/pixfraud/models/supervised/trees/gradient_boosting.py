"""Gradient boosting (estilo LightGBM): árvores em sequência, cada uma corrigindo o erro das anteriores."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from pixfraud.models.supervised.cross_validation import out_of_fold_scores


def make_gradient_boosting(
    max_iter: int = 300,
    learning_rate: float = 0.05,
    min_samples_leaf: int = 5,
    max_leaf_nodes: int = 31,
    l2_regularization: float = 0.0,
    seed: int = 42,
) -> HistGradientBoostingClassifier:
    """O classificador, com as classes balanceadas.

    Folhas pequenas por padrão: com ~15 fraudes no dataset, o padrão do
    scikit-learn (20 contas por folha) não isola nenhuma.
    """
    return HistGradientBoostingClassifier(max_iter=max_iter, learning_rate=learning_rate,
                                          min_samples_leaf=min_samples_leaf, max_leaf_nodes=max_leaf_nodes,
                                          l2_regularization=l2_regularization, class_weight="balanced",
                                          random_state=seed)


def gradient_boosting_scores(features: pd.DataFrame, labels: pd.Series, seed: int = 42, folds: int = 5,
                             **params) -> pd.Series:
    """Probabilidade de fraude por gradient boosting, em validação cruzada (ver ``out_of_fold_scores``).

    ``params`` vão para ``make_gradient_boosting``: ``max_iter`` (número de
    árvores), ``learning_rate`` (quanto cada árvore corrige), ``min_samples_leaf``,
    ``max_leaf_nodes`` (tamanho de cada árvore) e ``l2_regularization``.
    """
    return out_of_fold_scores(make_gradient_boosting(seed=seed, **params), features, labels, seed, folds)
