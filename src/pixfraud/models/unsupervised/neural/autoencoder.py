"""Autoencoder: uma rede neural que aprendeu a reconstruir as contas típicas erra ao reconstruir esta."""

from __future__ import annotations

import warnings

import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor

from pixfraud.models.base import Detection, detection, prepare_matrix, top_fraction


def autoencoder(
    features: pd.DataFrame,
    max_iter: int = 300,
    contamination: float = 0.05,
    bottleneck: float = 1 / 3,
    alpha: float = 1e-3,
    seed: int = 42,
) -> Detection:
    """Autoencoder: a conta que a rede não consegue reconstruir é anômala.

    Uma rede neural pequena (``MLPRegressor`` do scikit-learn) aprende a
    devolver a própria entrada passando por uma camada estreita, com a fração
    ``bottleneck`` do número de atributos (padrão: um terço). Como a maioria
    das contas é legítima, ela aprende o que é típico; o escore é o erro médio
    de reconstrução de cada conta. ``alpha`` é a regularização L2 dos pesos.
    Para de treinar quando o erro de validação deixa de cair.
    """
    X = prepare_matrix(features)
    n_features = X.shape[1]
    narrow = max(1, int(round(n_features * bottleneck, 6)))
    hidden = max(narrow + 1, (n_features + 1) // 2)
    model = MLPRegressor(hidden_layer_sizes=(hidden, narrow, hidden), alpha=alpha, max_iter=max_iter,
                         early_stopping=len(X) >= 50, n_iter_no_change=10, random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(X, X)
    reconstruction = model.predict(X).reshape(X.shape)
    scores = ((reconstruction - X) ** 2).mean(axis=1)
    return detection(scores, top_fraction(scores, contamination), features.index)
