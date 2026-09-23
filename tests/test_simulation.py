"""Testes de `pixfraud.simulation`: reprodutibilidade, rótulos e parâmetros de realismo."""

import hashlib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pixfraud.experiment import load_scenarios
from pixfraud.simulation import (
    FRAUD_HOURS,
    FRAUD_ROLES,
    LAUNDERING_TYPOLOGIES,
    LEGIT_SCENARIOS,
    SCAM_SCENARIOS,
    SimulationConfig,
    _after_activity,
    generate_dataset,
    load_config,
    load_dataset,
    save_dataset,
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


# --- parâmetros de realismo -------------------------------------------------

ROOT = Path(__file__).parents[1]
SCENARIOS = load_scenarios(ROOT / "configs" / "cenarios.yaml")
# Impressão digital do dataset padrão (semente 42), gravada antes de existirem os
# parâmetros de realismo: com eles desligados, o gerador não pode gastar nenhum
# sorteio a mais. O fluxo de números aleatórios do NumPy pode mudar entre
# versões, então a comparação só vale na versão em que o hash foi gravado.
BASE_FINGERPRINT = ("2.5", "24a2ceb1768e9b7bf98666c40ca4617340f157c9bca3440092085b7b5fd14eb1")


def test_realism_parameters_off_keep_the_original_dataset():
    numpy_version, expected = BASE_FINGERPRINT
    if not np.__version__.startswith(numpy_version + "."):
        pytest.skip(f"hash gravado com NumPy {numpy_version}")
    accounts, transactions = generate_dataset(SimulationConfig())
    text = accounts.to_csv(index=False, lineterminator="\n") + transactions.to_csv(index=False, lineterminator="\n")
    assert hashlib.sha256(text.encode()).hexdigest() == expected


@pytest.fixture(scope="module")
def calibrated():
    return generate_dataset(with_overrides(SimulationConfig(), SCENARIOS["calibrado"]))


def test_calibrated_scenario_matches_bcb_numbers(calibrated):
    accounts, tx = calibrated
    role = accounts.set_index("account_id")["role"]
    normal = tx[(tx["scenario"] == "normal") & tx["sender"].map(role).eq("normal")]
    to_merchant = normal["receiver"].map(role).eq("comercio")
    scams = tx[tx["scenario"].isin(SCAM_SCENARIOS)]
    # docs/resultados.md, seção 3: P2P R$ 257, P2B R$ 114, golpe R$ 2.277, 49% para empresas
    assert normal.loc[~to_merchant, "amount"].mean() == pytest.approx(257, rel=0.1)
    assert normal.loc[to_merchant, "amount"].mean() == pytest.approx(114, rel=0.1)
    assert scams["amount"].mean() == pytest.approx(2277, rel=0.25)  # poucos golpes: média mais variável
    assert to_merchant.mean() == pytest.approx(0.49, abs=0.02)
    # a taxa de golpes cai de ~110x para ~10x a real (~5 a cada 100 mil Pix)
    assert 20 < len(scams) / len(tx) * 1e5 < 100


def test_look_alike_transactions_are_legitimate(calibrated):
    accounts, tx = calibrated
    role = accounts.set_index("account_id")["role"]
    look_alike = tx[tx["scenario"].isin(set(LEGIT_SCENARIOS) - {"normal"})]
    assert set(look_alike["scenario"]) == {"salario", "fornecedor", "vaquinha", "repasse_salario"}
    assert not look_alike["is_fraud"].any()
    salaries = look_alike[look_alike["scenario"] == "salario"]
    assert salaries["sender"].map(role).eq("comercio").all()
    assert (salaries["timestamp"].dt.day == 7).all()  # 5º dia útil de janeiro de 2026, sem contar feriados
    suppliers = look_alike[look_alike["scenario"] == "fornecedor"]
    assert suppliers["sender"].map(role).eq("comercio").all()
    assert suppliers["receiver"].map(role).eq("comercio").all()
    # repasse do salário em poucas horas: tempo de permanência curto numa conta legítima
    rent = look_alike[look_alike["scenario"] == "repasse_salario"]
    got_paid = salaries.groupby("receiver")["timestamp"].min()
    wait = rent["timestamp"] - rent["sender"].map(got_paid)
    assert (wait > pd.Timedelta(0)).all() and wait.median() < pd.Timedelta("12h")


def test_recruited_mules_keep_their_legit_history(calibrated):
    accounts, tx = calibrated
    mules = accounts.loc[accounts["role"] == "laranja", "account_id"]
    legit_sent = tx[~tx["is_fraud"] & tx["sender"].isin(mules)].groupby("sender").size()
    assert legit_sent.max() > 10  # uma conta cedida traz o histórico todo, não 3 Pix de camuflagem
    assert not accounts.loc[accounts["is_fraud"], "is_victim"].any()  # a laranja nunca paga o próprio golpe


def test_collectors_cash_out_to_a_merchant(calibrated):
    accounts, tx = calibrated
    role = accounts.set_index("account_id")["role"]
    cashout = tx[tx["scenario"] == "saque"]
    assert cashout["is_fraud"].all()
    assert set(cashout["sender"]) == set(accounts.loc[accounts["role"] == "coletor", "account_id"])
    assert cashout["receiver"].map(role).eq("comercio").all()


def test_contestations_come_later_and_only_for_scams(calibrated):
    _, tx = calibrated
    contested = tx[tx["contestado_em"].notna()]
    assert contested["scenario"].isin(SCAM_SCENARIOS).all()
    assert (contested["contestado_em"] > contested["timestamp"]).all()
    assert 0.3 < len(contested) / tx["scenario"].isin(SCAM_SCENARIOS).sum() < 0.9  # p_contested = 0,6
    assert "contestado_em" not in generate_dataset(SMALL)[1]  # desligado: o esquema não muda


def test_contestation_column_survives_save_and_load(tmp_path):
    accounts, tx = generate_dataset(replace(SMALL, p_contested=1.0))
    save_dataset(accounts, tx, tmp_path)
    _, loaded = load_dataset(tmp_path)
    assert pd.api.types.is_datetime64_any_dtype(loaded["contestado_em"])
    assert loaded["contestado_em"].notna().sum() == tx["contestado_em"].notna().sum()


@pytest.mark.parametrize("typology", LAUNDERING_TYPOLOGIES[1:])
def test_laundering_typologies_have_their_shape(typology):
    cfg = replace(SMALL, n_rings=1, victims_per_ring=30, laundering_typologies=[typology])
    accounts, tx = generate_dataset(cfg)
    role = accounts.set_index("account_id")["role"]
    hops = tx[tx["scenario"] == typology]
    payments = tx["scenario"].isin(SCAM_SCENARIOS).sum()
    n_inter = (accounts["role"] == "intermediario").sum()
    assert len(hops) > 0 and hops["is_fraud"].all() and n_inter >= 2
    if typology == "espalha_junta":  # cada golpe se divide entre todos os intermediários
        assert len(hops) == payments * 2 * n_inter
    elif typology == "bipartido":  # cada golpe passa por um só; no total, laranjas x intermediários
        assert len(hops) == payments * 2
        to_inter = hops[hops["receiver"].map(role) == "intermediario"]
        assert to_inter.groupby("receiver")["sender"].nunique().max() >= 2
    else:  # ciclo: o dinheiro volta para a laranja antes de ir para a coletora
        assert hops["receiver"].map(role).eq("laranja").sum() == payments
        assert hops["receiver"].map(role).eq("coletor").sum() == payments


def test_weekly_calendar_has_quieter_weekends():
    _, tx = generate_dataset(replace(SMALL, n_days=28, calendar="semanal"))
    per_day = tx.groupby(tx["timestamp"].dt.dayofweek).size()
    assert per_day[[5, 6]].mean() < per_day[[0, 1, 2, 3]].mean()


def test_invalid_realism_parameters_are_rejected():
    with pytest.raises(ValueError, match="calendar"):
        replace(SMALL, calendar="mensal")
    with pytest.raises(ValueError, match="laundering_typologies"):
        replace(SMALL, laundering_typologies=["piramide"])
    with pytest.raises(ValueError, match="p_recruited_mule"):
        replace(SMALL, p_recruited_mule=1.5)
