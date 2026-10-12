---
tags: [glossario]
---

# Teste de Friedman e diferença crítica de Nemenyi

O teste de Friedman compara **três ou mais abordagens medidas nas mesmas unidades**. No
projeto, as abordagens são os modelos e as unidades são as sementes: cada modelo roda nas
mesmas redes. Dentro de cada semente, os modelos são ordenados (posto 1 = maior AP). O teste
pergunta se os **postos médios** diferem mais do que o acaso explicaria.

É o equivalente pareado do [Kruskal-Wallis](kruskal-wallis.md), assim como o
[Wilcoxon pareado](teste-de-wilcoxon-pareado.md) é o equivalente pareado do
[Mann-Whitney](mann-whitney.md). Usar Kruskal-Wallis entre modelos jogaria fora o
pareamento: uma semente difícil derruba todos os modelos juntos, e o Friedman desconta isso.

**Tamanho do efeito.** O W de Kendall, de 0 a 1, mede o quanto as sementes concordam na
ordem dos modelos: W = χ² / (N(k − 1)).

**Nemenyi.** Se o Friedman dá significativo, a diferença crítica diz que pares diferem:

$$CD = q_\alpha \sqrt{\frac{k(k+1)}{6N}}$$

com k modelos e N sementes ($q_\alpha$ vem da distribuição da amplitude studentizada). Dois
modelos cujos postos médios diferem menos que CD **não se distinguem** com essas sementes. No
diagrama de diferença crítica, cada modelo é um ponto com uma barra de ± CD/2: barras que não
se tocam são modelos que diferem. É o procedimento de Demšar (2006) para comparar vários
classificadores em vários conjuntos de dados.

**No projeto.** [`stats.friedman_models`](../../src/pixfraud/stats.py) e
[`visualization.plot_critical_difference`](../../src/pixfraud/visualization.py), usados por
[`avaliar_modelos.py`](../../scripts/03_modelos/avaliar_modelos.py)
(`modelos_friedman.csv`, `modelos_postos.csv`, `modelos_diferenca_critica.png`). Ver o
[plano de testes estatísticos](../plano-de-testes-estatisticos.md).
