---
tags: [codigo]
---

# `pixfraud.features`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/features.py`](../../src/pixfraud/features.py) · [mapa do código](mapa-do-codigo.md)

Atributos por conta usados pelos detectores de anomalia.

Os atributos são separados em grupos para permitir a comparação entre a
abordagem tabular e a abordagem baseada em grafos:

* tabulares: agregados das transações de cada conta, sem olhar para a
  estrutura da rede;
* temporais: velocidade de repasse e picos de recebimento (`pixfraud.temporal`);
* de grafo: métricas estruturais clássicas calculadas sobre o grafo;
* estruturais avançados: k-núcleo, participação entre comunidades e OddBall
  (`pixfraud.communities`).

## Classes e funções

### `tabular_features` (função)

```python
def tabular_features(transactions: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame
```

Agregados por conta, calculados diretamente da tabela de transações.

### `graph_features` (função)

```python
def graph_features(graph: nx.DiGraph, betweenness_k: int | None=500, seed: int=42) -> pd.DataFrame
```

Métricas estruturais de cada vértice do grafo de transações.

`betweenness_k` limita o cálculo da intermediação a `k` vértices de
origem sorteados (aproximação de Brandes); `None` calcula o valor exato,
que fica lento em grafos grandes.

### `build_features` (função)

```python
def build_features(transactions: pd.DataFrame, accounts: pd.DataFrame, graph: nx.DiGraph, betweenness_k: int | None=500, seed: int=42) -> pd.DataFrame
```

Tabela com todos os atributos (de todos os grupos), indexada por conta.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.online`](pixfraud.online.md)
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
- [`scripts/05_interpretacao/investigar_falsos_positivos.py`](scripts.05_interpretacao.md)
- [`scripts/ferramentas/ilustrar_testes.py`](scripts.ferramentas.md)
- [`tests/test_experiment.py`](testes.md)
- [`tests/test_features.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
