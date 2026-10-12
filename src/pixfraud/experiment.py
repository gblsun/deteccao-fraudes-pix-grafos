"""Núcleo do experimento: transações -> grafo -> atributos -> detectores -> métricas.

Usado pelos scripts de ``scripts/`` e pelo explorador interativo
(``app/explorador.py``). ``save_metadata`` grava, ao lado de cada resultado, o
que é preciso para refazê-lo (commit, configuração, sementes, versões).
"""

from __future__ import annotations

import copy
import importlib.metadata
import inspect
import json
import platform
import subprocess
from collections.abc import Iterable, Iterator
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

import networkx as nx
import pandas as pd
import yaml

from pixfraud.evaluation import evaluate
from pixfraud.features import FEATURE_SETS, build_features
from pixfraud.flow import label_spreading, propagate_risk
from pixfraud.graph import build_graph
from pixfraud.models import DETECTORS, GRAPH_DETECTORS, SUPERVISED, Detection
from pixfraud.models.supervised import random_forest_known_fraud_scores
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
# Tetos supervisionados de ``supervised_scores`` (as GNN ficam em ``pixfraud.models.supervised``, opcionais).
SUPERVISED_MODELS = tuple(SUPERVISED)


@dataclass
class Prepared:
    """Tudo o que os detectores precisam, calculado uma vez por dataset (ver ``prepare``)."""

    graph: nx.DiGraph
    features: pd.DataFrame
    labels: pd.Series  # is_fraud por conta


def load_experiment_config(path: str | Path) -> dict:
    """Lê o YAML de experimento inteiro (seções ``simulacao``, ``atributos`` e ``modelos``)."""
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
    models: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[tuple[str, str], Detection]]:
    """Roda cada detector (``models``, ou todos de ``DETECTORS``) em cada conjunto de atributos.

    Devolve a tabela de métricas (uma linha por combinação) e as detecções,
    indexadas por ``(conjunto, modelo)``.
    """
    rows, detections = [], {}
    for set_name, columns in feature_sets.items():
        for model_name in models or list(DETECTORS):
            detection = DETECTORS[model_name](features[columns], **models_config.get(model_name, {}))
            detections[(set_name, model_name)] = detection
            rows.append({"atributos": set_name, "modelo": model_name, **evaluate(labels, detection)})
    return pd.DataFrame(rows), detections


def seeded_models(models_config: dict, seed: int) -> dict:
    """Cópia da seção ``modelos`` com ``seed`` em todo detector que aceita semente.

    Assim cada repetição de um estudo muda também a aleatoriedade dos
    detectores (Isolation Forest, One-Class SVM aproximado, autoencoder), e
    não só o dataset.
    """
    models = copy.deepcopy(models_config)
    for name, detect in {**DETECTORS, **GRAPH_DETECTORS}.items():
        if "seed" in inspect.signature(detect).parameters:
            models.setdefault(name, {})["seed"] = seed
    return models


def run_seeds(
    simulation: SimulationConfig,
    config: dict,
    seeds: Iterable[int],
    feature_sets: dict[str, list[str]] = FEATURE_SETS,
    models: list[str] | None = None,
    processes: int = 1,
) -> Iterator[tuple[int, Prepared, pd.DataFrame]]:
    """Repete o experimento com várias sementes.

    Cada semente gera um dataset sintético diferente e muda a semente dos
    detectores (``seeded_models``). Produz ``(semente, preparado, métricas)``,
    com a coluna ``semente`` já incluída nas métricas, sempre na ordem das
    sementes. Com ``processes`` > 1, as sementes rodam em paralelo: o
    resultado é o mesmo, mais rápido, e a memória cresce com o nº de processos.
    """
    if processes <= 1:
        for seed in seeds:
            yield _run_one_seed(simulation, config, seed, feature_sets, models)
        return
    # Cada semente é independente: roda em processos separados, na ordem das sementes.
    with ProcessPoolExecutor(max_workers=processes) as pool:
        futures = [pool.submit(_run_one_seed, simulation, config, seed, feature_sets, models) for seed in seeds]
        for future in futures:
            yield future.result()


def _run_one_seed(simulation, config, seed, feature_sets, models):
    accounts, transactions = generate_dataset(replace(simulation, seed=seed))
    prepared = prepare(accounts, transactions, config)
    metrics, _ = run_detectors(prepared.features, prepared.labels, seeded_models(config["modelos"], seed),
                               feature_sets, models)
    return seed, prepared, metrics.assign(semente=seed)


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


def feature_ablation(
    features: pd.DataFrame,
    labels: pd.Series,
    columns: list[str],
    models_config: dict,
    models: list[str] | None = None,
) -> pd.DataFrame:
    """Quanto cada atributo contribui: a average precision cai quando ele sai?

    Para cada detector, roda uma vez com todos os ``columns`` e depois tirando
    um atributo de cada vez. ``queda`` > 0 quer dizer que o atributo ajudava;
    < 0, que ele atrapalhava (ruído para aquele detector).
    """
    rows = []
    for model in models or list(DETECTORS):
        detect, params = DETECTORS[model], models_config.get(model, {})
        full = evaluate(labels, detect(features[columns], **params))["average_precision"]
        for column in columns:
            rest = [c for c in columns if c != column]
            ap = evaluate(labels, detect(features[rest], **params))["average_precision"]
            rows.append({"modelo": model, "atributo": column, "ap_sem": ap, "ap_com_todos": full, "queda": full - ap})
    return pd.DataFrame(rows)


