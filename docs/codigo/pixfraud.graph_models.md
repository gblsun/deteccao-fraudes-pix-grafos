---
tags: [codigo]
---

# `pixfraud.graph_models`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/graph_models.py`](../../src/pixfraud/graph_models.py) · [mapa do código](mapa-do-codigo.md)

Detectores que olham só para a estrutura do grafo, sem a tabela de atributos.

Os modelos (FRAUDAR e node2vec + Isolation Forest) moraram aqui até serem
separados em `pixfraud.models.unsupervised.fraudar` e `.node2vec`. Este
módulo só reexporta o que estava aqui, para scripts, notebooks e notas antigos
continuarem funcionando; código novo deve importar de `pixfraud.models`.

## Quem usa este módulo

- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`tests/test_graph_models.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
