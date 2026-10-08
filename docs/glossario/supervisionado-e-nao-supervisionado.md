---
tags: [glossario]
---

# Supervisionado e não supervisionado

A diferença está em **com o que o modelo aprende**.

| | Supervisionado | Não supervisionado |
|---|---|---|
| Precisa do gabarito para aprender? | sim, muitos exemplos | não |
| O que aprende | como é uma fraude | como é o normal |
| Pergunta | "isto parece com as fraudes que conheço?" | "isto é estranho?" |
| Ponto forte | preciso quando há bons exemplos | funciona sem rótulos; pode achar golpes novos |
| Ponto fraco | só reconhece o tipo de golpe que já viu | marca tudo que é raro, inclusive contas legítimas incomuns |

**O gabarito entra em dois momentos.** Para **dar a nota** (a
[average precision](average-precision.md)), ele é usado com todos os modelos, depois que
cada um monta a sua fila de risco. Para **aprender**, só com os supervisionados, e sempre em
[validação cruzada](validacao-cruzada.md): a conta avaliada nunca está no treino do modelo
que dá a nota dela.

**Por que a pesquisa aposta no não supervisionado.** No Pix real quase não há gabarito: o
banco só descobre parte das fraudes, e tarde, pelas contestações do [MED](med.md). Os
supervisionados entram como **teto**. Na rede sintética, o Random Forest chega a AP de
1,00 porque as laranjas do gerador formam uma combinação de atributos que nenhuma conta
legítima tem (repasse rápido, sem círculo de amigos, poucos destinos). Isso diz mais sobre a
rede sintética do que sobre o modelo.

**O meio-termo, semi-supervisionado.** Usa só as poucas fraudes já conhecidas e espalha a
suspeita pelo grafo ([propagação de risco](propagacao-de-risco.md)). Nos cenários
realistas, combinado com o DBSCAN, foi o que chegou mais perto do teto.

**No projeto.** As pastas `unsupervised/`, `semi_supervised/` e `supervised/` do
[mapa dos modelos](../../src/pixfraud/models/mapa-dos-modelos.md).
