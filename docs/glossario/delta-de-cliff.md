---
tags: [glossario]
---

# Delta de Cliff ($\delta$)

Tamanho de efeito não paramétrico: com que frequência um valor do grupo A é maior que um
valor do grupo B.

$$\delta = P(X_A > X_B) - P(X_A < X_B)$$

Varia de $-1$ a $+1$; $0$ quer dizer distribuições sobrepostas. Limiares usuais
(Romano et al., 2006): $|\delta| < 0{,}147$ desprezível, $< 0{,}33$ pequeno,
$< 0{,}474$ médio, acima disso **grande**.

**Por que usamos.** Com milhares de contas, quase todo atributo fica "estatisticamente
significativo" ([Mann-Whitney](mann-whitney.md)); o que interessa é **o tamanho** da
diferença. É assim que medimos, por exemplo, que o [tempo de
permanência](tempo-de-permanencia.md) separa laranjas de contas comuns com $\delta = -1{,}00$.

**No projeto.** [`stats.compare_groups`](../../src/pixfraud/stats.py);
figura `cenarios_efeitos.png` e a seção de perfis em [resultados](../resultados.md).
