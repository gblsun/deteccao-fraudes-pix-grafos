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
* ``espalha_junta``, ``ciclo`` e ``bipartido``: outras formas de lavagem,
  inspiradas nas tipologias do AMLworld (ver ``laundering_typologies``);
* ``saque``: a coletora tira o dinheiro para uma corretora (``collector_cashout``);
* ``saida_coletor``: a coletora esvazia o que recebeu em vários Pix para
  pessoas e comércios (``collector_payouts``).

Os parâmetros ficam em ``configs/experimento.yaml`` e a semente torna o dataset
reprodutível. Os valores padrão são ilustrativos; o cenário ``calibrado`` de
``configs/cenarios.yaml`` usa os números do BCB (ver ``pixfraud.bcb``).

Por padrão o gerador embute sinais "fáceis" (golpes a qualquer hora, contas
fraudulentas recém-abertas, pessoas sempre ativas, só a fraude repassa
dinheiro). Os parâmetros de realismo desligam esses atalhos e **não gastam
nenhum sorteio quando estão desligados**: com os valores padrão, a mesma
semente produz exatamente o mesmo dataset de antes de eles existirem.

Com ``estrutura_aleatoria``, as contagens também são sorteadas a cada semente
(``draw_structure``): nº de quadrilhas, laranjas, vítimas e intermediários de
cada uma, como cada coletora tira o dinheiro, nº de comércios e quanto eles
pagam de salários e fornecedores. ``audit_roles`` confere, conta por conta, que
o papel gravado em ``accounts`` corresponde ao que a conta fez nas transações.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

FRAUD_ROLES = ("laranja", "intermediario", "coletor")
FRAUD_HOURS = ("uniforme", "comercial")
CALENDARS = ("uniforme", "semanal")
LAUNDERING_TYPOLOGIES = ("cadeia", "espalha_junta", "ciclo", "bipartido")
SCAM_SCENARIOS = ("falso_suporte", "clonagem_whatsapp")
# Repasses dentro da quadrilha (laranja -> ... -> coletora) e a saída do dinheiro dela.
LAUNDERING_SCENARIOS = ("repasse_laranja", "lavagem_em_cadeia", "ciclo", "espalha_junta", "bipartido")
EXIT_SCENARIOS = ("saque", "saida_coletor")
# Pix legítimos; todo o resto (golpes, repasses da quadrilha, saques) é fraude.
LEGIT_SCENARIOS = ("normal", "salario", "fornecedor", "vaquinha", "repasse_salario")
COLUMNS = ["t", "sender", "receiver", "amount", "scenario"]

