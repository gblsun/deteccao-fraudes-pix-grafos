"""Detecção ao longo do tempo: a conta foi sinalizada a tempo de bloquear o dinheiro?

No Pix, o MED (Mecanismo Especial de Devolução) só devolve o que ainda está nas
contas que receberam o dinheiro, e o bloqueio cautelar segura valores por até
72 h. Por isso não basta saber *se* uma conta fraudulenta é detectada: importa
*quando*. Aqui o detector roda em pontos de corte sucessivos (por exemplo, a
cada 6 h), vendo só os Pix feitos até ali, como aconteceria em produção.

* ``checkpoint_flags``: em cada ponto de corte, as ``k`` contas mais suspeitas
  (o que um analista revisaria);
* ``exposure_times``: quando cada conta fraudulenta recebeu dinheiro de golpe
  pela primeira vez;
* ``first_flags``: o primeiro corte, a partir dessa exposição, em que a conta
  foi sinalizada;
* ``recovered_amount``: reproduz os Pix da quadrilha bloqueando cada conta no
  instante em que foi sinalizada e mede quanto do dinheiro roubado ficou retido.
  Dinheiro parado numa conta da quadrilha por mais de ``cashout`` é
  considerado sacado (perdido).
"""

from __future__ import annotations

from collections import defaultdict, deque

import pandas as pd

from pixfraud.anomaly import DETECTORS
from pixfraud.experiment import prepare
from pixfraud.features import FEATURE_SETS


def exposure_times(transactions: pd.DataFrame, fraud_accounts) -> pd.Series:
    """Primeiro Pix fraudulento recebido por cada conta de ``fraud_accounts``."""
    fraud_tx = transactions[transactions["is_fraud"] & transactions["receiver"].isin(set(fraud_accounts))]
    return fraud_tx.groupby("receiver")["timestamp"].min().rename("exposicao")


def relevant_checkpoints(
    exposure: pd.Series,
    freq: str = "6h",
    horizon: str = "72h",
) -> pd.DatetimeIndex:
    """Pontos de corte (a cada ``freq``) em que alguma conta está até ``horizon`` depois da exposição.

    Fora desses intervalos, sinalizar uma conta fraudulenta não muda nada nas
    métricas, então não vale a pena calcular os atributos.
    """
    horizon = pd.Timedelta(horizon)
    grid = pd.date_range(exposure.min().floor(freq), exposure.max() + horizon, freq=freq)
    keep = [t for t in grid if ((exposure <= t) & (t <= exposure + horizon)).any()]
    return pd.DatetimeIndex(keep)


def checkpoint_flags(
    accounts: pd.DataFrame,
    transactions: pd.DataFrame,
    config: dict,
    checkpoints,
    k: int,
    feature_sets: dict[str, list[str]] | None = None,
    models: list[str] | None = None,
) -> pd.DataFrame:
    """As ``k`` contas mais suspeitas em cada ponto de corte, para cada conjunto de atributos e modelo.

    Em cada corte ``t``, os atributos são recalculados só com os Pix anteriores
    a ``t``, e só as contas que já apareceram entram na conta. Devolve uma
    linha por conta sinalizada: ``corte``, ``atributos``, ``modelo`` e ``account_id``.
    """
    feature_sets = feature_sets or FEATURE_SETS
    models = models or list(DETECTORS)
    rows = []
    for t in checkpoints:
        tx = transactions[transactions["timestamp"] < t]
        active = accounts[accounts["account_id"].isin(set(tx["sender"]) | set(tx["receiver"]))]
        if len(active) <= k:
            continue
        features = prepare(active, tx, config).features
        for set_name, columns in feature_sets.items():
            for model in models:
                detection = DETECTORS[model](features[columns], **config["modelos"].get(model, {}))
                for account in detection.scores.nlargest(k).index:
                    rows.append((t, set_name, model, account))
    return pd.DataFrame(rows, columns=["corte", "atributos", "modelo", "account_id"])


def first_flags(flags: pd.DataFrame, exposure: pd.Series) -> pd.Series:
    """Primeiro corte em que cada conta foi sinalizada, a partir da sua exposição (``NaT`` se nunca).

    ``flags`` são as linhas de **um** conjunto de atributos e modelo de
    ``checkpoint_flags``. Sinalizações anteriores à exposição são ignoradas:
    antes do golpe, um analista não teria o que bloquear.
    """
    merged = flags.merge(exposure.rename("exposicao"), left_on="account_id", right_index=True)
    valid = merged[merged["corte"] >= merged["exposicao"]]
    return valid.groupby("account_id")["corte"].min().reindex(exposure.index).rename("sinalizada")


def recovered_amount(
    transactions: pd.DataFrame,
    fraud_accounts,
    freeze_at: pd.Series,
    cashout: str = "24h",
) -> dict[str, float]:
    """Quanto do dinheiro roubado ficaria retido se cada conta fosse bloqueada em ``freeze_at``.

    Reproduz, em ordem, só os Pix fraudulentos (``is_fraud``). O dinheiro entra
    quando uma vítima (conta fora de ``fraud_accounts``) paga uma conta da
    quadrilha. Uma conta bloqueada não repassa mais nada: o que estava nela e
    o que chegar depois fica retido (recuperável pelo MED). Cada valor parado
    numa conta não bloqueada por mais de ``cashout`` é sacado e se perde.
    Repasses usam primeiro o dinheiro que chegou antes.
    """
    fraud_accounts = set(fraud_accounts)
    cashout = pd.Timedelta(cashout)
    freezes = sorted((t, account) for account, t in freeze_at.dropna().items())
    lots: dict = defaultdict(deque)  # conta -> [(chegada, valor)], do mais antigo ao mais novo
    frozen: set = set()
    stolen = recovered = 0.0
    next_freeze = 0

    def freeze_until(t):
        nonlocal next_freeze, recovered
        while next_freeze < len(freezes) and freezes[next_freeze][0] <= t:
            when, account = freezes[next_freeze]
            recovered += sum(value for arrival, value in lots[account] if when - arrival <= cashout)
            lots[account].clear()
            frozen.add(account)
            next_freeze += 1

    for tx in transactions[transactions["is_fraud"]].sort_values("timestamp", kind="stable").itertuples():
        freeze_until(tx.timestamp)
        if tx.sender in fraud_accounts:
            if tx.sender in frozen:
                continue
            queue = lots[tx.sender]
            while queue and tx.timestamp - queue[0][0] > cashout:
                queue.popleft()  # sacado
            amount, need = 0.0, tx.amount
            while queue and need > 1e-9:
                arrival, value = queue.popleft()
                used = min(value, need)
                amount += used
                need -= used
                if value > used:
                    queue.appendleft((arrival, value - used))
        else:
            amount = tx.amount
            stolen += amount
        if amount <= 0:
            continue
        if tx.receiver in frozen:
            recovered += amount
        elif tx.receiver in fraud_accounts:
            lots[tx.receiver].append((tx.timestamp, amount))
    freeze_until(pd.Timestamp.max)
    return {"roubado": stolen, "recuperado": recovered, "fracao_recuperada": recovered / stolen if stolen else 0.0}
