"""Métricas de desempenho dos detectores, calculadas por conta.

* ``precision``, ``recall`` e ``f1`` avaliam o rótulo binário do modelo;
* ``roc_auc`` e ``average_precision`` avaliam a ordenação pelo escore, sem
  depender de um limiar (a segunda é mais informativa quando as fraudes são
  raras);
* ``precision_at_k``: se um analista revisar as ``k`` contas mais suspeitas,
  que fração delas é fraude? Por padrão, ``k`` é o número de fraudes reais.
"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from pixfraud.anomaly import Detection


def evaluate(y_true: pd.Series, detection: Detection, k: int | None = None) -> dict[str, float]:
    y = y_true.reindex(detection.scores.index).astype(bool)
    k = int(y.sum()) if k is None else k
    top_k = detection.scores.nlargest(k).index
    return {
        "precision": precision_score(y, detection.is_anomaly, zero_division=0),
        "recall": recall_score(y, detection.is_anomaly, zero_division=0),
        "f1": f1_score(y, detection.is_anomaly, zero_division=0),
        "roc_auc": roc_auc_score(y, detection.scores),
        "average_precision": average_precision_score(y, detection.scores),
        "precision_at_k": float(y.loc[top_k].mean()),
        "n_flagged": int(detection.is_anomaly.sum()),
    }