# Peso relativo de cada hora do dia (0h a 23h): pouco uso de madrugada, picos
# no almoço e no começo da noite. Valores ilustrativos.
HOUR_WEIGHTS = np.array([
    1.0, 0.6, 0.4, 0.3, 0.3, 0.5, 1.2, 2.5, 4.0, 5.0, 5.5, 6.0,
    7.0, 6.5, 5.5, 5.5, 5.5, 6.0, 6.5, 7.0, 6.5, 5.0, 3.5, 2.0,
])
# Calendário "semanal": peso de cada dia da semana (segunda a domingo) e o
# aumento nos primeiros dias do mês, quando caem os salários. Ilustrativos.
WEEKDAY_WEIGHTS = np.array([1.0, 1.0, 1.0, 1.0, 1.1, 0.85, 0.65])
MONTH_START_BOOST = 1.25


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
    # realismo: estes parâmetros desligam sinais que o gerador embute por construção
    fraud_hours: str = "uniforme"   # "uniforme" ou "comercial" (golpes e repasses no perfil horário legítimo)
    p_new_fraud_account: float = 0.7  # fração das contas fraudulentas recém-abertas (< 60 dias)
    quiet_fraction: float = 0.0     # fração de pessoas legítimas pouco ativas
    quiet_activity: float = 0.1     # atividade das pessoas pouco ativas, relativa às demais
    # calibração com o BCB (None = mesmo valor dos Pix entre pessoas)
    merchant_amount_mu: float | None = None
    merchant_amount_sigma: float | None = None
    calendar: str = "uniforme"      # "uniforme" ou "semanal" (dia da semana e começo do mês)
    # negativos difíceis: contas legítimas que se comportam como partes de uma quadrilha
    employees_per_merchant: float = 0.0  # funcionários pagos por Pix, em média, por comércio
    salary_business_day: int = 5         # dia útil do mês em que caem os salários
    supplier_tx_per_week: float = 0.0    # pagamentos semanais de cada comércio a fornecedores
    p_organizer: float = 0.0             # fração de pessoas que organizam "vaquinhas"
    p_fast_forwarder: float = 0.0        # fração de pessoas que repassam o salário em poucas horas
    # quadrilhas mais realistas
    p_recruited_mule: float = 0.0        # fração das laranjas que são pessoas com histórico legítimo
    collector_cashout: bool = False      # a coletora tira o dinheiro para uma corretora
    cashout_delay_min: float = 180.0     # tempo médio (min) até cada saque da coletora
    collector_payouts: float = 0.0       # nº médio de Pix da coletora para pessoas e comércios, por quadrilha
    laundering_typologies: tuple[str, ...] = ("cadeia",)  # sorteadas por quadrilha
    p_contested: float = 0.0             # fração dos golpes contestados (coluna contestado_em)
    contest_delay_h: float = 48.0        # atraso mediano da contestação
    # estrutura sorteada por semente (ver draw_structure); desligada, não gasta sorteio nenhum
    estrutura_aleatoria: bool = False

    def __post_init__(self):
        if self.fraud_hours not in FRAUD_HOURS:
            raise ValueError(f"fraud_hours deve ser um de {FRAUD_HOURS}")
        if self.calendar not in CALENDARS:
            raise ValueError(f"calendar deve ser um de {CALENDARS}")
        if isinstance(self.laundering_typologies, str):
            self.laundering_typologies = (self.laundering_typologies,)
        self.laundering_typologies = tuple(self.laundering_typologies)
        unknown = set(self.laundering_typologies) - set(LAUNDERING_TYPOLOGIES)
        if unknown or not self.laundering_typologies:
            raise ValueError(f"laundering_typologies deve conter apenas {LAUNDERING_TYPOLOGIES}")
        for name in ("p_merchant", "p_contact", "p_chain", "p_new_fraud_account", "quiet_fraction",
                     "p_organizer", "p_fast_forwarder", "p_recruited_mule", "p_contested"):
            if not 0.0 <= getattr(self, name) <= 1.0:
                raise ValueError(f"{name} deve estar entre 0 e 1")
        if self.collector_cashout and self.collector_payouts > 0:
            raise ValueError("collector_cashout e collector_payouts são alternativas: a coletora saca "
                             "para uma corretora ou espalha o dinheiro, não os dois")


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


# Faixas do sorteio de ``estrutura_aleatoria``. Os números são ilustrativos, mas
# seguem o que se sabe do problema: quadrilhas de tamanho muito desigual (poucas
# grandes, muitas pequenas, daí a binomial negativa), 3% a 7% das contas sendo
# empresas e empresas que pagam folha e fornecedores (o BCB registra Pix de
# empresa para pessoa e de empresa para empresa), em vez de só receber.
MERCHANT_SHARE = (0.03, 0.07)
EMPLOYEES_PER_MERCHANT = (2.0, 6.0)
SUPPLIER_TX_PER_WEEK = (0.5, 2.0)
DISPERSION = 1.5           # binomial negativa: quanto menor, mais desiguais as quadrilhas
COLLECTOR_EXITS = {"acumula": 0.3, "saque": 0.4, "espalha": 0.3}  # o que a coletora faz com o dinheiro
COLLECTOR_PAYOUTS = (5, 30)  # nº médio de Pix de saída quando a coletora espalha o dinheiro


