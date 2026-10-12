---
tags: [codigo]
---

# `pixfraud.stats`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/stats.py`](../../src/pixfraud/stats.py) · [mapa do código](mapa-do-codigo.md)

Inferência estatística para a pesquisa.

* `compare_groups`: cada atributo difere entre contas fraudulentas e
  normais? Teste de Mann-Whitney, tamanho de efeito (delta de Cliff) e
  correção de Holm para múltiplos testes.
* `bootstrap_metric`: intervalo de confiança de uma métrica de desempenho
  (reamostrando as contas).
* `paired_comparison`: duas abordagens avaliadas nas mesmas sementes (ex.:
  tabular × grafo). Diferença média com IC, teste de Wilcoxon pareado e teste
  t pareado. `compare_runs` aplica o teste a vários pares de conjuntos de
  atributos, com correção de Holm, e `summarize_runs` resume as execuções.
* `null_model_test`: uma estatística do grafo (reciprocidade, triângulos…) é
  maior do que o esperado por acaso? Compara com grafos aleatórios que
  preservam os graus (modelo nulo) e dá o escore z e o p-valor empírico.
* `contingency_test`: associação entre duas variáveis categóricas
  (qui-quadrado; Fisher exato e razão de chances nas tabelas 2×2), como "é
  fraude" × "foi de madrugada".
* `kruskal_groups` e `dunn_posthoc`: cada atributo difere entre três ou
  mais grupos **independentes** (os papéis das contas, os cenários)? Kruskal-
  Wallis com ε² e Holm; o teste de Dunn diz quais pares diferem.
* `friedman_models`: vários modelos medidos nas **mesmas** sementes diferem?
  Teste de Friedman, W de Kendall, postos médios e a diferença crítica de
  Nemenyi (Demšar, 2006).
* `permutation_test_metric` e `topk_hypergeom`: o modelo é melhor que o
  acaso (embaralhando o gabarito; contando as fraudes no top-k)?

Qual usar em cada etapa: `docs/plano-de-testes-estatisticos.md`.

## Classes e funções

### `cliffs_delta` (função)

```python
def cliffs_delta(x, y) -> float
```

Delta de Cliff: P(X > Y) - P(X < Y), de -1 a 1 (0 = distribuições iguais).

### `effect_size_label` (função)

```python
def effect_size_label(delta: float) -> str
```

Rótulo do tamanho de efeito de Cliff (limiares de Romano et al., 2006).

### `holm_correction` (função)

```python
def holm_correction(p_values) -> np.ndarray
```

p-valores ajustados pelo método de Holm-Bonferroni (controla o erro familiar).

### `compare_groups` (função)

```python
def compare_groups(features: pd.DataFrame, labels: pd.Series) -> pd.DataFrame
```

Compara cada atributo entre fraude (`labels` verdadeiro) e normal.

Mann-Whitney U testa se um grupo tende a ter valores maiores que o outro
sem supor normalidade, o que é importante porque os atributos têm cauda
pesada. Com milhares de contas quase tudo fica "significativo", então o
**tamanho de efeito** (delta de Cliff) é o que diz se a diferença importa.

### `bootstrap_metric` (função)

```python
def bootstrap_metric(labels: pd.Series, scores: pd.Series, metric: str='average_precision', n_boot: int=1000, confidence: float=0.95, seed: int=0) -> dict[str, float]
```

Estimativa pontual e IC por bootstrap percentil de uma métrica de desempenho.

Reamostra as contas com reposição separadamente em fraude e normal
(bootstrap estratificado), para toda réplica ter a mesma proporção de
fraudes do dado original.

### `paired_comparison` (função)

```python
def paired_comparison(a: pd.Series, b: pd.Series, confidence: float=0.95) -> dict[str, float]
```

Compara duas abordagens medidas nas mesmas unidades (ex.: mesmas sementes).

Devolve a diferença média `a - b` com IC t de Student, o p-valor do
teste de Wilcoxon pareado (não paramétrico) e o do teste t pareado.

### `summarize_runs` (função)

```python
def summarize_runs(runs: pd.DataFrame, metric: str, confidence: float=0.95, by: list[str]=()) -> pd.DataFrame
```

Média, desvio e IC t de `metric` por (atributos, modelo) em várias execuções.

`by` acrescenta colunas ao agrupamento (ex.: `["cenario"]`); nesse caso
a ordenação pela média é feita dentro de cada grupo.

### `compare_runs` (função)

```python
def compare_runs(runs: pd.DataFrame, comparisons: list[tuple[str, str]], metrics: list[str], by: list[str]=(), unit: str='semente', between: str='atributos') -> pd.DataFrame
```

Testes pareados, semente a semente, entre conjuntos de atributos ou entre modelos.

