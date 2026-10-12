---
tags: [codigo]
---

# `pixfraud.models.unsupervised.graph`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/graph/__init__.py`](../../src/pixfraud/models/unsupervised/graph/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos de **estrutura do grafo**: recebem o grafo, não a tabela de atributos.

* `fraudar`: contas num bloco denso, como uma quadrilha;
* `node2vec_isolation_forest`: posição rara num vetor aprendido de passeios aleatórios.

## Quem usa este módulo

- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
