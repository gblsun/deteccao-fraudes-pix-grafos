---
tags: [codigo]
---

# `pixfraud.models.unsupervised.isolation.isolation_forest`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/isolation/isolation_forest.py`](../../src/pixfraud/models/unsupervised/isolation/isolation_forest.py) · [mapa do código](mapa-do-codigo.md)

Isolation Forest (Liu, Ting e Zhou, 2008): a conta isolada com poucos cortes aleatórios é anômala.

## Classes e funções

### `isolation_forest` (função)

```python
def isolation_forest(features: pd.DataFrame, n_estimators: int=300, contamination: float | str='auto', max_samples: int | float | str='auto', max_features: float=1.0, seed: int=42) -> Detection
```

Isolation Forest: contas isoladas com poucas partições aleatórias são anômalas.

Cada árvore sorteia um atributo e um ponto de corte, repetidamente, até
isolar cada conta; a conta rara precisa de poucos cortes. `max_samples` é
quantas contas cada árvore vê (`"auto"` = até 256) e `max_features`, a
fração de atributos sorteada por árvore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.isolation`](pixfraud.models.unsupervised.isolation.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
