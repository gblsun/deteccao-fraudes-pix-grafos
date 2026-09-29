---
tags: [glossario]
---

# FRAUDAR

Algoritmo de Hooi et al. (2016) para achar **blocos densos** num grafo: grupos de contas
que se ligam muito mais entre si do que o normal, como uma quadrilha que faz a mesma
vítima pagar várias laranjas, que repassam entre si. Não usa rótulos nem atributos, só a
estrutura.

Parte do [subgrafo mais denso](k-nucleo.md) pelo algoritmo guloso de Charikar (tira, uma a
uma, a conta de menor grau e guarda o momento de maior densidade = peso total / nº de
contas), com um peso que resiste a **camuflagem**: cada aresta $u \to v$ vale

$$w(u \to v) = \frac{1}{\log(d^-(v) + 5)}$$

em que $d^-(v)$ é o grau de entrada de $v$. Pagar a padaria (que recebe de todo mundo)
quase não conta, então uma quadrilha não se esconde "parecendo normal".

Depois de achar um bloco, o FRAUDAR tira essas contas e procura de novo: uma quadrilha por
bloco, do mais denso para o menos denso.

**Cuidado.** No Pix, a rede legítima também é densa (círculos de contatos). O primeiro
"bloco" costuma ser quase a rede inteira, e com muitas pessoas quase inativas a rede se
parte em vários círculos pequenos e densos, que competem com as quadrilhas. Por isso o
escore do projeto ignora blocos com mais de 5% das contas.

**No projeto.** [`communities.fraudar_blocks` e `fraudar_scores`](../../src/pixfraud/communities.py),
avaliados por [`scripts/avaliar_fraudar.py`](../../scripts/avaliar_fraudar.py); resultados
em [resultados](../resultados.md). Ver também [comunidades e
modularidade](comunidades-e-modularidade.md) e [egonet e OddBall](egonet-e-oddball.md).
