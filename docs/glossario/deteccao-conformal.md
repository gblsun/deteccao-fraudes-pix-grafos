---
tags: [glossario]
---

# Detecção conformal (p-valor por conta)

A forma de transformar o escore de risco de qualquer modelo num **teste de hipótese para
cada conta**, com o erro controlado.

**Hipótese nula, para cada conta:** "esta conta vem da mesma distribuição das contas
normais". Com um conjunto de **calibração** de contas tidas como normais, o p-valor é a
fração delas com escore pelo menos tão alto quanto o da conta:

$$p(x) = \frac{1 + \#\{\,c \in \text{calibração} : s(c) \ge s(x)\,\}}{1 + |\text{calibração}|}$$

Um p-valor pequeno quer dizer que poucas contas normais são tão estranhas quanto esta, e
ela é marcada. Não depende de supor distribuição normal (gaussiana), nem do modelo: serve
para o [PCA](../../src/pixfraud/models/unsupervised/statistical/pca.py), o kNN, o
autoencoder ou o [Isolation Forest](isolation-forest.md).

**Controle de alarmes falsos.** Com milhares de contas, testar cada uma a 5% gera centenas
de alarmes falsos. A correção de **Benjamini-Hochberg** controla a *taxa de falsas
descobertas* (FDR): "das contas marcadas, no máximo 10% são legítimas". Ordene os
p-valores $p_{(1)} \le \dots \le p_{(m)}$ e marque as $k$ primeiras, com $k$ o maior índice
em que $p_{(k)} \le \frac{k}{m}\,q$. Para uma equipe que investiga contas, essa garantia é
mais útil que um escore solto.

**Diferença para os testes clássicos de outlier.** Grubbs e Dixon fazem a mesma pergunta,
mas supõem dados gaussianos e um atributo por vez, o que não combina com o Pix (cauda pesada
e muitos atributos).

**Cuidado.** A garantia vale se a calibração for de contas realmente normais e parecidas
com as testadas. Fraudes escondidas na calibração deixam o teste mais permissivo.

**No projeto.** Ainda não implementado: ver a ideia
[detecção conformal com controle de alarmes falsos](../futuro/deteccao-conformal-com-fdr.md).
Outros testes estão em [testes para classificadores](testes-para-classificadores.md).