def draw_structure(cfg: SimulationConfig) -> tuple[SimulationConfig, list[SimulationConfig]]:
    """A configuração geral e a de cada quadrilha.

    Sem ``estrutura_aleatoria``, é a própria ``cfg`` repetida ``n_rings`` vezes
    (nenhum sorteio, o dataset não muda). Com ela, um gerador próprio
    (``default_rng([seed, 1])``, separado do que gera as transações) sorteia:

    * nº de quadrilhas: ``1 + Poisson(n_rings - 1)``, então ``n_rings`` vira a média;
    * por quadrilha: laranjas (``1 +`` binomial negativa com média
      ``mules_per_ring - 1``), vítimas (binomial negativa com média
      ``victims_per_ring``), intermediários (Poisson com média ``chain_length``,
      de 1 a 6), a fração de laranjas recrutadas entre pessoas com histórico
      (Beta(2, 3), média 40%) e o que a coletora faz (``COLLECTOR_EXITS``);
    * comércios: ``MERCHANT_SHARE`` das pessoas, que pagam salários e
      fornecedores (se a ``cfg`` não fixou esses valores), em vez de só receber.

    O papel de cada conta já é sorteado em ``generate_dataset`` (os ids são
    embaralhados); aqui muda o tamanho de cada papel.
    """
    if not cfg.estrutura_aleatoria:
        return cfg, [cfg] * cfg.n_rings
    rng = np.random.default_rng([cfg.seed, 1])
    n_rings = 1 + int(rng.poisson(max(cfg.n_rings - 1, 0)))
    base = replace(
        cfg,
        n_rings=n_rings,
        n_merchants=max(2, round(cfg.n_people * rng.uniform(*MERCHANT_SHARE))),
        employees_per_merchant=cfg.employees_per_merchant or float(rng.uniform(*EMPLOYEES_PER_MERCHANT)),
        supplier_tx_per_week=cfg.supplier_tx_per_week or float(rng.uniform(*SUPPLIER_TX_PER_WEEK)),
    )
    # as tipologias além da cadeia precisam de pelo menos 2 intermediários
    min_chain = 1 if cfg.laundering_typologies == ("cadeia",) else 2
    rings = []
    for _ in range(n_rings):
        exit_ = rng.choice(list(COLLECTOR_EXITS), p=list(COLLECTOR_EXITS.values()))
        mules = 1 + _negative_binomial(rng, max(cfg.mules_per_ring - 1, 0.5))
        rings.append(replace(
            base,
            mules_per_ring=mules,
            # toda laranja recebe ao menos um golpe (ver _fraud_ring)
            victims_per_ring=max(mules, _negative_binomial(rng, cfg.victims_per_ring)),
            chain_length=int(np.clip(rng.poisson(cfg.chain_length), min_chain, 6)),
            p_recruited_mule=float(rng.beta(2, 3)),
            collector_cashout=bool(exit_ == "saque"),
            collector_payouts=float(rng.integers(*COLLECTOR_PAYOUTS)) if exit_ == "espalha" else 0.0,
        ))
    return base, rings


def structure_summary(cfg: SimulationConfig) -> dict:
    """O que ``draw_structure`` sorteou, para gravar junto com o dataset (``dataset_meta.json``)."""
    base, rings = draw_structure(cfg)
    return {
        "estrutura_aleatoria": cfg.estrutura_aleatoria,
        "n_comercios": base.n_merchants,
        "funcionarios_por_comercio": round(base.employees_per_merchant, 2),
        "fornecedores_por_semana": round(base.supplier_tx_per_week, 2),
        "quadrilhas": [{"laranjas": r.mules_per_ring, "vitimas": r.victims_per_ring, "cadeia": r.chain_length,
                        "laranjas_recrutadas": round(r.p_recruited_mule, 2),
                        "coletora": "saque" if r.collector_cashout else "espalha" if r.collector_payouts else "acumula"}
                       for r in rings],
    }


def _negative_binomial(rng, mean: float, dispersion: float = DISPERSION) -> int:
    """Contagem com média ``mean`` e cauda longa (variância ``mean + mean²/dispersion``)."""
    return int(rng.negative_binomial(dispersion, dispersion / (dispersion + mean)))


def _chain_slots(cfg: SimulationConfig) -> int:
    return cfg.chain_length if cfg.laundering_typologies == ("cadeia",) else max(cfg.chain_length, 2)


