"""ECOD (Li et al., 2022): a conta está na cauda de vários atributos ao mesmo tempo."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from scipy.stats import rankdata, skew

from pixfraud.models.base import Detection, detection, prepare_matrix, top_fraction


def ecod(features: pd.DataFrame, contamination: float = 0.05) -> Detection:
    """ECOD: probabilidade de cauda empírica, atributo por atributo (Li et al., 2022).

    Para cada atributo, a função de distribuição empírica diz quão rara é a
    conta pela esquerda e pela direita; o escore soma ``-log`` dessas
    probabilidades em todos os atributos. Faz isso três vezes (cauda esquerda,
    direita e a indicada pela assimetria de cada atributo) e fica com a maior.
    Não tem parâmetro para ajustar e é muito rápido, mas ignora a relação entre
    atributos: uma conta comum em cada atributo e rara na combinação passa.
    O rótulo binário marca a fração ``contamination`` de maior escore.
    """
    X = prepare_matrix(features)
    n = len(X)
    left = rankdata(X, method="max", axis=0) / n  # P(X <= x)
    right = (n - rankdata(X, method="min", axis=0) + 1) / n  # P(X >= x)
    tail_left, tail_right = -np.log(left), -np.log(right)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # atributo constante: assimetria indefinida
        skewness = np.nan_to_num(skew(X, axis=0))
    tail_auto = np.where(skewness < 0, tail_left, tail_right)
    scores = np.max([tail_left.sum(axis=1), tail_right.sum(axis=1), tail_auto.sum(axis=1)], axis=0)
    return detection(scores, top_fraction(scores, contamination), features.index)