`runs` tem uma linha por (semente, atributos, modelo), como a saída de
`pixfraud.experiment.run_seeds`; `unit` é a coluna que identifica a
repetição (as janelas de tempo, num dataset externo). Com
`between="atributos"` (padrão), os pares `(a, b)` de `comparisons` são
conjuntos de atributos, comparados dentro de cada modelo; com
`between="modelo"`, são modelos, comparados dentro de cada conjunto. Um
par que não aparece num grupo é pulado. Aplica `paired_comparison` a `a - b`.
Cada métrica (dentro de cada grupo de `by`) é uma família de testes, e
a correção de Holm vale dentro dela: com 10 sementes, o menor p possível
no Wilcoxon exato é 2/1024 ≈ 0,002, e corrigir por todas as métricas juntas
tornaria qualquer diferença "não significativa".

### `null_model_test` (função)

```python
def null_model_test(graph: nx.DiGraph, statistic: Callable[[nx.DiGraph], float], n_samples: int=100, seed: int=0) -> dict[str, float]
```

Compara `statistic(graph)` com grafos aleatórios de mesmos graus de entrada e saída.

O modelo nulo é o modelo de configuração direcionado: cada conta mantém
exatamente seus graus e as ligações são sorteadas (laços e arestas
paralelas são descartados). Devolve o valor observado, a média e o desvio
do nulo, o escore z e o p-valor empírico bilateral.

### `contingency_test` (função)

```python
def contingency_test(a: pd.Series, b: pd.Series) -> dict
```

Teste qui-quadrado de independência entre duas variáveis categóricas, com o V de Cramér.

Numa tabela 2×2 acrescenta o teste exato de Fisher (que vale também com
contagens pequenas, como as fraudes num top-k) e a razão de chances.

### `epsilon_squared_label` (função)

```python
def epsilon_squared_label(eps2: float) -> str
```

Rótulo do ε² do Kruskal-Wallis (limiares usuais de η²: 0,01, 0,06 e 0,14).

### `kruskal_groups` (função)

```python
def kruskal_groups(features: pd.DataFrame, groups: pd.Series) -> pd.DataFrame
```

Kruskal-Wallis de cada atributo entre os grupos de `groups` (ex.: o papel da conta).

Generaliza o `compare_groups` para três ou mais grupos **independentes**.
Devolve H, p, p ajustado por Holm (entre os atributos), o tamanho de efeito
ε² = H / (n − 1) e o grupo de maior mediana. Um resultado significativo diz
que *algum* grupo difere; `dunn_posthoc` diz quais.

### `dunn_posthoc` (função)

```python
def dunn_posthoc(values: pd.Series, groups: pd.Series) -> pd.DataFrame
```

Teste de Dunn (1964): que pares de grupos diferem, depois de um Kruskal-Wallis significativo.

Compara os postos médios de cada par usando a mesma ordenação do Kruskal-
Wallis, com a correção para empates, e ajusta os p-valores por Holm entre
os pares. `postos médios a - b` > 0: `a` tende a ter valores maiores.

### `friedman_models` (função)

```python
def friedman_models(runs: pd.DataFrame, metric: str, by: list[str]=(), unit: str='semente', between: str='modelo', alpha: float=0.05) -> tuple[pd.DataFrame, pd.DataFrame]
```

Teste de Friedman entre vários modelos medidos nas mesmas unidades (sementes).

É o equivalente pareado do Kruskal-Wallis: dentro de cada semente os
modelos são ordenados (posto 1 = maior `metric`), e o teste pergunta se
os postos médios diferem mais do que o acaso explicaria. Só entram as
sementes em que todos os modelos do grupo têm valor.

Devolve duas tabelas, uma linha por grupo de `by`:

* testes: nº de modelos (k) e de sementes (N), χ², p, W de Kendall
  (concordância entre as sementes, de 0 a 1) e a **diferença crítica** de
  Nemenyi, CD = q_α · √(k(k+1) / 6N): dois modelos cujos postos médios
  diferem menos que CD não se distinguem (Demšar, 2006);
* postos: o posto médio de cada modelo, do melhor para o pior.

### `permutation_test_metric` (função)

```python
def permutation_test_metric(labels: pd.Series, scores: pd.Series, metric: str='average_precision', n_perm: int=1000, seed: int=0) -> dict[str, float]
```

O modelo é melhor que o acaso? Teste de permutação da métrica.

Embaralha o gabarito `n_perm` vezes, recalcula a métrica e conta quantas
vezes ela igualou ou superou a real: p = (b + 1) / (n_perm + 1). Vale para
qualquer métrica de `METRICS`; na AP, a média nula fica perto da taxa de fraude.

### `topk_hypergeom` (função)

```python
def topk_hypergeom(labels: pd.Series, scores: pd.Series, k: int | None=None) -> dict[str, float]
```

Fraudes entre as `k` contas de maior escore contra um sorteio de `k` contas.

Sob a hipótese nula (o top-k é um sorteio), o nº de fraudes no top-k segue
a distribuição hipergeométrica; p = P(X ≥ observado). `k` padrão: o nº de fraudes.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _precision_at_k(y: np.ndarray, scores: np.ndarray, k: int | None=None) -> float`: Fração de fraudes entre as `k` contas de maior escore (`k` padrão: nº de fraudes).

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`scripts/01_dados/validar_realismo.py`](scripts.01_dados.md)
- [`scripts/02_exploracao/inferencia_atributos.py`](scripts.02_exploracao.md)
- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
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
- [`tests/test_stats.py`](testes.md)