def generate_dataset(cfg: SimulationConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera as tabelas ``accounts`` (uma linha por conta) e ``transactions``."""
    cfg, rings = draw_structure(cfg)
    rng = np.random.default_rng(cfg.seed)

    n_fraud_max = sum(r.mules_per_ring + _chain_slots(r) + 1 for r in rings)
    n_total = cfg.n_people + cfg.n_merchants + n_fraud_max
    # Identificadores embaralhados para que o id não revele o papel da conta.
    ids = np.array([f"C{i:06d}" for i in rng.permutation(n_total)])
    people = ids[: cfg.n_people]
    merchants = ids[cfg.n_people : cfg.n_people + cfg.n_merchants]
    fraud_pool = iter(ids[cfg.n_people + cfg.n_merchants :])
    community = rng.permutation(cfg.n_people) // cfg.community_size
    day_p = _day_weights(cfg)

    parts = [_normal_transactions(rng, cfg, people, merchants, community, day_p)]
    roles: dict[str, str] = {}
    victims: set[str] = set()
    recruited: set[str] = set()  # pessoas (com histórico) que viraram laranjas
    for ring_cfg in rings:
        ring_tx, ring_roles, ring_victims = _fraud_ring(rng, ring_cfg, people, merchants, community, fraud_pool,
                                                        recruited, day_p,
                                                        victims if cfg.estrutura_aleatoria else frozenset())
        parts.append(ring_tx)
        if ring_cfg.collector_payouts > 0:
            collector = next(a for a, r in ring_roles.items() if r == "coletor")
            parts.append(_collector_payouts(rng, ring_cfg, ring_tx, collector, people, merchants))
        roles |= ring_roles
        victims |= ring_victims
    created = np.array([a for a in roles if a not in recruited], dtype=people.dtype)
    parts.append(_camouflage_transactions(rng, cfg, created, people, merchants, day_p))
    if _has_look_alikes(cfg):
        parts.append(_look_alike_transactions(rng, cfg, people, merchants, community, day_p))

    tx = pd.concat(parts, ignore_index=True)
    tx["timestamp"] = (pd.Timestamp(cfg.start_date) + pd.to_timedelta(tx.pop("t"), unit="s")).dt.floor("s")
    tx["amount"] = tx["amount"].clip(lower=0.01).round(2)
    tx["is_fraud"] = ~tx["scenario"].isin(LEGIT_SCENARIOS)
    tx = tx.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx.insert(0, "tx_id", [f"T{i:07d}" for i in range(len(tx))])
    tx = tx[["tx_id", "timestamp", "sender", "receiver", "amount", "is_fraud", "scenario"]]

    accounts = _accounts_table(rng, people, merchants, roles, victims, cfg.p_new_fraud_account)
    if cfg.p_contested > 0:
        tx = _contestations(rng, cfg, tx)
    return accounts, tx


def audit_roles(accounts: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    """Contas cujo comportamento nas transações não bate com o papel gravado em ``accounts``.

    Devolve uma linha por violação (``account_id``, ``role``, ``regra``); vazia
    quando todo papel confere. As regras dizem o que cada papel **faz**:

    * ``comercio``: é PJ; só paga salário ou fornecedor; não aplica nem repassa golpe;
    * ``laranja``: recebe golpe de vítimas e repassa para a quadrilha;
    * ``intermediario``: recebe repasse da quadrilha e repassa adiante, sem
      receber golpe direto de vítima;
    * ``coletor``: recebe repasse da quadrilha, nunca golpe direto, e só ele
      tira o dinheiro (saque ou saída para pessoas e comércios);
    * vítima (``is_victim``): fez ao menos um Pix de golpe, e não é fraudadora;
    * ``normal``: não enviou golpe nem repassou dinheiro de quadrilha.

    Os repasses de quadrilha só podem ir de uma conta fraudulenta para outra, e
    todo golpe sai de uma vítima e chega a uma laranja. Receber dinheiro que
    saiu da coletora (saque ou ``saida_coletor``) não é violação: o comércio ou
    a pessoa do outro lado não sabe de onde ele veio.
    """
    tx = transactions
    role = accounts.set_index("account_id")["role"]
    kind = accounts.set_index("account_id")["account_type"]
    victim = accounts.set_index("account_id")["is_victim"].astype(bool)
    scam, laundering = tx["scenario"].isin(SCAM_SCENARIOS), tx["scenario"].isin(LAUNDERING_SCENARIOS)
    exits = tx["scenario"].isin(EXIT_SCENARIOS)
    legit_out = tx["scenario"].isin(("salario", "fornecedor"))

    def accounts_with(mask, column):
        return set(tx.loc[mask, column])

    sent_scam, got_scam = accounts_with(scam, "sender"), accounts_with(scam, "receiver")
    sent_laundering, got_laundering = accounts_with(laundering, "sender"), accounts_with(laundering, "receiver")
    sent_exit = accounts_with(exits, "sender")
    merchant_sent_other = accounts_with(~legit_out, "sender")
    fraud_roles = set(FRAUD_ROLES)

    rules = {
        "comércio é PJ": lambda a, r: r != "comercio" or kind[a] == "PJ",
        "comércio só paga salário ou fornecedor": lambda a, r: r != "comercio" or a not in merchant_sent_other,
        "laranja recebe golpe": lambda a, r: r != "laranja" or a in got_scam,
        "laranja repassa": lambda a, r: r != "laranja" or a in sent_laundering,
        "intermediário recebe e repassa": lambda a, r: r != "intermediario" or (
            a in got_laundering and a in sent_laundering),
        "coletora recebe repasse": lambda a, r: r != "coletor" or a in got_laundering,
        "só laranja recebe golpe": lambda a, r: a not in got_scam or r == "laranja",
        "só vítima aplica golpe": lambda a, r: a not in sent_scam or bool(victim[a]),
        "só a coletora tira o dinheiro": lambda a, r: a not in sent_exit or r == "coletor",
        "repasse só entre fraudadoras": lambda a, r: (a not in sent_laundering and a not in got_laundering)
        or r in fraud_roles,
        "vítima não é fraudadora": lambda a, r: not victim[a] or r not in fraud_roles,
        "vítima pagou golpe": lambda a, r: not victim[a] or a in sent_scam,
    }
    rows = [(a, r, name) for a, r in role.items() for name, ok in rules.items() if not ok(a, r)]
    return pd.DataFrame(rows, columns=["account_id", "role", "regra"])


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
    if "contestado_em" in transactions:
        transactions["contestado_em"] = pd.to_datetime(transactions["contestado_em"])
    return accounts, transactions


def _day_weights(cfg: SimulationConfig) -> np.ndarray | None:
    """Probabilidade de cada dia do período (``None`` no calendário uniforme)."""
    if cfg.calendar == "uniforme":
        return None
    days = pd.date_range(cfg.start_date, periods=cfg.n_days, freq="D")
    weights = WEEKDAY_WEIGHTS[days.weekday] * np.where(days.day <= 7, MONTH_START_BOOST, 1.0)
    return weights / weights.sum()


def _random_seconds(rng: np.random.Generator, n: int, n_days: int, day_p: np.ndarray | None = None) -> np.ndarray:
    """Instantes (em segundos desde o início) seguindo o perfil horário ``HOUR_WEIGHTS``."""
    day = rng.integers(0, n_days, n) if day_p is None else rng.choice(n_days, size=n, p=day_p)
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
    horário dos golpes, e sempre nos repasses legítimos.
    """
    day, second = divmod(t, 86400.0)
    hour = int(second // 3600)
    target = day * 86400.0 + _ACTIVITY_AT_HOUR[hour] + _HOUR_RATE[hour] * (second - 3600.0 * hour) + delay
    day, remainder = divmod(target, 86400.0)
    hour = int(np.searchsorted(_ACTIVITY_AT_HOUR, remainder, side="right")) - 1
    return day * 86400.0 + 3600.0 * hour + (remainder - _ACTIVITY_AT_HOUR[hour]) / _HOUR_RATE[hour]


def _merchant_popularity(n: int) -> np.ndarray:
    """Popularidade tipo Zipf: poucos comércios concentram a maior parte dos pagamentos."""
    popularity = 1.0 / np.arange(1, n + 1) ** 1.1
    return popularity / popularity.sum()


def _amounts(rng, cfg, to_merchant: np.ndarray) -> np.ndarray:
    """Valores dos Pix comuns: P2P e P2B com a mesma lognormal, a menos que o P2B tenha a sua."""
    if cfg.merchant_amount_mu is None and cfg.merchant_amount_sigma is None:
        return rng.lognormal(cfg.amount_mu, cfg.amount_sigma, to_merchant.size)
    mu = np.where(to_merchant, _or(cfg.merchant_amount_mu, cfg.amount_mu), cfg.amount_mu)
    sigma = np.where(to_merchant, _or(cfg.merchant_amount_sigma, cfg.amount_sigma), cfg.amount_sigma)
    return rng.lognormal(mu, sigma)


def _or(value, default):
    return default if value is None else value


def _normal_transactions(rng, cfg, people, merchants, community, day_p=None) -> pd.DataFrame:
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
    receiver[to_merchant] = rng.choice(merchants, size=to_merchant.sum(), p=_merchant_popularity(len(merchants)))

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
        "t": _random_seconds(rng, n, cfg.n_days, day_p),
        "sender": people[sender],
        "receiver": receiver,
        "amount": _amounts(rng, cfg, to_merchant),
        "scenario": "normal",
    })


