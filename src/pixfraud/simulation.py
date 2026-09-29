"""Gerador de um dataset sintético de transações PIX com cenários de fraude.

A ideia não é reproduzir o PIX real, e sim produzir uma rede de transações com
propriedades plausíveis (valores com cauda pesada, sazonalidade ao longo do
dia, círculos de contatos e comércios que concentram pagamentos) na qual são
injetados padrões de fraude conhecidos:

* ``falso_suporte``: a vítima faz uma ou mais transferências seguidas para uma
  conta laranja, orientada por um falso atendente do banco;
* ``clonagem_whatsapp``: contatos de uma pessoa cujo WhatsApp foi clonado pagam
  a mesma conta laranja em um curto intervalo de tempo;
* ``repasse_laranja``: a conta laranja repassa rapidamente o valor recebido
  para a conta coletora da quadrilha;
* ``lavagem_em_cadeia``: o repasse passa por uma cadeia de contas
  intermediárias antes de chegar à coletora;
* ``saida_coletor`` (só com ``collector_cashout`` > 0): a coletora esvazia o
  que recebeu em vários Pix para pessoas e comércios.

Os parâmetros ficam em ``configs/experimento.yaml`` e a semente torna o dataset
reprodutível. Os valores padrão são ilustrativos e devem ser calibrados na
etapa de análise exploratória (ver ``pixfraud.bcb``).

Por padrão o gerador embute sinais "fáceis" (golpes a qualquer hora, contas
fraudulentas recém-abertas, pessoas sempre ativas). Os parâmetros
``fraud_hours``, ``p_new_fraud_account`` e ``quiet_fraction`` desligam esses
atalhos; os cenários de ``configs/cenarios.yaml`` os combinam.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

FRAUD_ROLES = ("laranja", "intermediario", "coletor")
FRAUD_HOURS = ("uniforme", "comercial")
COLUMNS = ["t", "sender", "receiver", "amount", "scenario"]

# Peso relativo de cada hora do dia (0h a 23h): pouco uso de madrugada, picos
# no almoço e no começo da noite. Valores ilustrativos.
HOUR_WEIGHTS = np.array([
    1.0, 0.6, 0.4, 0.3, 0.3, 0.5, 1.2, 2.5, 4.0, 5.0, 5.5, 6.0,
    7.0, 6.5, 5.5, 5.5, 5.5, 6.0, 6.5, 7.0, 6.5, 5.0, 3.5, 2.0,
])


@dataclass
class SimulationConfig:
    """Parâmetros da simulação (descritos em ``configs/experimento.yaml``)."""

    seed: int = 42
    start_date: str = "2026-01-01"
    n_days: int = 30
    # contas legítimas
    n_people: int = 2000
    n_merchants: int = 100
    community_size: int = 20
    tx_per_person_day: float = 0.6
    p_merchant: float = 0.4
    p_contact: float = 0.8
    amount_mu: float = 4.0
    amount_sigma: float = 1.1
    # quadrilhas
    n_rings: int = 6
    mules_per_ring: int = 4
    victims_per_ring: int = 15
    p_chain: float = 0.5
    chain_length: int = 3
    fraud_amount_shift: float = 1.5
    forward_delay_min: float = 30.0
    camouflage_tx: float = 3.0
    collector_cashout: float = 0.0  # nº médio de Pix de saída da coletora por quadrilha (0 = não esvazia)
    # realismo: estes parâmetros desligam sinais que o gerador embute por construção
    fraud_hours: str = "uniforme"   # "uniforme" ou "comercial" (golpes e repasses no perfil horário legítimo)
    p_new_fraud_account: float = 0.7  # fração das contas fraudulentas recém-abertas (< 60 dias)
    quiet_fraction: float = 0.0     # fração de pessoas legítimas pouco ativas
    quiet_activity: float = 0.1     # atividade das pessoas pouco ativas, relativa às demais

    def __post_init__(self):
        if self.fraud_hours not in FRAUD_HOURS:
            raise ValueError(f"fraud_hours deve ser um de {FRAUD_HOURS}")


def load_config(path: str | Path) -> SimulationConfig:
    """Lê a seção ``simulacao`` do arquivo YAML de experimento."""
    with open(path, encoding="utf-8") as f:
        section = yaml.safe_load(f).get("simulacao") or {}
    return with_overrides(SimulationConfig(), section)


def with_overrides(cfg: SimulationConfig, overrides: dict) -> SimulationConfig:
    """Cópia de ``cfg`` com alguns parâmetros trocados (usado pelos cenários de ``configs/cenarios.yaml``)."""
    unknown = set(overrides) - {f.name for f in fields(SimulationConfig)}
    if unknown:
        raise ValueError(f"Parâmetros desconhecidos em 'simulacao': {sorted(unknown)}")
    return replace(cfg, **overrides)


def generate_dataset(cfg: SimulationConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``."""
    rng = np.random.default_rng(cfg.seed)

    n_fraud_max = cfg.n_rings * (cfg.mules_per_ring + cfg.chain_length + 1)
    n_total = cfg.n_people + cfg.n_merchants + n_fraud_max
    # Identificadores embaralhados para que o id não revele o papel da conta.
    ids = np.array([f"C{i:06d}" for i in rng.permutation(n_total)])
    people = ids[: cfg.n_people]
    merchants = ids[cfg.n_people : cfg.n_people + cfg.n_merchants]
    fraud_pool = iter(ids[cfg.n_people + cfg.n_merchants :])
    community = rng.permutation(cfg.n_people) // cfg.community_size

    parts = [_normal_transactions(rng, cfg, people, merchants, community)]
    roles: dict[str, str] = {}
    victims: set[str] = set()
    for _ in range(cfg.n_rings):
        ring_tx, ring_roles, ring_victims = _fraud_ring(rng, cfg, people, community, fraud_pool)
        parts.append(ring_tx)
        if cfg.collector_cashout > 0:
            collector = next(a for a, r in ring_roles.items() if r == "coletor")
            parts.append(_collector_cashout(rng, cfg, ring_tx, collector, people, merchants))
        roles |= ring_roles
        victims |= ring_victims
    parts.append(_camouflage_transactions(rng, cfg, np.array(list(roles)), people, merchants))

    tx = pd.concat(parts, ignore_index=True)
    tx["timestamp"] = (pd.Timestamp(cfg.start_date) + pd.to_timedelta(tx.pop("t"), unit="s")).dt.floor("s")
    tx["amount"] = tx["amount"].clip(lower=0.01).round(2)
    tx["is_fraud"] = tx["scenario"] != "normal"
    tx = tx.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx.insert(0, "tx_id", [f"T{i:07d}" for i in range(len(tx))])
    tx = tx[["tx_id", "timestamp", "sender", "receiver", "amount", "is_fraud", "scenario"]]

    return _accounts_table(rng, people, merchants, roles, victims, cfg.p_new_fraud_account), tx


