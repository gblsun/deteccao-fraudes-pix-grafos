"""Grafos temporais: caminhos que respeitam a ordem cronológica dos Pix.

No grafo agregado, "existe caminho de A até B" não garante que o dinheiro de A
possa ter chegado a B: os Pix do caminho precisam acontecer em ordem. Aqui as
funções trabalham direto sobre a tabela de transações (colunas ``sender``,
``receiver``, ``amount`` e ``timestamp``).
"""

from __future__ import annotations

import networkx as nx
import pandas as pd

from pixfraud.graph import build_graph

DIRECTIONS = ("forward", "backward")


def temporal_reachability(
    transactions: pd.DataFrame,
    account,
    direction: str = "forward",
    start: pd.Timestamp | str | None = None,
    end: pd.Timestamp | str | None = None,
) -> pd.Series:
    """Contas ligadas a ``account`` por caminhos temporais.

    * ``direction="forward"`` (*earliest arrival*): para onde o dinheiro de
      ``account``, disponível a partir de ``start``, pode ter chegado. O valor
      de cada conta é o primeiro instante em que o dinheiro pode chegar a ela.
    * ``direction="backward"`` (*latest departure*): de onde pode ter vindo o
      dinheiro que estava em ``account`` até ``end``. O valor de cada conta é o
      último instante em que ela ainda pode enviar dinheiro que chegue a
      ``account`` a tempo.

    Uma única passada pelos Pix em ordem cronológica (ou inversa) resolve o
    problema: O(m log m) por causa da ordenação.
    """
    _check_direction(direction)
    tx = transactions[["sender", "receiver", "timestamp"]]
    if direction == "forward":
        best = {account: pd.Timestamp(start) if start is not None else pd.Timestamp.min}
        for u, v, t in tx.sort_values("timestamp", kind="stable").itertuples(index=False):
            if u in best and t >= best[u] and t < best.get(v, pd.Timestamp.max):
                best[v] = t
    else:
        best = {account: pd.Timestamp(end) if end is not None else pd.Timestamp.max}
        for u, v, t in tx.sort_values("timestamp", ascending=False, kind="stable").itertuples(index=False):
            if v in best and t <= best[v] and t > best.get(u, pd.Timestamp.min):
                best[u] = t
    best.pop(account)
    return pd.Series(best, name="first_arrival" if direction == "forward" else "last_departure").sort_values()


def temporal_trail_transactions(
    transactions: pd.DataFrame,
    account,
    direction: str = "forward",
    max_hops: int | None = None,
    max_delay: pd.Timedelta | str | None = None,
    start: pd.Timestamp | str | None = None,
    end: pd.Timestamp | str | None = None,
) -> pd.DataFrame:
    """Os Pix que formam caminhos temporais a partir de ``account`` (ou até ela).

    Além da ordem cronológica, dá para limitar o número de saltos
    (``max_hops``) e o tempo máximo que o dinheiro fica parado em cada conta
    intermediária (``max_delay``, ex.: ``"2h"``). Isso é útil para seguir
    repasses rápidos, típicos de contas laranja.
    """
    _check_direction(direction)
    delay = pd.Timedelta(max_delay) if max_delay is not None else None
    hops_limit = max_hops if max_hops is not None else float("inf")
    forward = direction == "forward"
    ordered = transactions.sort_values("timestamp", ascending=forward, kind="stable")

    # Para cada conta alcançada: lista de (instante, saltos) em que o dinheiro
    # chega a ela (forward) ou precisa sair dela (backward).
    origin = pd.Timestamp(start if forward else end) if (start if forward else end) is not None else None
    events: dict = {account: [(origin, 0)]}
    used = []
    for row in ordered.itertuples():
        here, there = (row.sender, row.receiver) if forward else (row.receiver, row.sender)
        if here not in events:
            continue
        t = row.timestamp
        hops = _best_hops(events[here], t, forward, delay, is_origin=here == account)
        if hops is None or hops >= hops_limit:
            continue
        used.append(row.Index)
        events.setdefault(there, []).append((t, hops + 1))
    return transactions.loc[used].sort_values("timestamp")


def temporal_trail(transactions: pd.DataFrame, account, **kwargs) -> nx.DiGraph:
    """Grafo (agregado) dos Pix de ``temporal_trail_transactions``; aceita os mesmos parâmetros."""
    return build_graph(temporal_trail_transactions(transactions, account, **kwargs))


def dwell_time(transactions: pd.DataFrame) -> pd.Series:
    """Tempo de permanência do dinheiro, em minutos, por conta.

    Para cada Pix recebido, mede quanto tempo a conta leva até fazer o próximo
    Pix de saída; o resultado é a mediana dessas esperas. Contas laranja
    repassam em minutos; pessoas comuns, em horas ou dias. Contas que nunca
    enviam depois de receber ficam de fora do resultado.
    """
    incoming = transactions[["receiver", "timestamp"]].rename(columns={"receiver": "account"})
    outgoing = transactions[["sender", "timestamp"]].rename(columns={"sender": "account", "timestamp": "out_time"})
    merged = pd.merge_asof(
        incoming.sort_values("timestamp"),
        outgoing.sort_values("out_time"),
        left_on="timestamp",
        right_on="out_time",
        by="account",
        direction="forward",
    )
    minutes = (merged["out_time"] - merged["timestamp"]).dt.total_seconds() / 60
    return minutes.groupby(merged["account"]).median().dropna().rename("dwell_time_min")


def windowed_in_degree(transactions: pd.DataFrame, freq: str = "1D") -> pd.DataFrame:
    """Grau de entrada por janela de tempo: linhas = janelas, colunas = contas.

    Cada célula é o número de pagadores distintos da conta naquela janela
    (``freq`` no formato do pandas: ``"1D"``, ``"6h"``, ``"7D"``...).
    """
    window = transactions["timestamp"].dt.floor(freq)
    counts = transactions.groupby([window, "receiver"])["sender"].nunique()
    return counts.unstack(fill_value=0)


def temporal_features(transactions: pd.DataFrame, accounts: pd.DataFrame, freq: str = "1D") -> pd.DataFrame:
    """Atributos temporais por conta: ``dwell_time_min`` e ``max_daily_in_degree``.

    Contas que nunca repassam recebem como tempo de permanência a duração
    total do período, o maior valor possível.
    """
    span = (transactions["timestamp"].max() - transactions["timestamp"].min()).total_seconds() / 60
    windows = windowed_in_degree(transactions, freq)
    df = pd.DataFrame(index=pd.Index(accounts["account_id"], name="account_id"))
    df["dwell_time_min"] = dwell_time(transactions).reindex(df.index).fillna(span)
    df["max_daily_in_degree"] = windows.max().reindex(df.index).fillna(0)
    return df


def _best_hops(events, t, forward, delay, is_origin):
    """Menor nº de saltos entre os eventos compatíveis com um Pix no instante ``t``."""
    best = None
    for when, hops in events:
        if when is not None:
            gap = (t - when) if forward else (when - t)
            if gap < pd.Timedelta(0):
                continue
            if delay is not None and not is_origin and gap > delay:
                continue
        if best is None or hops < best:
            best = hops
    return best


def _check_direction(direction: str) -> None:
    if direction not in DIRECTIONS:
        raise ValueError(f"direction deve ser um de {DIRECTIONS}")
