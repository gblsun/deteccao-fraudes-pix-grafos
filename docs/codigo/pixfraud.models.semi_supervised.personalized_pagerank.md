---
tags: [codigo]
---

# `pixfraud.models.semi_supervised.personalized_pagerank`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/semi_supervised/personalized_pagerank.py`](../../src/pixfraud/models/semi_supervised/personalized_pagerank.py) · [mapa do código](mapa-do-codigo.md)

PageRank personalizado ("culpa por associação"): a suspeita parte das fraudes já conhecidas.

## Classes e funções

### `propagate_risk` (função)

```python
def propagate_risk(graph: nx.DiGraph, seeds: Iterable, alpha: float=0.85, direction: str='both', weight: str | None='amount', relative: bool=False) -> pd.Series
```

Culpa por associação: PageRank personalizado a partir das contas `seeds`.

A "moeda" do PageRank sempre salta de volta para uma das contas-semente,
então o escore mede o quão perto (e por quantos caminhos) cada conta está
delas. `direction`: `"forward"` segue o dinheiro (para onde as sementes
pagaram), `"backward"` volta à origem (quem pagou as sementes) e
`"both"` ignora o sentido, o que alcança as laranjas "irmãs" que repassam
para o mesmo intermediário. Com `relative=True` o escore é dividido pelo
PageRank comum, para não favorecer só as contas muito conectadas
(como comércios).

## Quem usa este módulo

- [`pixfraud.models.semi_supervised`](pixfraud.models.semi_supervised.md)