def _fraud_ring(rng, cfg, people, merchants, community, fraud_pool, recruited, day_p=None, avoid=frozenset()):
    """Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora [-> saque].

    ``recruited`` guarda as pessoas que já viraram laranjas (em qualquer
    quadrilha), para que não sejam recrutadas de novo nem escolhidas como vítimas.
    """
    if cfg.p_recruited_mule > 0:
        mules = [_recruit(rng, people, recruited, avoid) if rng.random() < cfg.p_recruited_mule else next(fraud_pool)
                 for _ in range(cfg.mules_per_ring)]
    else:
        mules = [next(fraud_pool) for _ in range(cfg.mules_per_ring)]
    collector = next(fraud_pool)
    chain = [next(fraud_pool) for _ in range(cfg.chain_length)] if rng.random() < cfg.p_chain else []
    typology = "cadeia"
    if cfg.laundering_typologies != ("cadeia",):
        typology = str(rng.choice(list(cfg.laundering_typologies)))
        if typology != "cadeia" and len(chain) < 2:  # as outras tipologias precisam de intermediários
            chain = [next(fraud_pool) for _ in range(max(cfg.chain_length, 2))]
    exchange = merchants[rng.integers(len(merchants))] if cfg.collector_cashout else None
    roles = {m: "laranja" for m in mules} | {a: "intermediario" for a in chain} | {collector: "coletor"}

    rows, victims = [], set()
    # A quadrilha age durante uma janela de ~2 dias escolhida ao acaso.
    if day_p is not None and cfg.fraud_hours == "comercial":
        window = day_p[: max(cfg.n_days - 2, 1)]
        ring_start = rng.choice(window.size, p=window / window.sum()) * 86400.0
    else:
        ring_start = rng.integers(0, max(cfg.n_days - 2, 1)) * 86400.0
    for i in range(cfg.victims_per_ring):
        # Com a estrutura sorteada, as primeiras vítimas passam por laranjas diferentes, para
        # nenhuma laranja ficar sem golpe (no sorteio simples, ~5% das quadrilhas base têm uma).
        if cfg.estrutura_aleatoria and i < len(mules):
            mule = mules[i]
        else:
            mule = mules[rng.integers(len(mules))]
        if rng.random() < 0.5:
            scenario = "falso_suporte"
            payer = _pick_person(rng, people, recruited)
            payers = [payer] * int(rng.integers(1, 4))
        else:
            scenario = "clonagem_whatsapp"
            cloned = rng.integers(len(people))
            contacts = np.flatnonzero((community == community[cloned]) & (np.arange(len(people)) != cloned))
            if recruited:
                contacts = contacts[~np.isin(people[contacts], list(recruited))]
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
            rows += _launder(rng, cfg, t, amount, mule, chain, collector, typology, exchange)
    return pd.DataFrame(rows, columns=COLUMNS), roles, victims