def supervised_scores(
    features: pd.DataFrame,
    labels: pd.Series,
    seed: int = 42,
    folds: int = 5,
    model: str = "random_forest",
    **params,
) -> pd.Series:
    """Probabilidade de fraude de cada conta dada por um modelo que **viu os rótulos**.

    Serve de teto para os detectores não supervisionados: com validação
    cruzada estratificada, cada conta recebe o escore de um modelo treinado
    sem ela. Numa situação real esses rótulos não existiriam (ou seriam
    poucos), então a distância até este teto mostra quanto se perde por não
    tê-los. ``model``: um nome de ``pixfraud.models.SUPERVISED``
    (``random_forest`` ou ``gradient_boosting``); ``params`` são os
    hiperparâmetros dele (a seção ``modelos`` da configuração).
    """
    if model not in SUPERVISED:
        raise ValueError(f"modelo supervisionado desconhecido: {model} (use um de {SUPERVISED_MODELS})")
    return SUPERVISED[model](features, labels, seed=seed, folds=folds, **params)


def known_fraud_scores(features: pd.DataFrame, known: list, seed: int = 42, folds: int = 5, **params) -> pd.Series:
    """Random Forest treinado só com as fraudes **já conhecidas**; o resto conta como "não fraude".

    É o par tabular de ``pixfraud.gnn.sage_known_fraud_scores``, com a mesma
    divisão (ver ``models.supervised.random_forest.random_forest_known_fraud_scores``).
    """
    return random_forest_known_fraud_scores(features, known, seed=seed, folds=folds, **params)


# Todos os modelos da vitrine (``scripts/03_modelos/avaliar_modelos.py`` e o explorador da rede),
# agrupados por família, na ordem em que aparecem nas figuras.
MODEL_FAMILIES = {
    "não supervisionado": list(DETECTORS),
    "estrutura do grafo": [*GRAPH_DETECTORS, "dominant"],
    "semi-supervisionado": ["propagacao_relativa", "label_spreading", "combinado", "label_spreading_combinado"],
    "teto supervisionado": [*SUPERVISED_MODELS, "graphsage"],
}
FAMILY_OF = {model: family for family, models in MODEL_FAMILIES.items() for model in models}
MODEL_ORDER = [model for models in MODEL_FAMILIES.values() for model in models]


def all_model_scores(
    prepared: Prepared,
    models: dict,
    columns: list[str],
    known: list,
    known_legit: list,
    seed: int = 42,
    use_gnn: bool = False,
    reference: str = "dbscan",
    rank_index: pd.Index | None = None,
) -> dict[str, pd.Series]:
    """O escore de cada modelo da vitrine (``MODEL_FAMILIES``) num mesmo dataset.

    ``models`` é a seção ``modelos`` da configuração (já com a semente, ver
    ``seeded_models``); ``columns``, os atributos dos modelos que usam a tabela.
    Os semi-supervisionados partem das fraudes ``known`` e das legítimas
    ``known_legit``; os combinados são a média dos percentis com ``reference``,
    calculados entre as contas de ``rank_index`` (padrão: todas). Os tetos
    supervisionados usam os rótulos em validação cruzada. A GNN só entra com
    ``use_gnn``.
    """
    table = prepared.features[columns]
    scores = {m: detect(table, **models.get(m, {})).scores for m, detect in DETECTORS.items()}
    scores |= {m: detect(prepared.graph, **models.get(m, {})).scores for m, detect in GRAPH_DETECTORS.items()}
    scores["propagacao_relativa"] = propagate_risk(prepared.graph, known, relative=True)
    scores["label_spreading"] = label_spreading(prepared.graph, known, known_legit)
    index = prepared.labels.index if rank_index is None else rank_index

    def percentile(model):
        return scores[model].reindex(index).rank(pct=True)

    scores["combinado"] = (percentile("propagacao_relativa") + percentile(reference)) / 2
    scores["label_spreading_combinado"] = (percentile("label_spreading") + percentile(reference)) / 2
    for model in SUPERVISED_MODELS:
        scores[model] = supervised_scores(table, prepared.labels, seed=seed, model=model, **models.get(model, {}))
    if use_gnn:
        from pixfraud import gnn

        scores["dominant"] = gnn.dominant_scores(prepared.graph, table, seed=seed)
        scores["graphsage"] = gnn.graphsage_scores(prepared.graph, table, prepared.labels, seed=seed)
    return scores


def save_metadata(path: str | Path, config: dict | None = None, **extra) -> Path:
    """Grava um ``*_meta.json`` com o que é preciso para refazer um resultado.

    Guarda a data, o commit do git (e se havia alterações não commitadas, caso
    em que o resultado pode não corresponder exatamente ao commit), a versão do
    Python e dos pacotes principais e a configuração usada. ``extra`` acrescenta
    o que for específico de cada script: sementes, cenários, duração...
    """
    commit = _git("rev-parse", "HEAD")
    meta = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "commit": commit,
        "alteracoes_nao_commitadas": bool(_git("status", "--porcelain")) if commit else None,
        "python": platform.python_version(),
        "pacotes": {name: importlib.metadata.version(name)
                    for name in ("numpy", "pandas", "networkx", "scikit-learn", "scipy")},
        "configuracao": config,
        **extra,
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def _git(*args: str) -> str | None:
    """Saída de um comando do git no repositório do pacote, ou ``None`` se o git não estiver disponível."""
    try:
        done = subprocess.run(["git", *args], capture_output=True, text=True, check=True,
                              cwd=Path(__file__).resolve().parent)
    except (OSError, subprocess.CalledProcessError):
        return None
    return done.stdout.strip()
