"""One-Class SVM (Schölkopf et al., 2001): uma fronteira que envolve a maior parte das contas."""

from __future__ import annotations

import pandas as pd
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import SGDOneClassSVM
from sklearn.svm import OneClassSVM

from pixfraud.models.base import Detection, detection, prepare_matrix


def one_class_svm(
    features: pd.DataFrame,
    nu: float = 0.05,
    gamma: float | str = "scale",
    max_exact: int = 5_000,
    n_components: int = 300,
    seed: int = 42,
) -> Detection:
    """One-Class SVM: uma fronteira (núcleo RBF) que envolve a maior parte das contas.

    ``nu`` é, aproximadamente, a fração de contas deixadas do lado de fora
    (anômalas). O SVM exato custa entre o quadrado e o cubo do número de
    contas; acima de ``max_exact``, o núcleo é aproximado (Nyström, com
    ``n_components`` pontos) e o SVM é treinado por gradiente estocástico,
    com custo linear. O escore é a distância para dentro da fronteira, com o
    sinal trocado: quanto maior, mais para fora.
    """
    X = prepare_matrix(features)
    if len(X) <= max_exact:
        model = OneClassSVM(nu=nu, gamma=gamma).fit(X)
        Z = X
    else:
        if gamma == "scale":  # a mesma regra do scikit-learn para o núcleo exato
            gamma = 1.0 / (X.shape[1] * (X.var() or 1.0))
        Z = Nystroem(gamma=gamma, n_components=min(n_components, len(X)), random_state=seed).fit_transform(X)
        model = SGDOneClassSVM(nu=nu, random_state=seed).fit(Z)
    scores = -model.decision_function(Z)
    return detection(scores, model.predict(Z) == -1, features.index)
