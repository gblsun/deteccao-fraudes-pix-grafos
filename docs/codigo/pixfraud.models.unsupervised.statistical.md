---
tags: [codigo]
---

# `pixfraud.models.unsupervised.statistical`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/statistical/__init__.py`](../../src/pixfraud/models/unsupervised/statistical/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos **estatísticos**: a conta suspeita é rara segundo a distribuição dos atributos.

* `pca`: foge da correlação entre os atributos (componentes principais);
* `ecod`: está na cauda de vários atributos, cada um olhado sozinho.

## Quem usa este módulo

- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
