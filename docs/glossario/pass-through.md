---
tags: [glossario]
---

# Pass-through (dinheiro que atravessa a conta)

Fração do dinheiro que entra e sai da mesma conta:

$$\text{pass\_through} = \frac{\min(\text{recebido},\ \text{enviado})}{\max(\text{recebido},\ \text{enviado})}$$

Vale ~1 quando quase tudo o que chega é repassado, e ~0 quando a conta só recebe (uma
coletora) ou só paga.

**No projeto.** Atributo tabular ([`features.py`](../../src/pixfraud/features.py)), com
efeito grande em todos os cenários ([delta de Cliff](delta-de-cliff.md) entre 0,60 e 0,66).

Veja também: [conta laranja](conta-laranja.md).