def _recruit(rng, people, recruited: set, avoid=frozenset()) -> str:
    """Uma pessoa que ainda não é laranja: a conta cedida ou alugada para a quadrilha.

    ``avoid``: pessoas que também não podem ser recrutadas. Com a estrutura
    sorteada, são as vítimas das quadrilhas anteriores (na estrutura fixa, uma
    vítima pode raramente virar laranja de outra quadrilha; ver ``audit_roles``).
    """
    person = _pick_person(rng, people, recruited | avoid if avoid else recruited)
    recruited.add(person)
    return person


def _pick_person(rng, people, excluded: set) -> str:
    person = people[rng.integers(len(people))]
    while person in excluded:  # só acontece com laranjas recrutadas
        person = people[rng.integers(len(people))]
    return person


def _launder(rng, cfg, t, amount, mule, chain, collector, typology="cadeia", exchange=None):
    """Leva o valor da laranja até a coletora, seguindo a tipologia da quadrilha.

    * ``cadeia``: laranja -> [intermediários em fila] -> coletora;
    * ``ciclo``: o dinheiro dá uma volta pelos intermediários e volta à laranja
      antes de seguir para a coletora;
    * ``espalha_junta``: a laranja divide o valor entre os intermediários, que
      o juntam de novo na coletora;
    * ``bipartido``: cada repasse passa por um intermediário sorteado, então as
      laranjas e os intermediários formam um grafo bipartido.

    Com ``exchange``, cada valor que chega à coletora é sacado (Pix para a
    corretora) depois de ``cashout_delay_min`` minutos, em média.
    """
    if typology == "cadeia":
        path = [mule, *chain, collector]
        branches = [_hops(rng, cfg, t, amount, path, "lavagem_em_cadeia" if len(path) > 2 else "repasse_laranja")]
    elif typology == "ciclo":
        branches = [_hops(rng, cfg, t, amount, [mule, *chain, mule, collector], "ciclo")]
    elif typology == "espalha_junta":
        shares = rng.dirichlet(np.ones(len(chain)))
        branches = [_hops(rng, cfg, t, amount * share, [mule, inter, collector], "espalha_junta")
                    for inter, share in zip(chain, shares)]
    else:  # bipartido
        branches = [_hops(rng, cfg, t, amount, [mule, chain[rng.integers(len(chain))], collector], "bipartido")]

    rows = [row for branch_rows, _, _ in branches for row in branch_rows]
    if exchange is not None:
        for _, t_end, amount_end in branches:
            rows.append((_later(cfg, t_end, rng.exponential(cfg.cashout_delay_min * 60)), collector, exchange,
                         amount_end * rng.uniform(0.97, 1.0), "saque"))
    return rows


def _hops(rng, cfg, t, amount, path, scenario):
    """Repassa o valor ao longo de ``path``, retendo uma pequena comissão a cada salto."""
    rows = []
    for sender, receiver in zip(path[:-1], path[1:]):
        t = _later(cfg, t, rng.exponential(cfg.forward_delay_min * 60))
        amount *= rng.uniform(0.90, 0.99)
        rows.append((t, sender, receiver, amount, scenario))
    return rows, t, amount


