"""Carregadores de datasets públicos de fraude e lavagem de dinheiro.

Convertem os arquivos originais para o formato do projeto (tabelas
``accounts`` e ``transactions``, as mesmas de ``pixfraud.simulation``), para
rodar o mesmo pipeline fora do gerador sintético. Isso quebra a
circularidade de avaliar os detectores só nos padrões que nós mesmos
injetamos.

Os arquivos vêm do Kaggle (exige login ou o token da API); veja
``data/README.md``.

* **AMLworld** (IBM; Altman et al., 2023): transações entre contas bancárias
  com rótulo de lavagem e padrões em grafo (fan-in, fan-out, ciclos,
  cadeias…). Arquivos ``HI-Small_Trans.csv``, ``LI-Small_Trans.csv`` etc.
  São grandes: use ``days`` ou ``nrows`` para recortar. ``formats`` mantém só
  as formas de pagamento parecidas com o Pix, ``load_amlworld_patterns`` lê a
  tipologia de cada tentativa de lavagem (``*_Patterns.txt``) e
  ``time_windows`` divide o período em janelas, usadas como repetições.
* **PaySim** (Lopez-Rojas et al., 2016): simulação de dinheiro móvel.
  Atenção: quase toda conta de origem aparece uma única vez, então a
  estrutura em grafo é fraca. Serve mais como contraste.

Nos dois casos não existe idade da conta, então ``account_age_days`` fica 0
(esse atributo tabular deixa de informar).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from pathlib import Path

import pandas as pd

TRANSACTION_COLUMNS = ["tx_id", "timestamp", "sender", "receiver", "amount", "is_fraud", "scenario"]
# Formas de pagamento do AMLworld mais parecidas com o Pix: transferências
# eletrônicas entre contas (sem cheque, cartão, dinheiro vivo ou bitcoin).
PIX_LIKE_FORMATS = ("ACH", "Wire")
_ATTEMPT = re.compile(r"^BEGIN LAUNDERING ATTEMPT\s*-\s*([A-Za-z\- ]+?)\s*(?::|$)")


def load_amlworld(
    path: str | Path,
    currency: str | None = "US Dollar",
    days: int | None = None,
    nrows: int | None = None,
    formats: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê um arquivo ``*_Trans.csv`` do AMLworld.

    * a conta é identificada por banco + número (``"{banco}_{conta}"``);
    * ``currency``: mantém só os pagamentos feitos e recebidos nessa moeda,
      para os valores serem comparáveis (``None`` mantém todos);
    * ``formats``: mantém só essas formas de pagamento, por exemplo
      ``PIX_LIKE_FORMATS`` (``None`` mantém todas);
    * ``days``: mantém só os primeiros ``days`` dias;
    * transferências de uma conta para ela mesma são descartadas.

    Uma conta é marcada como fraudulenta se enviou ou recebeu alguma
    transação de lavagem.
    """
    # Lido em blocos, filtrando cada um: o HI-Small tem ~5 milhões de linhas e,
    # inteiro como texto, ocuparia alguns GB de memória.
    parts = [
        _amlworld_chunk(raw, currency, formats)
        for raw in pd.read_csv(path, dtype=str, nrows=nrows, chunksize=500_000)
    ]
    tx = pd.concat(parts, ignore_index=True)
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


def load_amlworld_patterns(path: str | Path) -> pd.DataFrame:
    """Lê o ``*_Patterns.txt`` do AMLworld: as transações de cada tentativa de lavagem.

    O arquivo tem blocos ``BEGIN LAUNDERING ATTEMPT - <TIPO>: ...`` e
    ``END LAUNDERING ATTEMPT - <TIPO>``, com as transações no mesmo formato do
    ``*_Trans.csv``. Devolve uma linha por transação, com o número da tentativa
    e a tipologia (``fan_in``, ``fan_out``, ``cycle``, ``gather_scatter``,
    ``scatter_gather``, ``stack``, ``bipartite``, ``random``...).
    """
    rows, attempt, typology = [], 0, None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = _ATTEMPT.match(line)
            if match:
                attempt += 1
                typology = match.group(1).strip().lower().replace("-", "_").replace(" ", "_")
            elif line.startswith("END LAUNDERING ATTEMPT"):
                typology = None
            elif typology is not None and line:
                fields = [field.strip() for field in line.split(",")]
                rows.append((attempt, typology, fields[0], _account_id(fields[1], fields[2]),
                             _account_id(fields[3], fields[4]), float(fields[7])))
    patterns = pd.DataFrame(rows, columns=["attempt", "typology", "timestamp", "sender", "receiver", "amount"])
    patterns["timestamp"] = pd.to_datetime(patterns["timestamp"], format="%Y/%m/%d %H:%M")
    return patterns


