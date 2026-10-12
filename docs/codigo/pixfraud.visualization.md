---
tags: [codigo]
---

# `pixfraud.visualization`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/visualization.py`](../../src/pixfraud/visualization.py) · [mapa do código](mapa-do-codigo.md)

Visualizações dos grafos.

* `draw_graph`, `to_html` e `save_graph`: desenhar e exportar grafos
  pequenos (estudo, padrões de fraude, vizinhança de uma conta);
* `plot_heat_graph` e `plot_risk_heatmap`: interpretar os resultados dos
  detectores. Os escores de modelos diferentes têm escalas diferentes, por
  isso as cores usam o percentil do risco (0 = menos suspeita, 1 = mais);
* `plot_value_matrix`: tabela colorida de resultados (conjunto de atributos
  × cenário, tipologia × modelo...), com o valor escrito em cada célula.

## Classes e funções

### `model_color` (função)

```python
def model_color(model: str) -> str
```

Cor fixa de um modelo nas figuras (cinza-médio para um modelo sem cor definida).

### `model_label` (função)

```python
def model_label(model: str) -> str
```

Nome legível de um modelo, o mesmo em todas as figuras e tabelas.

### `format_number` (função)

```python
def format_number(value: float, digits: int=2) -> str
```

Número com vírgula decimal, como no resto da documentação (`0,58`).

### `format_ci` (função)

```python
def format_ci(mean: float, low: float, high: float, digits: int=2) -> str
```

Média e intervalo de confiança no formato único dos resultados: `0,58 [0,52; 0,63]`.

### `flow_layout` (função)

```python
def flow_layout(graph: nx.DiGraph) -> dict
```

Posiciona os vértices da esquerda para a direita, no sentido do dinheiro.

Só vale para grafos direcionados acíclicos: cada coluna é uma "geração"
topológica (quem só envia fica à esquerda, quem só recebe à direita).

### `draw_graph` (função)

```python
def draw_graph(graph: nx.Graph, color_by='role', layout='auto', edge_labels: str | None='amount', node_labels: bool=True, ax: plt.Axes | None=None, seed: int=42, cmap: str=CMAP, title: str | None=None) -> plt.Axes
```

Desenho estático pensado para grafos pequenos (até ~100 vértices).

`color_by`: nome de um atributo categórico dos vértices (`"role"` usa
as cores de `ROLE_COLORS`), uma `pd.Series` numérica indexada pelos
vértices (ex.: um escore de risco) ou `None`.
`layout`: `"auto"` (fluxo da esquerda para a direita se o grafo for
acíclico, senão Kamada-Kawai), `"flow"`, `"spring"`, `"circular"`,
`"kamada_kawai"`, `"shell"` ou um dicionário `{vértice: (x, y)}`.
`edge_labels`: atributo das arestas escrito sobre elas (ex.:
`"amount"`), ou `None`.

### `to_html` (função)

```python
def to_html(graph: nx.Graph, path: str | Path, color_by='role', title: str='Grafo de transações', cmap: str=CMAP) -> Path
```

Salva uma visualização interativa em HTML (arrastar, zoom, passar o mouse).

Abre em qualquer navegador; precisa de internet para carregar a biblioteca
vis-network. Passe o mouse sobre um vértice para ver papel, graus e
valores; o tamanho do vértice é proporcional ao grau. Para a rede inteira
(milhares de contas), use `pixfraud.explorer`.

### `graph_html` (função)

```python
def graph_html(graph: nx.Graph, color_by='role', title: str='Grafo de transações', cmap: str=CMAP) -> str
```

O HTML interativo de `to_html` como texto (para embutir, por exemplo, no app Streamlit).

### `save_graph` (função)

```python
def save_graph(graph: nx.Graph, path: str | Path, **draw_kwargs) -> Path
```

Salva o grafo no formato indicado pela extensão do arquivo.

* `.png`, `.svg`, `.pdf`: desenho estático (`draw_graph`);
* `.html`: visualização interativa (`to_html`);
* `.gexf`, `.graphml`: para abrir no Gephi ou em outras ferramentas.

`draw_kwargs` são repassados a `draw_graph` ou `to_html`.

### `plot_heat_graph` (função)

```python
def plot_heat_graph(graph: nx.DiGraph, risk: pd.Series, top_k: int=10, max_neighbors: int=8, fraud: pd.Series | None=None, ax: plt.Axes | None=None, seed: int=42) -> plt.Axes
```

Grafo de calor: os `top_k` vértices mais suspeitos e sua vizinhança.

A cor de cada vértice é o seu percentil de risco (vértices "quentes" em
vermelho) e o tamanho é o grau no subgrafo desenhado. De cada vértice
suspeito são mostrados no máximo `max_neighbors` vizinhos, os de maior
risco. Se `fraud` (rótulos verdadeiros) for informado, as contas
fraudulentas ganham contorno preto, o que ajuda a ver acertos e erros.

### `plot_risk_heatmap` (função)

```python
def plot_risk_heatmap(features: pd.DataFrame, risk: pd.Series, top_k: int=25, fraud: pd.Series | None=None, ax: plt.Axes | None=None) -> plt.Axes
```

Heatmap de risco: por que cada conta foi considerada suspeita.

As linhas são as `top_k` contas de maior risco (em ordem decrescente) e
as colunas são os atributos, coloridos pelo percentil do valor em relação a
todas as contas. Contas fraudulentas (se `fraud` for informado) são
marcadas com `*`.

### `explain_account` (função)

