"""Testes de `pixfraud.online`: dinheiro recuperado calculado à mão e pontos de corte."""

import pandas as pd
import pytest

from pixfraud.online import (
    checkpoint_flags,
    exposure_times,
    first_flags,
    recovered_amount,
    relevant_checkpoints,
)
from pixfraud.simulation import SimulationConfig, generate_dataset

T0 = pd.Timestamp("2026-01-01 10:00")
FRAUD = {"laranja", "coletora"}


def _tx(rows):
    return pd.DataFrame(
        [(T0 + pd.Timedelta(h), s, r, a, f) for h, s, r, a, f in rows],
        columns=["timestamp", "sender", "receiver", "amount", "is_fraud"],
    )


# vítima paga 100 à laranja às 10h; a laranja repassa 95 à coletora às 11h (fica com 5)
CHAIN = _tx([
    ("0h", "vitima", "laranja", 100.0, True),
    ("1h", "laranja", "coletora", 95.0, True),
    ("2h", "pessoa", "loja", 30.0, False),
])


def _recovered(freeze: dict, cashout="24h"):
    freeze_at = pd.Series({k: T0 + pd.Timedelta(v) for k, v in freeze.items()}, dtype="datetime64[ns]")
    return recovered_amount(CHAIN, FRAUD, freeze_at, cashout=cashout)


@pytest.mark.parametrize("freeze, expected", [
    ({}, 0.0),                           # ninguém bloqueado: tudo se perde
    ({"laranja": "0h"}, 100.0),          # bloqueada antes do golpe chegar: retém tudo
    ({"laranja": "30min"}, 100.0),       # bloqueada antes de repassar
    ({"laranja": "2h"}, 5.0),            # depois do repasse: só a comissão
    ({"coletora": "3h"}, 95.0),          # coletora bloqueada a tempo
    ({"coletora": "30h"}, 0.0),          # mais de 24 h depois: já foi sacado
    ({"laranja": "2h", "coletora": "3h"}, 100.0),
])
def test_recovered_amount(freeze, expected):
    result = _recovered(freeze)
    assert result["roubado"] == 100.0
    assert result["recuperado"] == pytest.approx(expected)


def test_blocked_mule_keeps_money_that_arrives_later():
    tx = _tx([
        ("0h", "vitima", "laranja", 100.0, True),
        ("5h", "vitima2", "laranja", 50.0, True),
        ("5h30min", "laranja", "coletora", 45.0, True),
    ])
    freeze = pd.Series({"laranja": T0 + pd.Timedelta("3h")})
    result = recovered_amount(tx, FRAUD, freeze)
    assert result["roubado"] == 150.0 and result["recuperado"] == 150.0  # o repasse das 5h30 foi barrado


def test_exposure_and_first_flags():
    exposure = exposure_times(CHAIN, FRAUD)
    assert exposure["laranja"] == T0 and exposure["coletora"] == T0 + pd.Timedelta("1h")
    flags = pd.DataFrame({
        "corte": [T0 - pd.Timedelta("6h"), T0 + pd.Timedelta("6h"), T0 + pd.Timedelta("12h")],
        "atributos": "x", "modelo": "m",
        "account_id": ["laranja", "laranja", "laranja"],
    })
    first = first_flags(flags, exposure)
    assert first["laranja"] == T0 + pd.Timedelta("6h")  # a sinalização de antes do golpe não conta
    assert pd.isna(first["coletora"])


def test_relevant_checkpoints_skip_quiet_periods():
    exposure = pd.Series({"a": pd.Timestamp("2026-01-01 03:00"), "b": pd.Timestamp("2026-01-20 03:00")})
    checkpoints = relevant_checkpoints(exposure, freq="6h", horizon="12h")
    assert checkpoints.min() == pd.Timestamp("2026-01-01 06:00")
    assert pd.Timestamp("2026-01-10 00:00") not in checkpoints
    assert len(checkpoints) == 4  # 6h e 12h depois de cada exposição


def test_checkpoint_flags_budget():
    accounts, tx = generate_dataset(SimulationConfig(n_people=150, n_merchants=8, n_days=4, n_rings=2,
                                                     victims_per_ring=5))
    config = {"atributos": {"betweenness_k": 50},
              "modelos": {"isolation_forest": {"n_estimators": 30}, "dbscan": {"min_samples": 5}}}
    checkpoints = pd.date_range("2026-01-02", periods=2, freq="1D")
    flags = checkpoint_flags(accounts, tx, config, checkpoints, k=7, feature_sets={"grafo": ["in_degree", "pagerank"]})
    assert set(flags["modelo"]) == {"isolation_forest", "dbscan"}
    assert (flags.groupby(["corte", "modelo"]).size() == 7).all()
    # só entram contas que já tinham feito ou recebido Pix antes do corte
    first_seen = pd.concat([
        tx[["sender", "timestamp"]].rename(columns={"sender": "c"}),
        tx[["receiver", "timestamp"]].rename(columns={"receiver": "c"}),
    ]).groupby("c")["timestamp"].min()
    assert (first_seen.loc[flags["account_id"]].to_numpy() < flags["corte"].to_numpy()).all()
