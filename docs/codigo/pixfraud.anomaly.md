---
tags: [codigo]
---

# `pixfraud.anomaly`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/anomaly.py`](../../src/pixfraud/anomaly.py) · [mapa do código](mapa-do-codigo.md)

Detectores de anomalia não supervisionados aplicados aos atributos das contas.

Os modelos moraram aqui até serem separados, um arquivo por modelo, em
`pixfraud.models.unsupervised` (ver `pixfraud.models`). Este módulo só
reexporta o que estava aqui, para scripts, notebooks e notas antigos
continuarem funcionando; código novo deve importar de `pixfraud.models`.

## Quem usa este módulo

- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`scripts/04_avaliacao/avaliar_atributos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_cenarios.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_deteccao_online.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_externo.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_fraudar.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn_rotulos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_propagacao.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_robustez.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_sementes.py`](scripts.04_avaliacao.md)
- [`scripts/05_interpretacao/investigar_falsos_positivos.py`](scripts.05_interpretacao.md)
- [`scripts/ferramentas/ilustrar_testes.py`](scripts.ferramentas.md)
- [`tests/test_anomaly.py`](testes.md)
- [`tests/test_experiment.py`](testes.md)
- [`tests/test_online.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
- [`tests/test_scripts.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