```python
def explain_account(graph: nx.DiGraph, features: pd.DataFrame, risk: pd.Series, account, fraud: pd.Series | None=None, max_neighbors: int=12, color_by='role') -> plt.Figure
```

Ficha da conta: por que ela foi considerada suspeita?

* à esquerda, a vizinhança (as `max_neighbors` contas com quem ela mais
  movimentou dinheiro);
* à direita, o percentil de cada atributo da conta em relação a todas as
  contas (barras perto de 0 ou de 1 são os valores extremos que chamaram
  a atenção do detector);
* embaixo, a posição da conta no ranking de risco.

### `plot_value_matrix` (função)

```python
def plot_value_matrix(matrix: pd.DataFrame, cmap=SEQUENTIAL_CMAP, vmin: float=0.0, vmax: float=1.0, fmt: str='{:.2f}', ax: plt.Axes | None=None)
```

Matriz de resultados: uma célula colorida por valor, com o número escrito nela.

As células têm 2px de respiro entre si; o texto fica branco nas células
escuras. Os rótulos vêm do índice (linhas) e das colunas de `matrix`
(troque-os depois com `ax.set_xticks` se precisar). Devolve a malha,
para a barra de cores.

### `plot_model_intervals` (função)

```python
def plot_model_intervals(summary: pd.DataFrame, ax: plt.Axes, baseline: float | None=None, groups: dict[str, str] | None=None, xlabel: str='average precision (média e IC 95%)', xlim: tuple[float, float]=(0.0, 1.0), group_labels: bool=True) -> None
```

Um modelo por linha: média e IC 95%, na cor fixa do modelo, de cima para baixo.

`summary` tem os índices = modelos (na ordem desejada) e as colunas
`mean`, `ic_inferior` e `ic_superior` (a saída de
`stats.summarize_runs`). `baseline` desenha a linha "ao acaso" (a taxa de
fraude: uma ordenação aleatória tem AP igual a ela). `groups` (modelo ->
família) separa as famílias com faixas de fundo alternadas e o nome da
família à direita. É o formato padrão dos resultados de modelos.

### `plot_test_statistic` (função)

```python
def plot_test_statistic(ax: plt.Axes, dist, observed: float, name: str, alpha: float=0.05, two_sided: bool=True, null_sample: np.ndarray | None=None) -> None
```

A distribuição da estatística sob a hipótese nula, com a zona crítica e o valor observado.

`dist` é uma distribuição do `scipy.stats` já congelada (normal, t, χ²);
com `null_sample` (o nulo de uma permutação), desenha o histograma dele e
a zona crítica sai dos quantis empíricos. As caudas de `alpha` ficam
sombreadas; o valor observado é a linha vertical. Um valor muito além da
escala vira uma seta na borda, com o número escrito.

### `plot_normality` (função)

```python
def plot_normality(ax_hist: plt.Axes, ax_qq: plt.Axes, values, name: str) -> float
```

Os dados contra a curva normal: histograma com a normal ajustada e o Q-Q plot.

Devolve o p do teste de Shapiro-Wilk (até 5 000 valores, sorteados se houver
mais). Cauda pesada aparece como pontos fugindo da reta no Q-Q plot, e é o
motivo de o projeto usar testes não paramétricos.

### `plot_critical_difference` (função)

```python
def plot_critical_difference(ranks: pd.DataFrame, critical: float, ax: plt.Axes, between: str='modelo') -> None
```

Postos médios do teste de Friedman com a diferença crítica de Nemenyi.

`ranks` é a tabela de postos de `stats.friedman_models` (um grupo).
Cada modelo é um ponto no seu posto médio (1 = melhor), com uma barra de
± CD/2: **dois modelos cujas barras não se tocam diferem**; os que se tocam
não se distinguem com estas sementes. Ganham cor os modelos que não se
distinguem do primeiro colocado.

### `plot_differences` (função)

```python
def plot_differences(comparisons: pd.DataFrame, ax: plt.Axes, xlabel: str='diferença de AP (A − B), IC 95%', alpha: float=0.05) -> None
```

Gráfico de diferenças: uma comparação "A − B" por linha, com IC 95% e o placar.

`comparisons` é a saída de `stats.compare_runs` (uma métrica). Verde:
A melhor; vermelho: B melhor; cinza: sem diferença clara. Só ganha cor a
diferença com p de Wilcoxon corrigido por Holm abaixo de `alpha` (com
poucas sementes, nada ganha cor, e isso é o certo). À direita, "vence em X
de N" e o p. É o formato padrão dos comparativos em todos os estudos.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _layout(graph: nx.Graph, layout, seed: int) -> dict`: Posições dos vértices: um dicionário pronto ou um dos layouts de `LAYOUTS`.
- `def _node_colors(graph: nx.Graph, color_by, cmap: str=CMAP) -> tuple[dict, dict]`: Cor (hex) de cada vértice e itens de legenda `{categoria: cor}`.
- `def _format_amount(value: float) -> str`: Valor em reais sem casas decimais, com ponto de milhar.
- `def _serializable(value)`: Valor que o JSON aceita: tipos simples ou texto.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/criar_grafo.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/inferencia_atributos.py`](scripts.02_exploracao.md)
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
- [`scripts/ferramentas/gerar_ilustracoes.py`](scripts.ferramentas.md)
- [`scripts/ferramentas/ilustrar_grafos_de_conhecimento.py`](scripts.ferramentas.md)
- [`scripts/ferramentas/ilustrar_testes.py`](scripts.ferramentas.md)
- [`tests/test_evaluation.py`](testes.md)
- [`tests/test_patterns.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
