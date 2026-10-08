"""Testes de `pixfraud.exploration`: o que o explorador interativo calcula."""

import pandas as pd
import pytest

from pixfraud.experiment import load_experiment_config
from pixfraud.exploration import (
    SUPERVISED,
    UNSUPERVISED,
    generate_network,
    network_summary,
    picker_entries,
    rank_models,
    top_k_outcome,
)
from pixfraud.graph import build_graph

CONFIG_PATH, SCENARIOS_PATH = "configs/experimento.yaml", "configs/cenarios.yaml"


def test_network_summary_counts_by_hand():
    accounts = pd.DataFrame({
        "account_id": ["v", "l", "c", "n"],
        "role": ["normal", "laranja", "coletor", "normal"],
        "is_fraud": [False, True, True, False],
        "is_victim": [True, False, False, False],
    })
    tx = pd.DataFrame({
        "sender": ["v", "l", "n"], "receiver": ["l", "c", "v"], "amount": [500.0, 480.0, 20.0],
        "is_fraud": [True, True, False],
        "timestamp": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 10:30", "2026-01-03 09:00"]),
    })
    summary = network_summary(accounts, tx, build_graph(tx, accounts["account_id"]))
    assert summary["quadrilhas"] == 1 and summary["contas_fraudulentas"] == 2 and summary["taxa_fraude"] == 0.5
    assert summary["golpes"] == 1 and summary["valor_golpes"] == 500.0  # o repasse l -> c não conta de novo
    assert summary["dias"] == 3 and summary["valor_total"] == 1000.0
    assert summary["gigante_fraca"] == 1.0 and summary["gigante_forte"] == 0.25  # o dinheiro não volta


def test_top_k_outcome_sorts_hits_misses_and_false_alarms():
    scores = pd.Series([0.9, 0.8, 0.7, 0.1], index=list("abcd"))
    labels = pd.Series([True, False, False, True], index=list("abcd"))
    assert top_k_outcome(scores, labels, k=2).to_dict() == {
        "a": "achou", "b": "alarme_falso", "c": "resto", "d": "perdeu"}


def test_rank_models_orders_each_group_by_ap_and_feeds_the_picker():
    labels = pd.Series([True, False, False, True], index=list("abcd"))
    good, bad = pd.Series([0.9, 0.1, 0.2, 0.8], index=labels.index), pd.Series([0.1, 0.9, 0.8, 0.2], index=labels.index)
    scores = {"knn": (UNSUPERVISED, bad), "pca": (UNSUPERVISED, good), "random_forest": (SUPERVISED, good)}
    table = rank_models(scores, labels)
    assert list(table["modelo"]) == ["pca", "knn", "random_forest"]  # não supervisionados primeiro, melhor AP antes
    assert list(table["posicao"]) == [1, 2, 1]
    risk, groups = picker_entries(scores, table)
    assert list(risk)[0] == "1º PCA · AP 1,00" and groups["1º Random Forest · AP 1,00"] == SUPERVISED


@pytest.mark.lento
def test_generate_network_is_reproducible_and_follows_the_scenario():
    config = load_experiment_config(CONFIG_PATH)
    first = generate_network("base", 7, config, CONFIG_PATH, SCENARIOS_PATH)
    again = generate_network("base", 7, config, CONFIG_PATH, SCENARIOS_PATH)
    assert first[1].equals(again[1])  # mesma semente, mesmos Pix
    realistic = generate_network("realista", 7, config, CONFIG_PATH, SCENARIOS_PATH)
    assert realistic[0]["is_fraud"].mean() < first[0]["is_fraud"].mean()  # o realista tem fraudes mais raras
    with pytest.raises(ValueError, match="cenário desconhecido"):
        generate_network("nao_existe", 7, config, CONFIG_PATH, SCENARIOS_PATH)
