---
tags: [glossario]
---

# Teste de Kruskal-Wallis

Teste não paramétrico que compara **três ou mais grupos** pela ordem dos valores: todas as
observações são ordenadas juntas, e a estatística $H$ mede o quanto as ordens médias de cada
grupo se afastam da ordem média geral. É a generalização do
[teste de Mann-Whitney](mann-whitney.md) para mais de dois grupos.

**Serve para classificar contas? Não.** É um teste de hipótese sobre **grupos**: responde se
a distribuição de um atributo é diferente entre eles (por exemplo, normal, comércio,
laranja, intermediário e coletor). Não dá escore nem rótulo para *uma* conta, e precisa
dos grupos já conhecidos, ou seja, do gabarito. Mesmo um atributo muito diferente entre os
grupos tem distribuições que se sobrepõem, então separar grupos não garante acertar conta
por conta. Para isso existem os [modelos](../../src/pixfraud/models/mapa-dos-modelos.md).

**Para que serve aqui.** Escolher e justificar atributos: "o
[tempo de permanência](tempo-de-permanencia.md) difere entre os papéis das contas?".
Um resultado significativo diz que *algum* grupo difere; o teste de Dunn, com a
[correção de Holm](correcao-de-holm.md), diz quais pares diferem.

**Cuidados.**
- Com só dois grupos (fraude ou não; comércio ou não), ele equivale ao Mann-Whitney, que o
  projeto já usa.
- Com milhares de contas, quase tudo dá significativo: reporte também o tamanho do efeito
  ($\varepsilon^2 = H / (n - 1)$), como se faz com o [delta de Cliff](delta-de-cliff.md).

**No projeto.** [`stats.kruskal_groups`](../../src/pixfraud/stats.py) (H, ε² e Holm por
atributo) e o post-hoc [`stats.dunn_posthoc`](teste-de-dunn.md), usados por
[`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py) (atributos
entre os 6 papéis), por [`avaliar_modelos.py`](../../scripts/03_modelos/avaliar_modelos.py)
(a AP de cada modelo entre os cenários) e por
[`investigar_falsos_positivos.py`](../../scripts/05_interpretacao/investigar_falsos_positivos.py)
(o escore de risco entre os papéis). O par de dois grupos é `stats.compare_groups`. Para
comparar **modelos**, que rodam nas mesmas sementes, o teste certo é o
[Friedman](friedman-e-nemenyi.md), e não o Kruskal-Wallis. Testes que verificam se um modelo
classifica bem estão em [testes para classificadores](testes-para-classificadores.md).
