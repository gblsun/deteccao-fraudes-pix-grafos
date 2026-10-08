"""Validação cruzada dos modelos supervisionados: nenhuma conta recebe a nota de um modelo que viu o rótulo dela."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict


def out_of_fold_scores(model: ClassifierMixin, features: pd.DataFrame, labels: pd.Series, seed: int = 42,
                       folds: int = 5) -> pd.Series:
    """Probabilidade de fraude de cada conta, dada pelo modelo treinado sem ela.

    Validação cruzada estratificada: as contas são divididas em ``folds``
    partes com a mesma proporção de fraudes, e cada parte recebe a previsão do
    modelo treinado com as outras.
    """
    y = labels.reindex(features.index).astype(bool).to_numpy()
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    proba = cross_val_predict(model, features.to_numpy(dtype=float), y, cv=splitter, method="predict_proba")[:, 1]
    return pd.Series(proba, index=features.index, name="score")


def known_fraud_out_of_fold(make_model, features: pd.DataFrame, known: list, seed: int = 42,
                            folds: int = 5) -> pd.Series:
    """Treino só com as fraudes **já conhecidas**; o resto conta como "não fraude".

    As contas não rotuladas são separadas em ``folds`` dobras, e cada uma
    recebe a previsão de um modelo (``make_model()``) treinado com as fraudes
    conhecidas e as outras dobras. As contas de ``known`` recebem 1.0; avalie
    só nas demais.
    """
    X = features.to_numpy(dtype=float)
    y = features.index.isin(known)
    positives, unlabeled = np.flatnonzero(y), np.flatnonzero(~y)
    proba = np.ones(len(features))
    splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    for rest, held_out in splitter.split(unlabeled):
        train = np.concatenate([positives, unlabeled[rest]])
        model = make_model().fit(X[train], y[train])
        proba[unlabeled[held_out]] = model.predict_proba(X[unlabeled[held_out]])[:, 1]
    return pd.Series(proba, index=features.index, name="score")
