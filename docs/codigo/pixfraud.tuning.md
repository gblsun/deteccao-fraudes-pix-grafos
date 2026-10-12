---
tags: [codigo]
---

# `pixfraud.tuning`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/tuning/__init__.py`](../../src/pixfraud/tuning/__init__.py) · [mapa do código](mapa-do-codigo.md)

Otimização de hiperparâmetros: busca em grade que se amplia sozinha, escolhida em redes de **validação**.

O gabarito é usado para dar nota a cada combinação de hiperparâmetros, então a
escolha não pode ser feita nas mesmas redes em que os modelos são avaliados
depois: a nota sairia inflada, como estudar com a prova que vai cair. Por
isso `scripts/03_modelos/otimizar_hiperparametros.py` gera redes com sementes próprias
(a partir de `VALIDATION_SEED`), escolhe os hiperparâmetros nelas e grava a
configuração; os estudos de avaliação usam as sementes 1, 2, 3..., que nunca
entram na escolha.

* `search_space`: as grades (de `configs/busca_hiperparametros.yaml`) e a
  ampliação de uma grade quando o vencedor cai na ponta;
* `search`: a nota (average precision) de cada candidato e a escolha do vencedor.

A busca roda em rodadas: na primeira, a grade inteira; nas seguintes, só os
valores novos dos modelos cujo vencedor caiu na ponta da lista. Termina quando
nenhum vencedor está numa ponta que ainda possa crescer.

## Quem usa este módulo

- [`scripts/03_modelos/otimizar_hiperparametros.py`](scripts.03_modelos.md)
- [`tests/test_tuning.py`](testes.md)