def _later(cfg, t, delay):
    return t + delay if cfg.fraud_hours == "uniforme" else _after_activity(t, delay)


def _collector_payouts(rng, cfg, ring_tx, collector, people, merchants) -> pd.DataFrame:
    """A coletora esvazia o que recebeu: vários Pix de saída para pessoas e comércios.

    Sem isso a coletora é quase só um sorvedouro (recebe e não paga ninguém). Aqui
    ela repassa ~90% do recebido em ``Poisson(collector_payouts)`` Pix (pelo menos
    um), de valores desiguais, nas horas seguintes à última entrada. As arestas
    ganham o cenário ``saida_coletor``, para serem identificadas na rede. É a
    alternativa "muitas arestas" ao ``collector_cashout`` (uma corretora só).
    """
    incoming = ring_tx[ring_tx["receiver"] == collector]
    n = max(1, int(rng.poisson(cfg.collector_payouts)))
    receivers = np.where(rng.random(n) < cfg.p_merchant, rng.choice(merchants, n), rng.choice(people, n))
    amounts = incoming["amount"].sum() * rng.uniform(0.85, 0.95) * rng.dirichlet(np.ones(n))
    t = incoming["t"].max()
    rows = []
    for receiver, amount in zip(receivers, amounts):
        t = _later(cfg, t, rng.exponential(cfg.forward_delay_min * 60))
        rows.append((t, collector, receiver, amount, "saida_coletor"))
    return pd.DataFrame(rows, columns=COLUMNS)


def _camouflage_transactions(rng, cfg, accounts, people, merchants, day_p=None) -> pd.DataFrame:
    """Movimentações comuns das contas criadas para a fraude, para que não sejam triviais de isolar."""
    sender = np.repeat(accounts, rng.poisson(cfg.camouflage_tx, len(accounts)))
    n = sender.size
    to_merchant = rng.random(n) < cfg.p_merchant
    receiver = np.where(to_merchant, rng.choice(merchants, n), rng.choice(people, n))
    return pd.DataFrame({
        "t": _random_seconds(rng, n, cfg.n_days, day_p),
        "sender": sender,
        "receiver": receiver,
        "amount": _amounts(rng, cfg, to_merchant),
        "scenario": "normal",
    })


def _has_look_alikes(cfg) -> bool:
    return (cfg.employees_per_merchant > 0 or cfg.supplier_tx_per_week > 0 or cfg.p_organizer > 0
            or cfg.p_fast_forwarder > 0)


def _look_alike_transactions(rng, cfg, people, merchants, community, day_p=None) -> pd.DataFrame:
    """Pix legítimos que se parecem com partes de uma quadrilha ("negativos difíceis").

    * ``salario``: comércios pagam a folha no dia útil ``salary_business_day``,
      num leque de muitos destinos, como uma coletora que espalha dinheiro;
    * ``fornecedor``: comércios pagam outros comércios toda semana;
    * ``vaquinha``: uma pessoa junta dinheiro de vários contatos em poucas horas
      e paga um comércio, como uma laranja que recebe de várias vítimas e repassa;
    * ``repasse_salario``: uma pessoa repassa boa parte do salário (o aluguel) em
      poucas horas, o que dá tempo de permanência curto a uma conta legítima.
    """
    n_people, rows = len(people), []
    salary_days = _salary_days(cfg)

    employer: dict[int, int] = {}  # índice da pessoa -> índice do comércio
    if cfg.employees_per_merchant > 0:
        # Folha com cauda pesada (poucas empresas grandes), com média employees_per_merchant.
        sizes = rng.poisson(cfg.employees_per_merchant * rng.lognormal(-0.5, 1.0, len(merchants)))
        for m, k in enumerate(sizes):
            for p in rng.choice(n_people, size=min(int(k), n_people), replace=False):
                employer.setdefault(int(p), m)
    forwarders = np.flatnonzero(rng.random(n_people) < cfg.p_fast_forwarder) if cfg.p_fast_forwarder > 0 else []
    for p in forwarders:  # quem repassa o salário precisa receber um
        employer.setdefault(int(p), int(rng.integers(len(merchants))))
    landlord = {int(p): int((p + 1 + rng.integers(n_people - 1)) % n_people) for p in forwarders}

    for p, m in employer.items():
        salary = rng.lognormal(np.log(2500) - 0.08, 0.4)  # média ~R$ 2.500
        for day in salary_days:
            t = day * 86400.0 + rng.uniform(8, 12) * 3600.0
            rows.append((t, merchants[m], people[p], salary, "salario"))
            if p in landlord:
                t_rent = _after_activity(t, rng.exponential(2 * 3600))
                rows.append((t_rent, people[p], people[landlord[p]], salary * rng.uniform(0.3, 0.6),
                             "repasse_salario"))

    if cfg.supplier_tx_per_week > 0 and len(merchants) > 1:
        popularity = _merchant_popularity(len(merchants))
        n_pay = rng.poisson(cfg.supplier_tx_per_week * cfg.n_days / 7, len(merchants))
        payer = np.repeat(np.arange(len(merchants)), n_pay)
        supplier = rng.choice(len(merchants), size=payer.size, p=popularity)
        supplier = np.where(supplier == payer, (supplier + 1) % len(merchants), supplier)
        times = _random_seconds(rng, payer.size, cfg.n_days, day_p)
        amounts = rng.lognormal(np.log(1500) - 0.5, 1.0, payer.size)  # média ~R$ 1.500
        rows += list(zip(times, merchants[payer], merchants[supplier], amounts, ["fornecedor"] * payer.size))

    if cfg.p_organizer > 0:
        popularity = _merchant_popularity(len(merchants))
        for org in np.flatnonzero(rng.random(n_people) < cfg.p_organizer):
            members = np.flatnonzero((community == community[org]) & (np.arange(n_people) != org))
            for _ in range(rng.poisson(max(cfg.n_days / 30, 1e-9))):
                t = _random_seconds(rng, 1, cfg.n_days, day_p)[0]
                k = min(int(rng.integers(3, 9)), members.size)
                total = 0.0
                for friend in rng.choice(members, size=k, replace=False):
                    t += rng.exponential(1800)
                    value = rng.lognormal(np.log(60) - 0.18, 0.6)  # média ~R$ 60
                    total += value
                    rows.append((t, people[friend], people[org], value, "vaquinha"))
                if k:
                    store = merchants[rng.choice(len(merchants), p=popularity)]
                    rows.append((_after_activity(t, rng.exponential(2 * 3600)), people[org], store,
                                 total * rng.uniform(0.95, 1.0), "vaquinha"))
    return pd.DataFrame(rows, columns=COLUMNS)


