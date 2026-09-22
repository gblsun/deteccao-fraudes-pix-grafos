"""Núcleo do experimento: transações -> grafo -> atributos -> detectores -> métricas.

Usado por ``scripts/rodar_experimento.py``, ``scripts/avaliar_robustez.py``,
``scripts/avaliar_cenarios.py`` e pelo explorador interativo
(``app/explorador.py``).
"""

from __future__ import annotations

import copy
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace
from pathlib import Path

import networkx as nx
import pandas as pd
import yaml

from pixfraud.anomaly import DETECTORS, Detection
from pixfraud.evaluation import evaluate
from pixfraud.features import FEATURE_SETS, build_features
from pixfraud.graph import build_graph
from pixfraud.simulation import SimulationConfig, generate_dataset, with_overrides

# Pares (a, b) de conjuntos de atributos comparados nos estudos com várias
# sementes: "a - b" > 0 quer dizer que ``a`` foi melhor.
COMPARISONS = [
    ("grafo", "tabular"),
    ("combinado", "tabular"),
    ("grafo_avancado", "grafo"),
    ("completo", "combinado"),
    ("completo", "tabular"),
]
REPEATED_METRICS = ["average_precision", "precision_at_k", "roc_auc", "f1"]


@dataclass
class Prepared:
    graph: nx.DiGraph
    features: pd.DataFrame
    labels: pd.Series  # is_fraud por conta


def load_experiment_config(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def prepare(accounts: pd.DataFrame, transactions: pd.DataFrame, config: dict) -> Prepared:
    """Monta o grafo e calcula todos os atributos (seção ``atributos`` da configuração)."""
    graph = build_graph(transactions, accounts["account_id"])
    features = build_features(transactions, accounts, graph, **config.get("atributos", {}))
    labels = accounts.set_index("account_id")["is_fraud"].astype(bool)
    return Prepared(graph, features, labels)


def run_detectors(
    features: pd.DataFrame,
    labels: pd.Series,
    models_config: dict,
    feature_sets: dict[str, list[str]] = FEATURE_SETS,
) -> tuple[pd.DataFrame, dict[tuple[str, str], Detection]]:
    """Roda cada detector em cada conjunto de atributos.

    Devolve a tabela de métricas (uma linha por combinação) e as detecções,
    indexadas por ``(conjunto, modelo)``.
    """
    rows, detections = [], {}
    for set_name, columns in feature_sets.items():
        for model_name, detect in DETECTORS.items():
            detection = detect(features[columns], **models_config.get(model_name, {}))
            detections[(set_name, model_name)] = detection
            rows.append({"atributos": set_name, "modelo": model_name, **evaluate(labels, detection)})
    return pd.DataFrame(rows), detections


def run_seeds(
    simulation: SimulationConfig,
    config: dict,
    seeds: Iterable[int],
    feature_sets: dict[str, list[str]] = FEATURE_SETS,
) -> Iterator[tuple[int, Prepared, pd.DataFrame]]:
    """Repete o experimento com várias sementes, uma de cada vez.

    Cada semente gera um dataset sintético diferente e muda a semente do
    Isolation Forest. Produz ``(semente, preparado, métricas)``, com a coluna
    ``semente`` já incluída nas métricas.
    """
    for seed in seeds:
        accounts, transactions = generate_dataset(replace(simulation, seed=seed))
        prepared = prepare(accounts, transactions, config)
        models = copy.deepcopy(config["modelos"])
        models.setdefault("isolation_forest", {})["seed"] = seed
        metrics, _ = run_detectors(prepared.features, prepared.labels, models, feature_sets)
        yield seed, prepared, metrics.assign(semente=seed)


def load_scenarios(path: str | Path) -> dict[str, dict]:
    """Lê os cenários de ``configs/cenarios.yaml``: nome -> parâmetros da simulação a trocar.

    Os nomes dos parâmetros são validados aqui, para um erro de digitação não
    aparecer só no meio de uma execução longa.
    """
    with open(path, encoding="utf-8") as f:
        scenarios = {name: overrides or {} for name, overrides in yaml.safe_load(f).items()}
    for overrides in scenarios.values():
        with_overrides(SimulationConfig(), overrides)
    return scenarios
