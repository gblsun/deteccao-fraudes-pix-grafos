---
tags: [glossario]
---

# Componente gigante

Um **componente** é um grupo de contas em que dá para ir de qualquer uma a qualquer outra
seguindo os Pix, mesmo sem um Pix direto entre elas. O **componente gigante** é o que
reúne a grande maioria das contas, com o resto espalhado em pedacinhos.

```
A — B — C        D — E        F      ->  três componentes: {A, B, C}, {D, E} e {F}
```

**Ele aparece de repente.** No modelo de Erdős–Rényi (ligações sorteadas), enquanto cada
conta tem em média menos de uma ligação a rede é só pedaços soltos; quando a média passa de
um, surge um componente que engole boa parte da rede, uma *transição de fase*.

**Dois tipos, porque o Pix tem sentido** ([grafo direcionado](grafo-direcionado-ponderado.md)):
- **fraco:** ignora o sentido; no Pix sintético contém quase todas as contas;
- **forte:** exige ir *e voltar* seguindo o dinheiro; bem menor.

**Por que importa para fraude.** O dinheiro do golpe só passa (vítima → laranja →
intermediário → coletora) e quase nunca volta, então as contas da quadrilha costumam estar
no componente fraco e **fora** do forte, um sinal de [pass-through](pass-through.md). E,
como as vítimas são pessoas comuns, a quadrilha fica ligada ao componente gigante e se
esconde dentro da rede principal; se ficasse isolada, seria fácil de achar.

**No projeto.** [`network.component_summary`](../../src/pixfraud/network.py), usado em
`scripts/analisar_tipo_de_rede.py` e na aba Resumo do
[explorador](../../app/guia-do-explorador.md).
