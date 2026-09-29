"""Testes de `pixfraud.simulation`: reprodutibilidade, rótulos e parâmetros de realismo."""

from dataclasses import replace
from pathlib import Path

import pandas as pd
import pytest

from pixfraud.simulation import (
    FRAUD_HOURS,
    FRAUD_ROLES,
    SimulationConfig,
    _after_activity,
    generate_dataset,
    load_config,
    with_overrides,
)

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


def test_dataset_without_rings_has_only_legit_accounts():
    accounts, transactions = generate_dataset(SimulationConfig(n_people=100, n_merchants=5, n_days=3, n_rings=0))
    assert not accounts["is_fraud"].any()
    assert (transactions["scenario"] == "normal").all()


def test_repository_config_is_valid():
    cfg = load_config(Path(__file__).parents[1] / "configs" / "experimento.yaml")
    assert cfg.n_people > 0


def test_with_overrides_validates_names():
    assert with_overrides(SMALL, {"n_rings": 0}).n_rings == 0
    assert SMALL.n_rings == 2
    with pytest.raises(ValueError, match="desconhecidos"):
        with_overrides(SMALL, {"n_pessoas": 3})
    with pytest.raises(ValueError, match="fraud_hours"):
        with_overrides(SMALL, {"fraud_hours": "madrugada"})


def test_commercial_hours_remove_the_night_signal():
    night = {}
    for hours in FRAUD_HOURS:
        _, tx = generate_dataset(replace(SMALL, victims_per_ring=100, fraud_hours=hours))
        scams = tx[tx["scenario"].isin(["falso_suporte", "clonagem_whatsapp"])]
        night[hours] = (scams["timestamp"].dt.hour < 6).mean()
    # uniforme: 6 de 24 horas (25%); comercial: o perfil legítimo (~3%)
    assert night["uniforme"] > 0.15
    assert night["comercial"] < 0.10


def test_commercial_hours_also_apply_to_slow_forwards():
    cfg = replace(SMALL, victims_per_ring=100, forward_delay_min=360)
    night = {}
    for hours in FRAUD_HOURS:
        _, tx = generate_dataset(replace(cfg, fraud_hours=hours))
        forwards = tx[tx["scenario"].isin(["repasse_laranja", "lavagem_em_cadeia"])]
        night[hours] = (forwards["timestamp"].dt.hour < 6).mean()
    assert night["uniforme"] > 0.15
    assert night["comercial"] < 0.10


def test_activity_clock():
    for t in [0.0, 3 * 3600 + 120, 12 * 3600, 5 * 86400 + 23.5 * 3600]:
        assert _after_activity(t, 0) == pytest.approx(t)
        assert _after_activity(t, 86400) == pytest.approx(t + 86400)  # um dia de atividade = um dia
    # 6 h de atividade a partir das 22h só terminam na manhã seguinte
    assert 30 * 3600 < _after_activity(22 * 3600, 6 * 3600) < 36 * 3600


@pytest.mark.parametrize("p_new, young", [(0.0, False), (1.0, True)])
def test_fraud_account_age_follows_parameter(p_new, young):
    accounts, _ = generate_dataset(replace(SMALL, p_new_fraud_account=p_new))
    age = accounts.loc[accounts["is_fraud"], "account_age_days"]
    assert (age < 60).all() if young else (age >= 30).all()


def test_quiet_people_send_fewer_pix():
    def share_almost_inactive(cfg):
        accounts, tx = generate_dataset(cfg)
        people = accounts.loc[accounts["role"] == "normal", "account_id"]
        return (tx.groupby("sender").size().reindex(people, fill_value=0) <= 1).mean()

    assert share_almost_inactive(replace(SMALL, quiet_fraction=0.5)) > share_almost_inactive(SMALL) + 0.2


def test_collector_cashout_off_by_default_keeps_dataset(dataset):
    _, tx = dataset
    assert "saida_coletor" not in set(tx["scenario"])
    _, same = generate_dataset(replace(SMALL, collector_cashout=0))
    pd.testing.assert_frame_equal(same, tx)


def test_collector_cashout_empties_the_collector():
    accounts, tx = generate_dataset(replace(SMALL, collector_cashout=10))
    collectors = set(accounts.loc[accounts["role"] == "coletor", "account_id"])
    out = tx[tx["scenario"] == "saida_coletor"]
    assert set(out["sender"]) == collectors
    assert out["is_fraud"].all()
    for collector in collectors:
        received = tx.loc[(tx["receiver"] == collector) & tx["is_fraud"], "amount"].sum()
        sent = out.loc[out["sender"] == collector]
        assert 0.8 * received < sent["amount"].sum() < received
        # a saída vem depois de todo o dinheiro da quadrilha ter chegado
        last_in = tx.loc[(tx["receiver"] == collector) & tx["is_fraud"], "timestamp"].max()
        assert (sent["timestamp"] >= last_in).all()
