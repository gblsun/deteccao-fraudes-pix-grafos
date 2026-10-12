---
tags: [codigo]
---

# `pixfraud.external`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/external.py`](../../src/pixfraud/external.py) · [mapa do código](mapa-do-codigo.md)

Carregadores de datasets públicos de fraude e lavagem de dinheiro.

Convertem os arquivos originais para o formato do projeto (tabelas
`accounts` e `transactions`, as mesmas de `pixfraud.simulation`), para
rodar o mesmo pipeline fora do gerador sintético. Isso quebra a
circularidade de avaliar os detectores só nos padrões que nós mesmos
injetamos.

Os arquivos vêm do Kaggle (exige login ou o token da API); veja
`data/README.md`.

* **AMLworld** (IBM; Altman et al., 2023): transações entre contas bancárias
  com rótulo de lavagem e padrões em grafo (fan-in, fan-out, ciclos,
  cadeias…). Arquivos `HI-Small_Trans.csv`, `LI-Small_Trans.csv` etc.
  São grandes: use `days` ou `nrows` para recortar. `formats` mantém só
  as formas de pagamento parecidas com o Pix, `load_amlworld_patterns` lê a
  tipologia de cada tentativa de lavagem (`*_Patterns.txt`) e
  `time_windows` divide o período em janelas, usadas como repetições.
* **PaySim** (Lopez-Rojas et al., 2016): simulação de dinheiro móvel.
  Atenção: quase toda conta de origem aparece uma única vez, então a
  estrutura em grafo é fraca. Serve mais como contraste.

Nos dois casos não existe idade da conta, então `account_age_days` fica 0
(esse atributo tabular deixa de informar).

## Classes e funções

### `load_amlworld` (função)

```python
def load_amlworld(path: str | Path, currency: str | None='US Dollar', days: int | None=None, nrows: int | None=None, formats: Iterable[str] | None=None) -> tuple[pd.DataFrame, pd.DataFrame]
```

Lê um arquivo `*_Trans.csv` do AMLworld.

* a conta é identificada por banco + número (`"{banco}_{conta}"`);
* `currency`: mantém só os pagamentos feitos e recebidos nessa moeda,
  para os valores serem comparáveis (`None` mantém todos);
* `formats`: mantém só essas formas de pagamento, por exemplo
  `PIX_LIKE_FORMATS` (`None` mantém todas);
* `days`: mantém só os primeiros `days` dias;
* transferências de uma conta para ela mesma são descartadas.

Uma conta é marcada como fraudulenta se enviou ou recebeu alguma
transação de lavagem.

### `load_paysim` (função)

```python
def load_paysim(path: str | Path, start: str='2026-01-01', nrows: int | None=None) -> tuple[pd.DataFrame, pd.DataFrame]
```

Lê o CSV do PaySim (colunas `step, type, amount, nameOrig, nameDest, isFraud`...).

`step` é a hora da simulação, convertida em data a partir de `start`.
No PaySim o fraudador toma uma conta e transfere o dinheiro para outra:
a origem de uma transação fraudulenta é a **vítima** e o destino é a
conta **fraudulenta**.

### `load_amlworld_patterns` (função)

```python
def load_amlworld_patterns(path: str | Path) -> pd.DataFrame
```

Lê o `*_Patterns.txt` do AMLworld: as transações de cada tentativa de lavagem.

O arquivo tem blocos `BEGIN LAUNDERING ATTEMPT - <TIPO>: ...` e
`END LAUNDERING ATTEMPT - <TIPO>`, com as transações no mesmo formato do
`*_Trans.csv`. Devolve uma linha por transação, com o número da tentativa
e a tipologia (`fan_in`, `fan_out`, `cycle`, `gather_scatter`,
`scatter_gather`, `stack`, `bipartite`, `random`...).

### `pattern_accounts` (função)

```python
def pattern_accounts(patterns: pd.DataFrame) -> pd.DataFrame
```

Contas de cada tipologia (`account_id`, `typology`); uma conta pode estar em várias.

### `time_windows` (função)

```python
def time_windows(transactions: pd.DataFrame, days: int) -> Iterator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame]]
```

Divide as transações em janelas consecutivas de `days` dias.

Gera `(início, accounts, transactions)` para cada janela com transações.
Os rótulos são refeitos dentro da janela: uma conta é suspeita se enviou ou
recebeu alguma transação de lavagem **naquela janela** (sem vítimas, como
no AMLworld). Janelas diferentes servem de repetições, no lugar das
sementes do gerador.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _amlworld_chunk(raw: pd.DataFrame, currency: str | None, formats: Iterable[str] | None) -> pd.DataFrame`: Converte um bloco do `*_Trans.csv`, já filtrado por moeda e forma de pagamento.
- `def _account(bank: pd.Series, number: pd.Series) -> pd.Series`: `"{banco}_{conta}"`, com o código do banco sem zeros à esquerda (igual nos dois arquivos).
- `def _account_id(bank: str, number: str) -> str`: Identificador único de conta externa: banco (sem zeros à esquerda) e número.
- `def _parties(tx: pd.DataFrame) -> set`: Todas as contas que pagam ou recebem em `tx`.
- `def _project_format(tx: pd.DataFrame, fraud_accounts: set, victims: set) -> tuple[pd.DataFrame, pd.DataFrame]`: Ordena as transações, numera os `tx_id` e monta as duas tabelas no formato do projeto.
- `def _accounts_table(tx: pd.DataFrame, fraud_accounts: set, victims: set) -> pd.DataFrame`: Tabela de contas de um dataset externo: tipo e idade desconhecidos, papel só fraude/normal.

## Quem usa este módulo

- [`scripts/01_dados/importar_dataset.py`](scripts.01_dados.md)
- [`scripts/04_avaliacao/avaliar_externo.py`](scripts.04_avaliacao.md)
- [`tests/test_external.py`](testes.md)
