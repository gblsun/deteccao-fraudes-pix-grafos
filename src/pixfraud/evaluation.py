"""Métricas de desempenho dos detectores, calculadas por conta.

* ``precision``, ``recall`` e ``f1`` avaliam o rótulo binário do modelo;
* ``roc_auc`` e ``average_precision`` avaliam a ordenação pelo escore, sem
  depender de um limiar (a segunda é mais informativa quando as fraudes são
  raras);
* ``precision_at_k``: se um analista revisar as ``k`` contas mais suspeitas,
  que fração delas é fraude? Por padrão, ``k`` é o número de fraudes reais.

``recall_by_group`` separa o acerto por grupo de contas (por exemplo, a
tipologia de lavagem do AMLworld): quais formatos cada abordagem encontra?
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

from pixfraud.models import Detection


def evaluate(y_true: pd.Series, detection: Detection, k: int | None = None) -> dict[str, float]:
    """Todas as métricas do módulo para uma detecção; ``k`` padrão = nº de fraudes reais."""
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


def ranking_metrics(y_true: pd.Series, scores: pd.Series, k: int | None = None) -> dict[str, float]:
    """As métricas que só dependem da ordenação: AP, ROC-AUC e precision@k.

    Para abordagens que dão um escore mas não um rótulo binário (propagação de
    risco, tetos supervisionados). Contas sem escore contam como escore 0.
    """
    y = y_true.astype(bool)
    s = scores.reindex(y.index).fillna(0.0)
    k = int(y.sum()) if k is None else k
    return {
        "average_precision": average_precision_score(y, s),
        "roc_auc": roc_auc_score(y, s),
        "precision_at_k": float(y.loc[s.nlargest(k).index].mean()),
    }


def recall_by_group(members: pd.DataFrame, scores: pd.Series, k: int, by: str = "typology") -> pd.DataFrame:
    """Fração das contas de cada grupo que está entre as ``k`` de maior escore.

    ``members`` tem as colunas ``account_id`` e ``by``; uma conta pode estar
    em mais de um grupo. Contas fora de ``scores`` são ignoradas.
    """
    top = set(scores.nlargest(k).index)
    present = members[members["account_id"].isin(scores.index)]
    hits = present.assign(hit=present["account_id"].isin(top))
    return hits.groupby(by)["hit"].agg(contas="size", recall_at_k="mean").reset_index()
