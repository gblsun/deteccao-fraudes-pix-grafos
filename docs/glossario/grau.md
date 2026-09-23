---
tags: [glossario]
---

# Grau (in_degree, out_degree)

Número de contas distintas ligadas a uma conta. No grafo direcionado, contam-se
separadamente:

$$\text{in\_degree}(v) = |\{u : u \to v\}|, \qquad \text{out\_degree}(v) = |\{u : v \to u\}|$$

**Como ler.** Grau de entrada alto = recebe de muita gente (comércio popular, ou uma conta
laranja recebendo de várias vítimas). Grau de saída baixo e grau de entrada alto ao mesmo
tempo é a assinatura de uma **coletora**.

**No projeto.** [`features.graph_features`](../../src/pixfraud/features.py); no cenário
`sem_atalhos`, o grau de entrada tem $\delta = -0{,}65$ nas laranjas (menor que o normal,
porque recebem de poucas vítimas de cada vez) e o de saída, $-0{,}86$ nos intermediários.
