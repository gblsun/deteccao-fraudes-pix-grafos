---
tags: [codigo]
---

# `pixfraud.models.semi_supervised`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/semi_supervised/__init__.py`](../../src/pixfraud/models/semi_supervised/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos **semi-supervisionados**: usam só as poucas fraudes já conhecidas, como um banco de verdade.

No Pix real, parte das fraudes vira conhecida quando as vítimas contestam
(MED). Estes modelos não são treinados: espalham a suspeita dessas contas pelo
grafo, para achar as que ainda não foram descobertas.

* `propagate_risk`: PageRank personalizado ("culpa por associação");
* `label_spreading`: o mesmo, usando também as contas sabidamente legítimas.

## Quem usa este módulo

- [`pixfraud.flow`](pixfraud.flow.md)
- [`tests/test_tuning.py`](testes.md)
