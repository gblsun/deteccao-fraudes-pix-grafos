---
tags: [glossario]
---

# Coeficiente de participação

Quanto as ligações de uma conta se espalham por [comunidades](comunidades-e-modularidade.md)
diferentes, em vez de ficarem dentro da sua própria comunidade:

$$P(v) = 1 - \sum_{c} \Bigl(\frac{k_{v,c}}{k_v}\Bigr)^2$$

onde $k_{v,c}$ é o número de vizinhos de $v$ na comunidade $c$. Vale 0 se todos os
vizinhos estão na mesma comunidade, e cresce conforme eles se espalham.

**Como ler.** Contas-ponte entre grupos (como um intermediário que liga a comunidade da
vítima à comunidade da quadrilha) têm participação mais alta.

**No projeto.** [`communities.participation_coefficient`](../../src/pixfraud/communities.py).
Efeito pequeno nos nossos dados ($\delta$ entre 0,26 e 0,43): as quadrilhas simuladas não
cruzam tantas comunidades quanto se poderia esperar.
