---
tags: [ata]
---

# Para o orientador: respostas à reunião de 01/10

Material para a próxima reunião. Responde aos pedidos da
[reunião de 2026-10-01](2026-10-01.md) e retoma o que estava pendente desde a de
[2026-09-24](2026-09-24.md).

Volta para as [atas de reunião](atas-de-reuniao.md).

## 1. Os falsos positivos com percentil de risco 100%

- **O modelo não disse "coletora".** O selo do explorador era o papel real da conta, que
  vem do gerador. O risco é só um escore de anomalia (DBSCAN). A
  [correção na ata](2026-10-01.md) traz os números exatos.
- **C001118 e C000560 são comércio de verdade.** São os dois comércios mais populares da
  rede (1.573 e 1.095 pagadores) e nunca pagam ninguém. Por isso ficam no extremo do grau
  de entrada, do volume recebido e do PageRank.
- O painel do explorador agora mostra o percentil com uma casa decimal, a posição no
  ranking e o aviso de que o selo é o papel real.

<!-- RESULTADOS_FALSOS_POSITIVOS -->

## 2. O papel de cada conta confere?

`simulation.audit_roles` confere 12 regras de comportamento para cada conta. Exemplos: o
comércio é PJ e só paga salário ou fornecedor; a laranja recebe golpe e repassa; só a
coletora tira o dinheiro; a vítima pagou um golpe e não é fraudadora. Rodou em 14 cenários
× 20 sementes e no dataset da reunião.

- **Dataset da reunião (semente 42): todos os 2.142 papéis conferem.**
- Na estrutura fixa, ~1,7% das laranjas nunca recebem golpe, porque cada vítima sorteia a
  laranja. Ela fica com o rótulo de fraude, mas só faz Pix de camuflagem. Há também 2 casos
  de vítima recrutada como laranja por outra quadrilha. As duas falhas ficaram registradas
  em [`data/README.md`](../../data/README.md) e foram mantidas na estrutura fixa, para os
  resultados antigos não mudarem.
- Na estrutura aleatória (abaixo), as duas foram corrigidas: **0 violações**.

## 3. Gerador com estrutura aleatória

Cenário `aleatorio`: a cada semente, sorteiam-se o nº de quadrilhas e, em cada uma, o nº de
laranjas, vítimas e intermediários, a fração de laranjas recrutadas e o que a coletora faz
(acumula, saca ou espalha). Também são sorteados o nº de comércios e quanto eles pagam de
salários e fornecedores. As contagens seguem distribuições de cauda longa (binomial
negativa): muitas quadrilhas pequenas e poucas grandes. Detalhes em
[`data/README.md`](../../data/README.md).

## 4. KNN, K-Means e PCA

Três detectores novos (glossário: [KNN](../glossario/knn.md),
[K-Means](../glossario/k-means.md), [PCA](../glossario/pca.md)) e um KNN supervisionado.

**Como comparar com os atuais**, que era a dúvida da reunião: todos dão um escore por
conta, então entram nas mesmas métricas de ranking ([average
precision](../glossario/average-precision.md), precision@k, ROC-AUC). Também são
avaliados nas mesmas contas de `avaliar_modelos.py`. O KNN supervisionado fica no grupo
dos "tetos", ao lado do Random Forest: ele viu rótulos que um banco raramente tem.

<!-- RESULTADOS_MODELOS -->

## 5. Redes neurais para grafos

- Já avaliadas ([resultados, seções 10 e 11](../resultados.md)): o DOMINANT, sem rótulos,
  fica abaixo do DBSCAN. A GraphSAGE chega perto do teto quando conhece **todos** os
  rótulos, mas perde para a propagação de risco quando conhece só 10% a 25% das fraudes,
  que é o caso real do MED.
- O DOMINANT e a GraphSAGE entraram em `avaliar_modelos.py`, para ficarem na mesma
  comparação dos outros modelos. **Nesta rodada eles ficaram de fora:** o Controle
  Inteligente de Aplicativos do Windows passou a bloquear uma DLL do PyTorch neste
  computador, e o código agora trata isso como "GNN indisponível". Rodam de novo onde o
  PyTorch carregar (por exemplo, no CI ou noutra máquina).

## 6. Tipo de rede (pendente desde 24/09)

Estudo no [notebook 06 · Tipo de rede](../../estudos/06_tipo_de_rede.ipynb). Números na
[seção 13 dos resultados](../resultados.md).

| Pergunta | Resposta |
|----------|----------|
| É livre de escala (lei de potência)? | **Só nos recebimentos**: grau de entrada com $\alpha \approx 2{,}0$ (os comércios). O grau de saída não tem cauda. |
| É um Barabási–Albert? | **Não.** Tem hubs de recebimento com grau ~6× o do BA e agrupamento 6× maior (0,25 contra 0,04), por causa dos círculos de contatos. |
| Componente gigante | A fraca tem 100% das contas. A forte (ir e voltar seguindo o dinheiro) tem 95% no `base` e 85% no `realista`: quem só recebe, como os comércios, fica fora. |
| Passeio aleatório | Partindo das vítimas e seguindo o dinheiro, **20 a 30% dos passeios passam por uma coletora**, que são só 2 a 6 de ~2.100 contas. |
| Cosseno (ângulo entre vetores) | Acha mais laranjas "irmãs" que o Jaccard: 0,63 contra 0,50 no `realista`. Conta quanto se paga, e não só para quem. |

Ligação com os falsos positivos: os comércios são os hubs da lei de potência e os
sorvedouros onde os passeios terminam. Os detectores que olham grau e PageRank os veem
como extremos pelo mesmo motivo.
