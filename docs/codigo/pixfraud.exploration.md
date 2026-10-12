---
tags: [codigo]
---

# `pixfraud.exploration`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/exploration.py`](../../src/pixfraud/exploration.py) · [mapa do código](mapa-do-codigo.md)

O que o explorador interativo (`app/explorador.py`) e a página da rede precisam calcular.

Fica no pacote, e não no app, para poder ser testado sem o Streamlit:

* `generate_network`: gera e prepara a rede de uma semente e um cenário;
* `all_model_scores`: o escore de risco de **todos** os modelos, não
  supervisionados e supervisionados;
* `rank_models`: a nota (AP e precision@k) de cada modelo, ordenada dentro do grupo;
* `network_summary`: os números que resumem a rede (contas, quadrilhas,
  valor dos golpes, componente gigante...);
* `top_k_outcome`: o que o modelo acertou e errou entre as `k` contas mais suspeitas.

## Classes e funções

### `generate_network` (função)

```python
def generate_network(scenario: str, seed: int, config: dict, config_path: str | Path, scenarios_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, Prepared]
```

Contas, Pix e a rede preparada (grafo, atributos, rótulos) de `seed` no `scenario`.

O mesmo caminho dos estudos (`scripts/03_modelos/avaliar_modelos.py`): o gerador de
`config_path` com os parâmetros do cenário trocados, e a semente trocada.

### `all_model_scores` (função)

```python
def all_model_scores(prepared: Prepared, columns: list, config: dict, seed: int, progress: Callable[[str, float], None] | None=None) -> dict[str, tuple[str, pd.Series]]
```

Escores de cada modelo: `{nome: (grupo, escores)}`.

`grupo` é `UNSUPERVISED` ou `SUPERVISED`; os supervisionados são
pontuados em validação cruzada (cada conta pelo modelo que não viu o
rótulo dela). As redes neurais para grafos entram só com o extra `gnn`.
Um modelo que falha (ex.: o DOMINANT recusa redes muito grandes) é pulado,
para não perder o resto. `progress(nome, segundos)` é chamado depois de
cada modelo.

### `rank_models` (função)

```python
def rank_models(scores: dict[str, tuple[str, pd.Series]], labels: pd.Series, k: int | None=None) -> pd.DataFrame
```

Uma linha por modelo: grupo, nome legível, AP, ROC-AUC e precision@k.

Ordenada pelo grupo (não supervisionados primeiro) e, dentro dele, da maior
AP para a menor; a coluna `posicao` é a colocação dentro do grupo.

### `picker_entries` (função)

```python
def picker_entries(scores: dict[str, tuple[str, pd.Series]], ranking: pd.DataFrame) -> tuple[dict, dict]
```

`risk` e `risk_groups` para `explorer.network_explorer_html`, na ordem de `ranking`.

Cada modelo aparece no seletor como "1º PCA · AP 0,81", agrupado em não
supervisionados e supervisionados.

### `network_summary` (função)

```python
def network_summary(accounts: pd.DataFrame, transactions: pd.DataFrame, graph: nx.DiGraph) -> dict
```

Os números que resumem uma rede, para os cartões do explorador.

Uma quadrilha = uma conta coletora (o gerador cria uma por quadrilha). O
valor dos golpes soma os Pix de fraude pagos pelas vítimas; os repasses
dentro da quadrilha não entram, para não contar o mesmo dinheiro duas vezes.

### `top_k_outcome` (função)

```python
def top_k_outcome(scores: pd.Series, labels: pd.Series, k: int) -> pd.Series
```

Para cada conta: `achou`, `alarme_falso`, `perdeu` ou `resto` (ver `OUTCOMES`).

O top-k são as `k` contas de maior escore, a fila que um analista olharia primeiro.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`tests/test_exploration.py`](testes.md)
