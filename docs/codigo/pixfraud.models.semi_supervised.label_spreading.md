---
tags: [codigo]
---

# `pixfraud.models.semi_supervised.label_spreading`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/semi_supervised/label_spreading.py`](../../src/pixfraud/models/semi_supervised/label_spreading.py) · [mapa do código](mapa-do-codigo.md)

Label spreading (Zhou et al., 2004): fraudes **e** contas legítimas conhecidas espalham o rótulo pelo grafo.

## Classes e funções

### `label_spreading` (função)

```python
def label_spreading(graph: nx.DiGraph, positives: Iterable, negatives: Iterable=(), alpha: float=0.85, weight: str | None=None, max_iter: int=200, tol: float=1e-06) -> pd.Series
```

Propagação de rótulos com exemplos positivos **e negativos** (Zhou et al., 2004).

Cada conta começa com +1 (fraude conhecida), -1 (legítima conhecida) ou 0
(desconhecida), e a cada passo recebe a média dos vizinhos, normalizada
pelos graus (`S = D^{-1/2} W D^{-1/2}`), sem esquecer o valor inicial:
`F <- alpha * S F + (1 - alpha) * Y`. No fim, o escore diz de qual dos
dois lados a conta está mais perto no grafo.

A diferença para `propagate_risk` é usar também o que se sabe de bom: uma
conta ao lado de muitas legítimas conhecidas é puxada para baixo. O grafo é
tratado como não direcionado, e com `weight=None` cada par de contas pesa
1, para os comércios, com muitos Pix, não dominarem.

## Quem usa este módulo

- [`pixfraud.flow`](pixfraud.flow.md)
- [`pixfraud.models.semi_supervised`](pixfraud.models.semi_supervised.md)
- [`tests/test_tuning.py`](testes.md)
