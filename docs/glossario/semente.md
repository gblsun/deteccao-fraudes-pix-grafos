---
tags: [glossario]
---

# Semente (aleatória)

O número que dá a partida no sorteio do computador. Ele não sorteia de verdade: uma fórmula
gera, a partir da semente, uma sequência que *parece* aleatória. **Mesma semente, mesma
sequência**; semente diferente, sequência diferente.

**Onde aparece.**
- **Na rede sintética:** quem paga quem, valores, horários, quem vira vítima e quem vira
  laranja. `gerar_dataset.py --seed 42` gera sempre as mesmas 2.142 contas e os mesmos
  41.993 Pix; outra semente gera outra rede com os mesmos parâmetros.
- **Nos modelos que sorteiam:** os cortes do [Isolation Forest](isolation-forest.md), os
  centros iniciais do k-means, as árvores do [Random Forest](random-forest.md).

**Por que importa.**
- **Reprodutibilidade:** qualquer pessoa refaz exatamente os mesmos números. Por isso a
  semente fica gravada junto de cada resultado (`*_meta.json`).
- **Não confiar numa rede só:** a ordem entre modelos parecidos pode mudar de uma semente
  para outra. Uma conclusão vale quando se mantém em várias sementes, com média e
  [IC 95%](intervalo-de-confianca.md) ([resultados, seção 12](../resultados.md)).

**Sementes reservadas.**
- **42:** a dos resultados do relatório.
- **1, 2, 3...:** os estudos com várias sementes (avaliação).
- **1001 em diante:** a [otimização de hiperparâmetros](otimizacao-de-hiperparametros.md),
  que nunca usa as de avaliação.

Mais sementes reduzem o efeito do sorteio, mas não o viés do gerador: todas saem do mesmo
simulador.