def _salary_days(cfg) -> list[int]:
    """Dias do período (a partir de 0) em que cai o ``salary_business_day``-ésimo dia útil do mês."""
    start = pd.Timestamp(cfg.start_date)
    end = start + pd.Timedelta(days=cfg.n_days)
    days = []
    for month in pd.period_range(start, end - pd.Timedelta(seconds=1), freq="M"):
        business = pd.bdate_range(month.start_time, month.end_time)
        if len(business) >= cfg.salary_business_day:
            payday = business[cfg.salary_business_day - 1]
            if start <= payday < end:
                days.append((payday - start).days)
    return days


def _contestations(rng, cfg, tx: pd.DataFrame) -> pd.DataFrame:
    """Coluna ``contestado_em``: quando a vítima contestou o golpe (vazia nos demais Pix).

    Nem toda vítima contesta, e a contestação chega com atraso (mediana
    ``contest_delay_h``), como no MED: é só a partir dela que o banco sabe da fraude.
    """
    scam = tx["scenario"].isin(SCAM_SCENARIOS).to_numpy()
    contested = np.zeros(len(tx), dtype=bool)
    contested[scam] = rng.random(scam.sum()) < cfg.p_contested
    delay = pd.to_timedelta(rng.lognormal(np.log(cfg.contest_delay_h), 1.0, contested.sum()), unit="h")
    tx["contestado_em"] = pd.Series(pd.NaT, index=tx.index, dtype="datetime64[ns]")
    tx.loc[contested, "contestado_em"] = (tx.loc[contested, "timestamp"] + delay).dt.floor("s").to_numpy()
    return tx


def _accounts_table(rng, people, merchants, roles, victims, p_new_fraud_account) -> pd.DataFrame:
    person_ids = set(people)
    created = [a for a in roles if a not in person_ids]  # contas abertas para a fraude
    n_fraud = len(created)
    # Contas usadas em fraudes tendem a ser recém-abertas; parte delas, porém,
    # são contas antigas cedidas ou invadidas, com a mesma idade das contas comuns.
    # As laranjas recrutadas entre as pessoas mantêm a idade (e o histórico) que já tinham.
    new = rng.random(n_fraud) < p_new_fraud_account
    fraud_age = np.where(new, rng.integers(1, 60, n_fraud), rng.integers(30, 3650, n_fraud))
    role = np.array([roles.get(p, "normal") for p in people] + ["comercio"] * len(merchants)
                    + [roles[a] for a in created])
    accounts = pd.DataFrame({
        "account_id": np.concatenate([people, merchants, np.array(created, dtype=people.dtype)]),
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
