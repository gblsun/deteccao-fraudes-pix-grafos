"""O que todos os modelos compartilham: o formato da saída e a preparação dos atributos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


@dataclass
class Detection:
    """Resultado de um detector: um escore contínuo e um rótulo binário por conta.

    Os escores servem para ordenar as contas (AP, precision@k, grafo de calor); a
    escala depende do modelo, então só a ordem é comparável entre detectores.
    """

    scores: pd.Series  # quanto maior, mais anômala a conta
    is_anomaly: pd.Series  # rótulo binário atribuído pelo modelo


def prepare_matrix(features: pd.DataFrame) -> np.ndarray:
    """Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza cada coluna."""
    values = features.to_numpy(dtype=float)
    negativas = features.columns[(values < 0).any(axis=0)]
    if len(negativas):  # log1p de valor negativo vira NaN, e o erro só apareceria lá na frente
        raise ValueError(f"atributos com valores negativos não são aceitos: {list(negativas)}")
    return StandardScaler().fit_transform(np.log1p(values))


def top_fraction(scores: np.ndarray, fraction: float) -> np.ndarray:
    """Rótulo binário dos detectores que só dão escore: a fração ``fraction`` de maior escore."""
    return scores > np.quantile(scores, 1.0 - fraction)


def detection(scores, is_anomaly, index) -> Detection:
    """Monta um ``Detection`` a partir de arrays alinhados com ``index``."""
    return Detection(
        scores=pd.Series(np.asarray(scores, dtype=float), index=index, name="score"),
        is_anomaly=pd.Series(np.asarray(is_anomaly, dtype=bool), index=index, name="is_anomaly"),
    )
