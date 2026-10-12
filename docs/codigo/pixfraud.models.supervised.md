---
tags: [codigo]
---

# `pixfraud.models.supervised`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/supervised/__init__.py`](../../src/pixfraud/models/supervised/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos **supervisionados**: aprendem com o gabarito (quem é fraude), sempre em validação cruzada.

Cada conta recebe a probabilidade dada por um modelo que **não viu o rótulo
dela** (`cross_validation.out_of_fold_scores`). Na pesquisa eles são um
teto: mostram até onde se chegaria se as respostas fossem conhecidas, o que
no Pix real quase nunca acontece.

* `trees/`: `random_forest` e `gradient_boosting`, sobre a tabela de atributos;
* `neural/`: `graphsage` e `graphsage_directed`, redes neurais para grafos
  (precisam do `torch`).

`SUPERVISED` registra os de árvores, todos com a assinatura
`(features, labels, seed=42, folds=5, **hiperparâmetros) -> pd.Series`.

## Quem usa este módulo

- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.models`](pixfraud.models.md)
