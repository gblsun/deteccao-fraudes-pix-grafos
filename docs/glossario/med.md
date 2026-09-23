---
tags: [glossario]
---

# MED (Mecanismo Especial de Devolução)

Procedimento do Pix para devolver valores em casos de fraude ou falha operacional: a
vítima contesta pelo banco, que pode devolver o dinheiro **que ainda estiver** na conta
recebedora. Existe também o **bloqueio cautelar**, que segura valores suspeitos por até
72 horas enquanto o caso é analisado.

**Por que isso comanda a pesquisa.** Nos dados abertos do Banco Central (06/2025 a
04/2026), apenas **11% do valor contestado e aceito volta** à vítima; **51% não volta por
saldo insuficiente**, ou seja, o dinheiro já tinha saído da conta. Detectar não basta: é
preciso detectar **antes do repasse**.

**No projeto.** É o que a avaliação de [detecção a tempo](../../src/pixfraud/online.py)
mede, e a origem dos rótulos parciais usados na
[propagação de risco](propagacao-de-risco.md).

Veja também: [conta laranja](conta-laranja.md),
[tempo de permanência](tempo-de-permanencia.md).
