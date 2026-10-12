---
tags: [codigo]
---

# `pixfraud.online`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/online.py`](../../src/pixfraud/online.py) · [mapa do código](mapa-do-codigo.md)

Detecção ao longo do tempo: a conta foi sinalizada a tempo de bloquear o dinheiro?

No Pix, o MED (Mecanismo Especial de Devolução) só devolve o que ainda está nas
contas que receberam o dinheiro, e o bloqueio cautelar segura valores por até
72 h. Por isso não basta saber *se* uma conta fraudulenta é detectada: importa
*quando*. Aqui o detector roda em pontos de corte sucessivos (por exemplo, a
cada 6 h), vendo só os Pix feitos até ali, como aconteceria em produção.

* `checkpoint_flags`: em cada ponto de corte, as `k` contas mais suspeitas
  (o que um analista revisaria);
* `exposure_times`: quando cada conta fraudulenta recebeu dinheiro de golpe
  pela primeira vez;
* `first_flags`: o primeiro corte, a partir dessa exposição, em que a conta
  foi sinalizada;
* `recovered_amount`: reproduz os Pix da quadrilha bloqueando cada conta no
  instante em que foi sinalizada e mede quanto do dinheiro roubado ficou retido.
  Dinheiro parado numa conta da quadrilha por mais de `cashout` é
  considerado sacado (perdido).

## Classes e funções

### `exposure_times` (função)

```python
def exposure_times(transactions: pd.DataFrame, fraud_accounts) -> pd.Series
```

Primeiro Pix fraudulento recebido por cada conta de `fraud_accounts`.

### `relevant_checkpoints` (função)

```python
def relevant_checkpoints(exposure: pd.Series, freq: str='6h', horizon: str='72h') -> pd.DatetimeIndex
```

Pontos de corte (a cada `freq`) em que alguma conta está até `horizon` depois da exposição.

Fora desses intervalos, sinalizar uma conta fraudulenta não muda nada nas
métricas, então não vale a pena calcular os atributos.

### `checkpoint_flags` (função)

```python
def checkpoint_flags(accounts: pd.DataFrame, transactions: pd.DataFrame, config: dict, checkpoints, k: int, feature_sets: dict[str, list[str]] | None=None, models: list[str] | None=None) -> pd.DataFrame
```

As `k` contas mais suspeitas em cada ponto de corte, para cada conjunto de atributos e modelo.

Em cada corte `t`, os atributos são recalculados só com os Pix anteriores
a `t`, e só as contas que já apareceram entram na conta. Devolve uma
linha por conta sinalizada: `corte`, `atributos`, `modelo` e `account_id`.

### `first_flags` (função)

```python
def first_flags(flags: pd.DataFrame, exposure: pd.Series) -> pd.Series
```

Primeiro corte em que cada conta foi sinalizada, a partir da sua exposição (`NaT` se nunca).

`flags` são as linhas de **um** conjunto de atributos e modelo de
`checkpoint_flags`. Sinalizações anteriores à exposição são ignoradas:
antes do golpe, um analista não teria o que bloquear.

### `recovered_amount` (função)

```python
def recovered_amount(transactions: pd.DataFrame, fraud_accounts, freeze_at: pd.Series, cashout: str='24h') -> dict[str, float]
```

Quanto do dinheiro roubado ficaria retido se cada conta fosse bloqueada em `freeze_at`.

Reproduz, em ordem, só os Pix fraudulentos (`is_fraud`). O dinheiro entra
quando uma vítima (conta fora de `fraud_accounts`) paga uma conta da
quadrilha. Uma conta bloqueada não repassa mais nada: o que estava nela e
o que chegar depois fica retido (recuperável pelo MED). Cada valor parado
numa conta não bloqueada por mais de `cashout` é sacado e se perde.
Repasses usam primeiro o dinheiro que chegou antes.

## Quem usa este módulo

- [`scripts/04_avaliacao/avaliar_deteccao_online.py`](scripts.04_avaliacao.md)
- [`tests/test_online.py`](testes.md)
