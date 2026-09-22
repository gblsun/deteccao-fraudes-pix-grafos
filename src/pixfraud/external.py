"""Carregadores de datasets públicos de fraude e lavagem de dinheiro.

Convertem os arquivos originais para o formato do projeto (tabelas
``accounts`` e ``transactions``, as mesmas de ``pixfraud.simulation``), para
rodar o mesmo pipeline fora do gerador sintético. Isso quebra a
circularidade de avaliar os detectores só nos padrões que nós mesmos
injetamos.

Os arquivos precisam ser baixados à mão do Kaggle (exige login); veja
``data/README.md``.

* **AMLworld** (IBM; Altman et al., 2023): transações entre contas bancárias
  com rótulo de lavagem e padrões em grafo (fan-in, fan-out, ciclos,
  cadeias…). Arquivos ``HI-Small_Trans.csv``, ``LI-Small_Trans.csv`` etc.
  São grandes: use ``days`` ou ``nrows`` para recortar.
* **PaySim** (Lopez-Rojas et al., 2016): simulação de dinheiro móvel.
  Atenção: quase toda conta de origem aparece uma única vez, então a
  estrutura em grafo é fraca. Serve mais como contraste.

Nos dois casos não existe idade da conta, então ``account_age_days`` fica 0
(esse atributo tabular deixa de informar).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

TRANSACTION_COLUMNS = ["tx_id", "timestamp", "sender", "receiver", "amount", "is_fraud", "scenario"]


def load_amlworld(
    path: str | Path,
    currency: str | None = "US Dollar",
    days: int | None = None,
    nrows: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê um arquivo ``*_Trans.csv`` do AMLworld.

    * a conta é identificada por banco + número (``"{banco}_{conta}"``);
    * ``currency``: mantém só os pagamentos feitos e recebidos nessa moeda,
      para os valores serem comparáveis (``None`` mantém todos);
    * ``days``: mantém só os primeiros ``days`` dias;
    * transferências de uma conta para ela mesma são descartadas.

    Uma conta é marcada como fraudulenta se enviou ou recebeu alguma
    transação de lavagem.
    """
    raw = pd.read_csv(path, dtype=str, nrows=nrows)
    # O arquivo tem duas colunas chamadas "Account" (origem e destino): usamos a posição.
    tx = pd.DataFrame({
        "timestamp": pd.to_datetime(raw["Timestamp"], format="%Y/%m/%d %H:%M"),
        "sender": raw["From Bank"].str.strip() + "_" + raw.iloc[:, 2].str.strip(),
        "receiver": raw["To Bank"].str.strip() + "_" + raw.iloc[:, 4].str.strip(),
        "amount": raw["Amount Paid"].astype(float),
        "is_fraud": raw["Is Laundering"].astype(int).astype(bool),
        "scenario": raw["Payment Format"],
    })
    if currency is not None:
        tx = tx[(raw["Payment Currency"] == currency) & (raw["Receiving Currency"] == currency)]
    tx = tx[tx["sender"] != tx["receiver"]]
    if days is not None:
        tx = tx[tx["timestamp"] < tx["timestamp"].min().normalize() + pd.Timedelta(days=days)]
    tx = tx.assign(scenario=tx["scenario"].where(~tx["is_fraud"], "lavagem"))
    return _project_format(tx, fraud_accounts=_parties(tx[tx["is_fraud"]]), victims=set())


def load_paysim(
    path: str | Path,
    start: str = "2026-01-01",
    nrows: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê o CSV do PaySim (colunas ``step, type, amount, nameOrig, nameDest, isFraud``...).

    ``step`` é a hora da simulação, convertida em data a partir de ``start``.
    No PaySim o fraudador toma uma conta e transfere o dinheiro para outra:
    a origem de uma transação fraudulenta é a **vítima** e o destino é a
    conta **fraudulenta**.
    """
    raw = pd.read_csv(path, nrows=nrows)
    tx = pd.DataFrame({
        "timestamp": pd.Timestamp(start) + pd.to_timedelta(raw["step"], unit="h"),
        "sender": raw["nameOrig"],
        "receiver": raw["nameDest"],
        "amount": raw["amount"].astype(float),
        "is_fraud": raw["isFraud"].astype(bool),
        "scenario": raw["type"].str.lower(),
    })
    tx = tx[tx["sender"] != tx["receiver"]]
    fraud = tx[tx["is_fraud"]]
    return _project_format(tx, fraud_accounts=set(fraud["receiver"]), victims=set(fraud["sender"]))


def _parties(tx: pd.DataFrame) -> set:
    return set(tx["sender"]) | set(tx["receiver"])


def _project_format(tx: pd.DataFrame, fraud_accounts: set, victims: set) -> tuple[pd.DataFrame, pd.DataFrame]:
    tx = tx.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx.insert(0, "tx_id", [f"T{i:08d}" for i in range(len(tx))])
    ids = sorted(_parties(tx))
    accounts = pd.DataFrame({"account_id": ids})
    accounts["account_type"] = "?"
    accounts["account_age_days"] = 0
    accounts["is_fraud"] = accounts["account_id"].isin(fraud_accounts)
    accounts["is_victim"] = accounts["account_id"].isin(victims) & ~accounts["is_fraud"]
    accounts["role"] = accounts["is_fraud"].map({True: "suspeita", False: "normal"})
    accounts = accounts[["account_id", "account_type", "account_age_days", "role", "is_fraud", "is_victim"]]
    return accounts, tx[TRANSACTION_COLUMNS]
