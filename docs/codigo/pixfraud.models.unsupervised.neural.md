---
tags: [codigo]
---

# `pixfraud.models.unsupervised.neural`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/neural/__init__.py`](../../src/pixfraud/models/unsupervised/neural/__init__.py) · [mapa do código](mapa-do-codigo.md)

Redes neurais **de reconstrução**: aprendem a reconstruir as contas típicas e erram na suspeita.

* `autoencoder`: rede densa sobre a tabela de atributos (scikit-learn);
* `dominant`: autoencoder de grafo, que reconstrói também as ligações
  (PyTorch, extra `gnn`).

## Quem usa este módulo

- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
