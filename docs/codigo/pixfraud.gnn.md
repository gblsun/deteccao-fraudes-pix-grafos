---
tags: [codigo]
---

# `pixfraud.gnn`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/gnn.py`](../../src/pixfraud/gnn.py) · [mapa do código](mapa-do-codigo.md)

Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch.

Os modelos moraram aqui até serem separados, um arquivo por modelo, em
`pixfraud.models`:

* `dominant_scores` (**não supervisionado**): `models.unsupervised.neural.dominant`;
* `sage_supervised_scores` e `sage_known_fraud_scores` (**supervisionado**
  e **poucos rótulos**): `models.supervised.neural.graphsage`;
* `graphsage_scores` (**supervisionado**, variante **direcionada**, com
  PyTorch Geometric): `models.supervised.neural.graphsage_directed`.

Este módulo só reexporta o que estava aqui, para scripts, notebooks e notas
antigos continuarem funcionando; código novo deve importar de `pixfraud.models`.

## Quem usa este módulo

- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`scripts/04_avaliacao/avaliar_atributos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn_rotulos.py`](scripts.04_avaliacao.md)
- [`scripts/reproduzir_tudo.py`](scripts.raiz.md)
- [`tests/test_gnn.py`](testes.md)
- [`tests/test_gnn_direcionada.py`](testes.md)
- [`tests/test_scripts.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