def save_dataset(accounts: pd.DataFrame, transactions: pd.DataFrame, out_dir: str | Path) -> None:
    """Grava ``accounts.csv`` e ``transactions.csv`` em ``out_dir`` (criada se não existir)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    accounts.to_csv(out / "accounts.csv", index=False)
    transactions.to_csv(out / "transactions.csv", index=False)


def load_dataset(data_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê as tabelas gravadas por ``save_dataset`` (vale também para os datasets externos)."""
    data = Path(data_dir)
    accounts = pd.read_csv(data / "accounts.csv")
    transactions = pd.read_csv(data / "transactions.csv", parse_dates=["timestamp"])
    return accounts, transactions


def _random_seconds(rng: np.random.Generator, n: int, n_days: int) -> np.ndarray:
    """Instantes (em segundos desde o início) seguindo o perfil horário ``HOUR_WEIGHTS``."""
    day = rng.integers(0, n_days, n)
    hour = rng.choice(24, size=n, p=HOUR_WEIGHTS / HOUR_WEIGHTS.sum())
    return (day * 24 + hour) * 3600.0 + rng.uniform(0, 3600, n)


# "Relógio de atividade": corre mais rápido nas horas movimentadas e mais devagar de
# madrugada (taxa = peso da hora / peso médio, então um dia inteiro vale 24 h).
_HOUR_RATE = HOUR_WEIGHTS / HOUR_WEIGHTS.mean()
_ACTIVITY_AT_HOUR = np.concatenate([[0.0], np.cumsum(_HOUR_RATE * 3600.0)])