def pattern_accounts(patterns: pd.DataFrame) -> pd.DataFrame:
    """Contas de cada tipologia (``account_id``, ``typology``); uma conta pode estar em várias."""
    members = pd.concat([
        patterns[["sender", "typology"]].rename(columns={"sender": "account_id"}),
        patterns[["receiver", "typology"]].rename(columns={"receiver": "account_id"}),
    ])
    return members.drop_duplicates().sort_values(["typology", "account_id"]).reset_index(drop=True)


def time_windows(transactions: pd.DataFrame, days: int) -> Iterator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame]]:
    """Divide as transações em janelas consecutivas de ``days`` dias.

    Gera ``(início, accounts, transactions)`` para cada janela com transações.
    Os rótulos são refeitos dentro da janela: uma conta é suspeita se enviou ou
    recebeu alguma transação de lavagem **naquela janela** (sem vítimas, como
    no AMLworld). Janelas diferentes servem de repetições, no lugar das
    sementes do gerador.
    """
    step = pd.Timedelta(days=days)
    start, end = transactions["timestamp"].min().normalize(), transactions["timestamp"].max()
    while start <= end:
        tx = transactions[(transactions["timestamp"] >= start) & (transactions["timestamp"] < start + step)]
        if len(tx):
            tx = tx.reset_index(drop=True)
            yield start, _accounts_table(tx, _parties(tx[tx["is_fraud"]]), victims=set()), tx
        start += step


def _amlworld_chunk(raw: pd.DataFrame, currency: str | None, formats: Iterable[str] | None) -> pd.DataFrame:
    """Converte um bloco do ``*_Trans.csv``, já filtrado por moeda e forma de pagamento."""
    keep = pd.Series(True, index=raw.index)
    if currency is not None:
        keep &= (raw["Payment Currency"] == currency) & (raw["Receiving Currency"] == currency)
    if formats is not None:
        keep &= raw["Payment Format"].isin(list(formats))
    raw = raw[keep]
    # O arquivo tem duas colunas chamadas "Account" (origem e destino): usamos a posição.
    return pd.DataFrame({
        "timestamp": pd.to_datetime(raw["Timestamp"], format="%Y/%m/%d %H:%M"),
        "sender": _account(raw["From Bank"], raw.iloc[:, 2]),
        "receiver": _account(raw["To Bank"], raw.iloc[:, 4]),
        "amount": raw["Amount Paid"].astype(float),
        "is_fraud": raw["Is Laundering"].astype(int).astype(bool),
        "scenario": raw["Payment Format"],
    })


def _account(bank: pd.Series, number: pd.Series) -> pd.Series:
    """``"{banco}_{conta}"``, com o código do banco sem zeros à esquerda (igual nos dois arquivos)."""
    bank = bank.str.strip().str.lstrip("0").replace("", "0")
    return bank + "_" + number.str.strip()


def _account_id(bank: str, number: str) -> str:
    return f"{bank.lstrip('0') or '0'}_{number}"


def _parties(tx: pd.DataFrame) -> set:
    return set(tx["sender"]) | set(tx["receiver"])


def _project_format(tx: pd.DataFrame, fraud_accounts: set, victims: set) -> tuple[pd.DataFrame, pd.DataFrame]:
    tx = tx.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx.insert(0, "tx_id", [f"T{i:08d}" for i in range(len(tx))])
    return _accounts_table(tx, fraud_accounts, victims), tx[TRANSACTION_COLUMNS]


def _accounts_table(tx: pd.DataFrame, fraud_accounts: set, victims: set) -> pd.DataFrame:
    ids = sorted(_parties(tx))
    accounts = pd.DataFrame({"account_id": ids})
    accounts["account_type"] = "?"
    accounts["account_age_days"] = 0
    accounts["is_fraud"] = accounts["account_id"].isin(fraud_accounts)
    accounts["is_victim"] = accounts["account_id"].isin(victims) & ~accounts["is_fraud"]
    accounts["role"] = accounts["is_fraud"].map({True: "suspeita", False: "normal"})
    return accounts[["account_id", "account_type", "account_age_days", "role", "is_fraud", "is_victim"]]
