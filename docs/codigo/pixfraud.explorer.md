---
tags: [codigo]
---

# `pixfraud.explorer`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/explorer.py`](../../src/pixfraud/explorer.py) · [mapa do código](mapa-do-codigo.md)

Explorador interativo da rede inteira: uma página HTML com sigma.js (WebGL).

Mostra todas as contas e Pix de uma vez, com ferramentas dinâmicas: busca de
conta, filtro por papel, cor por papel / risco (de um ou vários modelos, com
seletor) / comunidade, clique para ver a
vizinhança e os detalhes de uma conta, e uma linha do tempo que mostra a rede
crescendo dia a dia (com botão de "tocar").

O posicionamento é calculado em Python (`community_layout`): cada
comunidade (Louvain) é desenhada separadamente e as comunidades são dispostas
em espiral, com as contas da quadrilha (laranjas, intermediários e coletoras)
juntas no centro. As relações são setas de quem pagou para quem recebeu. O navegador só desenha, o que mantém a página leve mesmo com
dezenas de milhares de arestas.

Uso típico:

    save_network_explorer("reports/estudos/rede.html", graph, transactions=tx,
                          roles=papel, risk=escores)

A página abre em qualquer navegador e precisa de internet para carregar as
bibliotecas (sigma.js e graphology, via cdnjs).

## Classes e funções

### `community_layout` (função)

```python
def community_layout(graph: nx.Graph, communities: pd.Series, seed: int=42, center: Iterable=()) -> dict
```

Posições que deixam as comunidades visíveis.

Cada comunidade recebe um disco de raio proporcional à raiz do seu tamanho
e é desenhada por dentro com o layout de molas (spring). Os discos são
dispostos numa espiral de girassol (ângulo áureo), do maior para o menor,
sem se sobrepor.

`center`: contas que saem das suas comunidades e ficam juntas num disco no
centro, com folga (por exemplo, as contas das quadrilhas). Assim o dinheiro
que chega a elas aparece como setas convergindo para o meio, em vez de
riscos cruzando a rede de um lado a outro.

### `explorer_payload` (função)

```python
def explorer_payload(graph: nx.DiGraph, transactions: pd.DataFrame | None=None, roles: pd.Series | None=None, risk: pd.Series | dict[str, pd.Series] | None=None, communities: pd.Series | None=None, positions: dict | None=None, seed: int=42, center_roles: Iterable[str]=CENTER_ROLES, risk_groups: dict[str, str] | None=None, labels: pd.Series | None=None, initial_model: int=0) -> dict
```

Dados compactos (listas de números) que a página do explorador consome.

`labels` (o gabarito: `True` para conta fraudulenta) liga o modo de cor
"Acertos" e a caixa de desempenho (AP e precision@k do modelo escolhido).
`initial_model` é a posição, em `risk`, do modelo que a página abre selecionado.

As contas com papel em `center_roles` (as da quadrilha) ficam no centro do
desenho (ver `community_layout`); passe `()` para desligar.

`risk`: um escore por conta, ou vários, como `{nome do modelo: escores}`;
com vários, a página ganha um seletor de modelo, e `risk_groups`
(`{nome do modelo: grupo}`, ex.: "Supervisionados") separa a lista em
grupos. Cada escore vira percentil, para que modelos de escalas diferentes
usem a mesma escala de cor.

### `network_explorer_html` (função)

```python
def network_explorer_html(graph: nx.DiGraph, transactions: pd.DataFrame | None=None, roles: pd.Series | None=None, risk: pd.Series | dict[str, pd.Series] | None=None, communities: pd.Series | None=None, title: str='Rede Pix', subtitle: str='', positions: dict | None=None, seed: int=42, center_roles: Iterable[str]=CENTER_ROLES, risk_groups: dict[str, str] | None=None, labels: pd.Series | None=None, initial_model: int=0) -> str
```

Página HTML completa do explorador (ver `save_network_explorer`).

### `save_network_explorer` (função)

```python
def save_network_explorer(path: str | Path, graph: nx.DiGraph, **kwargs) -> Path
```

Salva o explorador em `path` (.html). Aceita os parâmetros de `network_explorer_html`.

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _place_center(sub: nx.Graph, spacing: float, positions: dict, seed: int) -> float`: Põe cada grupo ligado de `sub` (uma quadrilha, em geral) num círculo em volta da origem.
- `def _free_spot(placed: list, radius: float, spacing: float, i: int) -> np.ndarray`: Primeiro ponto da espiral de girassol em que um disco de `radius` não encosta nos já colocados.
- `def _first_days(graph: nx.DiGraph, transactions: pd.DataFrame | None) -> tuple[dict, list]`: Dia (índice) do primeiro Pix de cada aresta e a lista de dias do período.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`tests/test_explorer.py`](testes.md)