def _after_activity(t: float, delay: float) -> float:
    """Instante em que ``delay`` segundos de atividade terão passado a partir de ``t``.

    Um repasse que levaria 6 h começando às 22h não cai às 4h: o relógio quase
    para de madrugada, e o repasse sai no meio da manhã seguinte. Em horário
    comercial, as esperas ficam um pouco mais curtas. Usado quando
    ``fraud_hours="comercial"``, para os repasses seguirem o mesmo perfil
    horário dos golpes.
    """
    day, second = divmod(t, 86400.0)
    hour = int(second // 3600)
    target = day * 86400.0 + _ACTIVITY_AT_HOUR[hour] + _HOUR_RATE[hour] * (second - 3600.0 * hour) + delay
    day, remainder = divmod(target, 86400.0)
    hour = int(np.searchsorted(_ACTIVITY_AT_HOUR, remainder, side="right")) - 1
    return day * 86400.0 + 3600.0 * hour + (remainder - _ACTIVITY_AT_HOUR[hour]) / _HOUR_RATE[hour]


def _normal_transactions(rng, cfg, people, merchants, community) -> pd.DataFrame:
    """Pagamentos a comércios e transferências P2P, em geral dentro do círculo de contatos."""
    n_people = len(people)
    activity = cfg.tx_per_person_day * rng.lognormal(0.0, 0.5, n_people)
    if cfg.quiet_fraction > 0:
        # Pessoas que quase não usam o Pix: sem elas, ter poucos Pix já parece anômalo.
        activity[rng.random(n_people) < cfg.quiet_fraction] *= cfg.quiet_activity
    sender = np.repeat(np.arange(n_people), rng.poisson(activity * cfg.n_days))
    n = sender.size

    receiver = np.empty(n, dtype=object)
    to_merchant = rng.random(n) < cfg.p_merchant
    # Popularidade tipo Zipf: poucos comércios concentram a maior parte dos pagamentos.
    popularity = 1.0 / np.arange(1, len(merchants) + 1) ** 1.1
    receiver[to_merchant] = rng.choice(merchants, size=to_merchant.sum(), p=popularity / popularity.sum())

    p2p = np.flatnonzero(~to_merchant)
    target = rng.integers(0, n_people, p2p.size)
    in_circle = rng.random(p2p.size) < cfg.p_contact
    # Sorteia um membro da mesma comunidade: as pessoas ordenadas por comunidade
    # ocupam blocos contíguos em ``order``, a partir de ``offsets[c]``.
    order = np.argsort(community, kind="stable")
    sizes = np.bincount(community)
    offsets = np.concatenate([[0], np.cumsum(sizes)[:-1]])
    c = community[sender[p2p[in_circle]]]
    target[in_circle] = order[offsets[c] + (rng.random(c.size) * sizes[c]).astype(int)]
    self_transfer = target == sender[p2p]
    target[self_transfer] = (target[self_transfer] + 1) % n_people
    receiver[p2p] = people[target]

    return pd.DataFrame({
        "t": _random_seconds(rng, n, cfg.n_days),
        "sender": people[sender],
        "receiver": receiver,
        "amount": rng.lognormal(cfg.amount_mu, cfg.amount_sigma, n),
        "scenario": "normal",
    })


def _fraud_ring(rng, cfg, people, community, fraud_pool):
    """Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora."""
    mules = [next(fraud_pool) for _ in range(cfg.mules_per_ring)]
    collector = next(fraud_pool)
    chain = [next(fraud_pool) for _ in range(cfg.chain_length)] if rng.random() < cfg.p_chain else []
    roles = {m: "laranja" for m in mules} | {a: "intermediario" for a in chain} | {collector: "coletor"}

    rows, victims = [], set()
    # A quadrilha age durante uma janela de ~2 dias escolhida ao acaso.
    ring_start = rng.integers(0, max(cfg.n_days - 2, 1)) * 86400.0
    for _ in range(cfg.victims_per_ring):
        mule = mules[rng.integers(len(mules))]
        if rng.random() < 0.5:
            scenario = "falso_suporte"
            payers = [people[rng.integers(len(people))]] * int(rng.integers(1, 4))
        else:
            scenario = "clonagem_whatsapp"
            cloned = rng.integers(len(people))
            contacts = np.flatnonzero((community == community[cloned]) & (np.arange(len(people)) != cloned))
            n_payers = min(int(rng.integers(2, 5)), contacts.size)
            payers = people[rng.choice(contacts, size=n_payers, replace=False)]
        if cfg.fraud_hours == "uniforme":
            t = ring_start + rng.uniform(0, 2 * 86400)
        else:
            t = ring_start + _random_seconds(rng, 1, 2)[0]
        for payer in payers:
            t += rng.exponential(600)
            amount = rng.lognormal(cfg.amount_mu + cfg.fraud_amount_shift, 0.6 * cfg.amount_sigma)
            rows.append((t, payer, mule, amount, scenario))
            victims.add(payer)
            rows += _launder(rng, cfg, t, amount, [mule, *chain, collector])
    return pd.DataFrame(rows, columns=COLUMNS), roles, victims


def _launder(rng, cfg, t, amount, path):
    """Repassa o valor ao longo de ``path``, retendo uma pequena comissão a cada salto."""
    scenario = "lavagem_em_cadeia" if len(path) > 2 else "repasse_laranja"
    rows = []
    for sender, receiver in zip(path[:-1], path[1:]):
        delay = rng.exponential(cfg.forward_delay_min * 60)
        t = t + delay if cfg.fraud_hours == "uniforme" else _after_activity(t, delay)
        amount *= rng.uniform(0.90, 0.99)
        rows.append((t, sender, receiver, amount, scenario))
    return rows


def _collector_cashout(rng, cfg, ring_tx, collector, people, merchants) -> pd.DataFrame:
    """A coletora esvazia o que recebeu: vários Pix de saída para pessoas e comércios.

    Sem isso a coletora é quase só um sorvedouro (recebe e não paga ninguém). Aqui
    ela repassa ~90% do recebido em ``Poisson(collector_cashout)`` Pix (pelo menos
    um), de valores desiguais, nas horas seguintes à última entrada. As arestas
    ganham o cenário ``saida_coletor``, para serem identificadas na rede.
    """
    incoming = ring_tx[ring_tx["receiver"] == collector]
    n = max(1, int(rng.poisson(cfg.collector_cashout)))
    receivers = np.where(rng.random(n) < cfg.p_merchant, rng.choice(merchants, n), rng.choice(people, n))
    amounts = incoming["amount"].sum() * rng.uniform(0.85, 0.95) * rng.dirichlet(np.ones(n))
    t = incoming["t"].max()
    rows = []
    for receiver, amount in zip(receivers, amounts):
        delay = rng.exponential(cfg.forward_delay_min * 60)
        t = t + delay if cfg.fraud_hours == "uniforme" else _after_activity(t, delay)
        rows.append((t, collector, receiver, amount, "saida_coletor"))
    return pd.DataFrame(rows, columns=COLUMNS)


def _camouflage_transactions(rng, cfg, accounts, people, merchants) -> pd.DataFrame:
    """Movimentações comuns das contas fraudulentas, para que não sejam triviais de isolar."""
    sender = np.repeat(accounts, rng.poisson(cfg.camouflage_tx, len(accounts)))
    n = sender.size
    receiver = np.where(rng.random(n) < cfg.p_merchant, rng.choice(merchants, n), rng.choice(people, n))
    return pd.DataFrame({
        "t": _random_seconds(rng, n, cfg.n_days),
        "sender": sender,
        "receiver": receiver,
        "amount": rng.lognormal(cfg.amount_mu, cfg.amount_sigma, n),
        "scenario": "normal",
    })


def _accounts_table(rng, people, merchants, roles, victims, p_new_fraud_account) -> pd.DataFrame:
    n_fraud = len(roles)
    role = np.array(["normal"] * len(people) + ["comercio"] * len(merchants) + list(roles.values()))
    # Contas usadas em fraudes tendem a ser recém-abertas; parte delas, porém,
    # são contas antigas cedidas ou invadidas, com a mesma idade das contas comuns.
    new = rng.random(n_fraud) < p_new_fraud_account
    fraud_age = np.where(new, rng.integers(1, 60, n_fraud), rng.integers(30, 3650, n_fraud))
    accounts = pd.DataFrame({
        "account_id": np.concatenate([people, merchants, np.array(list(roles), dtype=people.dtype)]),
        "account_type": np.where(role == "comercio", "PJ", "PF"),
        "account_age_days": np.concatenate([
            rng.integers(30, 3650, len(people)),
            rng.integers(180, 5000, len(merchants)),
            fraud_age,
        ]),
        "role": role,
    })
    accounts["is_fraud"] = accounts["role"].isin(FRAUD_ROLES)
    accounts["is_victim"] = accounts["account_id"].isin(victims)
    return accounts.sort_values("account_id").reset_index(drop=True)
