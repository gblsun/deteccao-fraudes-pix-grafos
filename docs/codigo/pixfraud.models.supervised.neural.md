---
tags: [codigo]
---

# `pixfraud.models.supervised.neural`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/neural/__init__.py`](../../src/pixfraud/models/supervised/neural/__init__.py) · [mapa do código](mapa-do-codigo.md)

Redes neurais **para grafos** supervisionadas (precisam do `torch`, extra `gnn`).

* `graphsage`: GraphSAGE própria, com todos os rótulos ou só com as fraudes conhecidas;
* `graphsage_directed`: GraphSAGE com PyTorch Geometric, uma convolução por sentido do Pix.

Sem o `torch` os módulos ainda importam; as funções avisam o que instalar quando chamadas.

## Quem usa este módulo

Nenhum outro arquivo importa este módulo.
