---
tags: [codigo]
---

# `pixfraud.models.unsupervised.graph.fraudar`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/graph/fraudar.py`](../../src/pixfraud/models/unsupervised/graph/fraudar.py) · [mapa do código](mapa-do-codigo.md)

FRAUDAR (Hooi et al., 2016): contas em blocos densos, como uma quadrilha, ficam no topo.

Olha só para a estrutura do grafo, sem a tabela de atributos.

## Classes e funções

### `fraudar` (função)

```python
def fraudar(graph: nx.Graph, contamination: float=0.05) -> Detection
```

FRAUDAR como escore por conta (`communities.peeling_scores`).

O núcleo ponderado da remoção gulosa com os pesos do FRAUDAR: contas em
blocos densos, como uma quadrilha em que várias laranjas mandam para os
mesmos intermediários, ficam no topo; os pesos fazem Pix para comércios
muito procurados valerem pouco, e assim "pagar a padaria" não camufla a
quadrilha. O rótulo binário marca a fração `contamination` de maior
escore. Não usa valores nem horários, só quem pagou quem.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.graph`](pixfraud.models.unsupervised.graph.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
