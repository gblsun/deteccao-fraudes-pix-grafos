from pathlib import Path

import pandas as pd
import pytest

from pixfraud.simulation import FRAUD_ROLES, SimulationConfig, generate_dataset, load_config

SMALL = SimulationConfig(n_people=200, n_merchants=10, n_days=5, n_rings=2, victims_per_ring=5)


@pytest.fixture(scope="module")
def dataset():
    return generate_dataset(SMALL)


def test_same_seed_gives_same_dataset(dataset):
    accounts, transactions = generate_dataset(SMALL)
    pd.testing.assert_frame_equal(accounts, dataset[0])
    pd.testing.assert_frame_equal(transactions, dataset[1])


def test_transactions_reference_known_accounts(dataset):
    accounts, transactions = dataset
    known = set(accounts["account_id"])
    assert accounts["account_id"].is_unique
    assert transactions["tx_id"].is_unique
    assert set(transactions["sender"]) <= known
    assert set(transactions["receiver"]) <= known


def test_no_self_transfers_and_positive_amounts(dataset):
    _, transactions = dataset
    assert (transactions["sender"] != transactions["receiver"]).all()
    assert (transactions["amount"] > 0).all()


def test_rings_have_expected_roles(dataset):
    accounts, _ = dataset
    roles = accounts["role"].value_counts()
    assert roles["laranja"] == SMALL.n_rings * SMALL.mules_per_ring
    assert roles["coletor"] == SMALL.n_rings
    assert accounts["is_fraud"].sum() == accounts["role"].isin(FRAUD_ROLES).sum()


def test_fraudulent_money_reaches_collectors(dataset):
    accounts, transactions = dataset
    collectors = set(accounts.loc[accounts["role"] == "coletor", "account_id"])
    assert collectors <= set(transactions.loc[transactions["is_fraud"], "receiver"])


def test_repository_config_is_valid():
    cfg = load_config(Path(__file__).parents[1] / "configs" / "experimento.yaml")
    assert cfg.n_people > 0
