"""Dar nota a cada candidato numa rede de validação e escolher o vencedor."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from pixfraud.models import DETECTORS, GRAPH_DETECTORS, SUPERVISED
from pixfraud.tuning.search_space import params_key


def model_scores(model: str, prepared, columns: list, params: dict, seed: int) -> pd.Series:
    """Escores de ``model`` numa rede preparada (``experiment.Prepared``), com ``params``."""
    if model in DETECTORS:
        return DETECTORS[model](prepared.features[columns], **params).scores
    if model in GRAPH_DETECTORS:
        return GRAPH_DETECTORS[model](prepared.graph, **params).scores
    if model in SUPERVISED:
        return SUPERVISED[model](prepared.features[columns], prepared.labels, seed=seed, **params)
    raise ValueError(f"modelo desconhecido: {model}")


def average_precision(labels: pd.Series, scores: pd.Series) -> float:
    """AP dos escores conferidos com o gabarito (``labels``), nas contas de ``scores``."""
    return float(average_precision_score(labels.reindex(scores.index).astype(bool), scores))


def score_candidates(prepared, columns: list, todo: dict[str, list[dict]], current: dict[str, dict],
                     seed: int) -> list[dict]:
    """AP de cada candidato de ``todo`` (``{modelo: [hiperparâmetros, ...]}``) numa rede de validação.

    ``current`` é a configuração atual completa de cada modelo, para marcar a
    linha ``padrao``.
    """
    rows = []
    for model, params_list in todo.items():
        for params in params_list:
            ap = average_precision(prepared.labels, model_scores(model, prepared, columns, params, seed))
            rows.append({"modelo": model, "parametros": params_key(params),
                         "padrao": params_key(params) == params_key(current[model]), "average_precision": ap})
    return rows


def choose(runs: pd.DataFrame) -> pd.DataFrame:
    """Resumo por (modelo, candidato), com a AP média e qual candidato foi escolhido.

    ``runs`` tem uma linha por (rede de validação, modelo, candidato). Vence o
    candidato de maior AP média; num empate, a configuração atual.
    """
    summary = (runs.groupby(["modelo", "parametros", "padrao"], sort=False)["average_precision"]
               .agg(media="mean", desvio="std", redes="count").reset_index())
    summary["escolhido"] = False
    for _, group in summary.groupby("modelo", sort=False):
        best = group["media"].max()
        winners = group[np.isclose(group["media"], best, rtol=0, atol=1e-12)]
        pick = winners[winners["padrao"]].index if winners["padrao"].any() else winners.index[:1]
        summary.loc[pick[0], "escolhido"] = True
    return summary


def chosen_params(summary: pd.DataFrame) -> dict[str, dict]:
    """``{modelo: hiperparâmetros escolhidos}`` a partir de ``choose``."""
    rows = summary[summary["escolhido"]]
    return {row.modelo: json.loads(row.parametros) for row in rows.itertuples()}
