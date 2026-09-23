---
tags: [glossario]
---

# ROC-AUC

Probabilidade de uma conta fraudulenta sorteada ao acaso receber escore maior que uma
conta legítima sorteada ao acaso.

$$\text{ROC-AUC} = P\bigl(\text{escore}(\text{fraude}) > \text{escore}(\text{normal})\bigr)$$

**Por que não usamos como métrica principal.** Com fraudes raras, ela fica otimista: há
contas normais demais "empurrando" a média para cima. Nos nossos experimentos, quase toda
combinação passa de 0,96, inclusive as ruins — ela não separa as abordagens. A
[average precision](average-precision.md) separa.

Veja também: [classes raras](classes-raras.md).
