---
tags: [glossario]
---

# K-núcleo (core number)

O maior $k$ tal que a conta pertence a um subgrafo em que todo mundo tem grau $\ge k$
dentro dele (decomposição em k-núcleos, retirando iterativamente os vértices de menor
grau).

**Como ler.** Núcleo alto = a conta está numa parte densamente conectada da rede
(comunidade real). Núcleo baixo = conta periférica, ligada de leve à rede — o perfil
típico de uma conta laranja recém-criada.

**No projeto.** [`communities.core_numbers`](../../src/pixfraud/communities.py), parte do
conjunto `grafo_avancado`. Um dos atributos que mais faz falta na
[ablação](../resultados.md) (queda de até 0,09 de AP ao removê-lo).
