---
tags: [ideia]
---

# Detecção conformal com controle de alarmes falsos

Volta para as [ideias futuras](ideias-futuras.md).

## A ideia

Hoje cada modelo devolve uma fila de risco, e a decisão de quantas contas investigar (o
top-k) é arbitrária. A [detecção conformal](../glossario/deteccao-conformal.md) transforma
o escore de **qualquer** modelo num p-valor por conta ("quão estranha é esta conta perto das
normais?"), e a correção de Benjamini-Hochberg escolhe quantas marcar com uma garantia
operacional: **no máximo q% das contas marcadas são alarmes falsos**.

É a resposta à pergunta "existe teste de hipótese para dizer se a conta é fraude?" (conversa
de 08/10, ver o [diário](../diario/2026-10-08.md)): o
[Kruskal-Wallis](../glossario/kruskal-wallis.md) compara grupos e não classifica; o p-valor
conformal testa conta por conta.

## Como se encaixaria

- Uma camada sobre `pixfraud.models` (por exemplo, `pixfraud/models/conformal.py`), sem
  mudar os modelos: recebe os escores e um conjunto de calibração e devolve p-valores e a
  marcação com FDR controlada.
- **Calibração:** contas sabidamente legítimas (na rede sintética, uma parte das legítimas
  sorteada; no Pix real, contas antigas sem contestação), separadas das contas avaliadas.
- **Avaliação:** a FDR observada fica abaixo de q? Quantas fraudes são achadas com q = 5%,
  10% e 20%? Comparar entre PCA, kNN, autoencoder e "PageRank relativo + DBSCAN", nos
  cenários realistas.
- No [explorador](../../app/guia-do-explorador.md), q substituiria o top-k como controle:
  "investigue estas contas; no máximo 10% são alarmes falsos".

## O que falta

- Decidir de onde vem a calibração sem usar o gabarito das contas avaliadas.
- Conferir a garantia quando a calibração tem fraudes escondidas (contaminação), que é o
  caso real.
- Referências: Vovk, Gammerman e Shafer (2005), *Algorithmic Learning in a Random World*;
  Bates et al. (2023), "Testing for outliers with conformal p-values"; Benjamini e Hochberg
  (1995). Ainda sem fichamento em [`leituras/`](../leituras/mapa-das-leituras.md).
