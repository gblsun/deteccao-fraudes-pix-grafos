---
tags: [codigo]
---

# `pixfraud.experiment`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/experiment.py`](../../src/pixfraud/experiment.py) · [mapa do código](mapa-do-codigo.md)

Núcleo do experimento: transações -> grafo -> atributos -> detectores -> métricas.

Usado pelos scripts de `scripts/` e pelo explorador interativo
(`app/explorador.py`). `save_metadata` grava, ao lado de cada resultado, o
que é preciso para refazê-lo (commit, configuração, sementes, versões).

## Classes e funções

### `Prepared` (classe)

```python
class Prepared
```

Tudo o que os detectores precisam, calculado uma vez por dataset (ver `prepare`).

### `load_experiment_config` (função)

```python
def load_experiment_config(path: str | Path) -> dict
```

Lê o YAML de experimento inteiro (seções `simulacao`, `atributos` e `modelos`).

### `prepare` (função)

```python
def prepare(accounts: pd.DataFrame, transactions: pd.DataFrame, config: dict) -> Prepared
```

Monta o grafo e calcula todos os atributos (seção `atributos` da configuração).

### `run_detectors` (função)

```python
def run_detectors(features: pd.DataFrame, labels: pd.Series, models_config: dict, feature_sets: dict[str, list[str]]=FEATURE_SETS, models: list[str] | None=None) -> tuple[pd.DataFrame, dict[tuple[str, str], Detection]]
```

Roda cada detector (`models`, ou todos de `DETECTORS`) em cada conjunto de atributos.

Devolve a tabela de métricas (uma linha por combinação) e as detecções,
indexadas por `(conjunto, modelo)`.

### `seeded_models` (função)

```python
def seeded_models(models_config: dict, seed: int) -> dict
```

Cópia da seção `modelos` com `seed` em todo detector que aceita semente.

Assim cada repetição de um estudo muda também a aleatoriedade dos
detectores (Isolation Forest, One-Class SVM aproximado, autoencoder), e
não só o dataset.

### `run_seeds` (função)

```python
def run_seeds(simulation: SimulationConfig, config: dict, seeds: Iterable[int], feature_sets: dict[str, list[str]]=FEATURE_SETS, models: list[str] | None=None, processes: int=1) -> Iterator[tuple[int, Prepared, pd.DataFrame]]
```

Repete o experimento com várias sementes.

Cada semente gera um dataset sintético diferente e muda a semente dos
detectores (`seeded_models`). Produz `(semente, preparado, métricas)`,
com a coluna `semente` já incluída nas métricas, sempre na ordem das
sementes. Com `processes` > 1, as sementes rodam em paralelo: o
resultado é o mesmo, mais rápido, e a memória cresce com o nº de processos.

### `load_scenarios` (função)

```python
def load_scenarios(path: str | Path) -> dict[str, dict]
```

Lê os cenários de `configs/cenarios.yaml`: nome -> parâmetros da simulação a trocar.

Os nomes dos parâmetros são validados aqui, para um erro de digitação não
aparecer só no meio de uma execução longa.

### `feature_ablation` (função)

```python
def feature_ablation(features: pd.DataFrame, labels: pd.Series, columns: list[str], models_config: dict, models: list[str] | None=None) -> pd.DataFrame
```

Quanto cada atributo contribui: a average precision cai quando ele sai?

Para cada detector, roda uma vez com todos os `columns` e depois tirando
um atributo de cada vez. `queda` > 0 quer dizer que o atributo ajudava;
< 0, que ele atrapalhava (ruído para aquele detector).

### `supervised_scores` (função)

```python
def supervised_scores(features: pd.DataFrame, labels: pd.Series, seed: int=42, folds: int=5, model: str='random_forest', **params) -> pd.Series
```

Probabilidade de fraude de cada conta dada por um modelo que **viu os rótulos**.

Serve de teto para os detectores não supervisionados: com validação
cruzada estratificada, cada conta recebe o escore de um modelo treinado
sem ela. Numa situação real esses rótulos não existiriam (ou seriam
poucos), então a distância até este teto mostra quanto se perde por não
tê-los. `model`: um nome de `pixfraud.models.SUPERVISED`
(`random_forest` ou `gradient_boosting`); `params` são os
hiperparâmetros dele (a seção `modelos` da configuração).

### `known_fraud_scores` (função)

```python
def known_fraud_scores(features: pd.DataFrame, known: list, seed: int=42, folds: int=5, **params) -> pd.Series
```

Random Forest treinado só com as fraudes **já conhecidas**; o resto conta como "não fraude".

É o par tabular de `pixfraud.gnn.sage_known_fraud_scores`, com a mesma
divisão (ver `models.supervised.random_forest.random_forest_known_fraud_scores`).

### `all_model_scores` (função)

```python
def all_model_scores(prepared: Prepared, models: dict, columns: list[str], known: list, known_legit: list, seed: int=42, use_gnn: bool=False, reference: str='dbscan', rank_index: pd.Index | None=None) -> dict[str, pd.Series]
```

O escore de cada modelo da vitrine (`MODEL_FAMILIES`) num mesmo dataset.

`models` é a seção `modelos` da configuração (já com a semente, ver
`seeded_models`); `columns`, os atributos dos modelos que usam a tabela.
Os semi-supervisionados partem das fraudes `known` e das legítimas
`known_legit`; os combinados são a média dos percentis com `reference`,
calculados entre as contas de `rank_index` (padrão: todas). Os tetos
supervisionados usam os rótulos em validação cruzada. A GNN só entra com
`use_gnn`.

### `save_metadata` (função)

```python
def save_metadata(path: str | Path, config: dict | None=None, **extra) -> Path
```

Grava um `*_meta.json` com o que é preciso para refazer um resultado.

Guarda a data, o commit do git (e se havia alterações não commitadas, caso
em que o resultado pode não corresponder exatamente ao commit), a versão do
Python e dos pacotes principais e a configuração usada. `extra` acrescenta
o que for específico de cada script: sementes, cenários, duração...

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _run_one_seed(simulation, config, seed, feature_sets, models)`: Gera a rede de uma semente, prepara os atributos e roda os detectores nela.
- `def _git(*args: str) -> str | None`: Saída de um comando do git no repositório do pacote, ou `None` se o git não estiver disponível.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`pixfraud.online`](pixfraud.online.md)
- [`scripts/01_dados/auditar_papeis.py`](scripts.01_dados.md)
- [`scripts/01_dados/gerar_dataset.py`](scripts.01_dados.md)
- [`scripts/01_dados/validar_realismo.py`](scripts.01_dados.md)
- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/inferencia_atributos.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`scripts/03_modelos/otimizar_hiperparametros.py`](scripts.03_modelos.md)
- [`scripts/03_modelos/rodar_experimento.py`](scripts.03_modelos.md)
- [`scripts/04_avaliacao/avaliar_atributos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_cenarios.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_deteccao_online.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_externo.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_fraudar.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn_rotulos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_propagacao.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_robustez.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_sementes.py`](scripts.04_avaliacao.md)
- [`scripts/05_interpretacao/investigar_falsos_positivos.py`](scripts.05_interpretacao.md)
- [`scripts/ferramentas/ilustrar_testes.py`](scripts.ferramentas.md)
- [`tests/test_experiment.py`](testes.md)
- [`tests/test_exploration.py`](testes.md)
- [`tests/test_gnn_direcionada.py`](testes.md)
- [`tests/test_scripts.py`](testes.md)
- [`tests/test_simulation.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
