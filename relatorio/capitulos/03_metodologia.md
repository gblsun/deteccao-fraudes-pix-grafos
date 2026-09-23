---
tags: [relatorio]
---

# Metodologia

Volta para o [roteiro do relatório](../mapa-do-relatorio.md).

> **Rascunho** gerado a partir do código do repositório (`src/pixfraud/`, `configs/`,
> `scripts/`). Os fatos e números estão conferidos; o texto deve ser reescrito com as
> suas palavras e no nível de detalhe pedido pela instituição. A explicação completa de
> cada modelo está em [`docs/modelos.md`](../../docs/modelos.md).

## Dados

**Dataset sintético.** Como não há transações Pix individuais públicas, foi construído um
gerador de transações (`pixfraud.simulation`) com 2.000 pessoas, organizadas em círculos
de 20 contatos, e 100 comércios, ao longo de 30 dias. Cada pessoa faz em média 0,6 Pix
por dia; 40% vão para comércios, cuja popularidade segue uma lei de Zipf, e 80% dos Pix
entre pessoas ficam no círculo de contatos. Os valores seguem uma distribuição lognormal
(mediana ≈ R$ 55) e os horários, um perfil diário com picos no almoço e no começo da noite.

Sobre essa rede são injetadas seis quadrilhas. Cada uma tem quatro contas laranja e uma
coletora e, com probabilidade 0,5, uma cadeia de três intermediários. Cada quadrilha aplica
15 golpes em uma janela de cerca de dois dias, em dois cenários: *falso suporte* (uma
vítima faz de um a três Pix) e *clonagem de WhatsApp* (de dois a quatro contatos de uma
pessoa pagam a mesma laranja). Os golpes valem cerca de 4,5 vezes um Pix típico. Cada valor
recebido é repassado em cerca de 30 minutos, com uma pequena comissão retida a cada salto,
e as contas da quadrilha também fazem alguns Pix comuns (camuflagem). Com a mesma semente,
o dataset é idêntico.

**Cenários de dificuldade.** Na configuração padrão, o gerador embute sinais "fáceis": os
golpes acontecem em qualquer horário, 70% das contas fraudulentas são recém-abertas e toda
pessoa é ativa. Para não tirar conclusões apoiadas nesses atalhos, foram definidos oito
cenários (`configs/cenarios.yaml`), que desligam cada atalho separadamente e depois em
conjunto. Os mais difíceis também incluem pessoas quase inativas, fraudes três vezes mais
raras e repasses lentos (~6 h). Com os golpes em horário comercial, os repasses também
seguem o perfil horário: o atraso de cada repasse é contado num "relógio de atividade"
que anda devagar de madrugada.

**Validação com dados públicos.** As estatísticas abertas do Pix [@bcb2026dadosabertos]
foram usadas para comparar o gerador com o sistema real: natureza dos pagamentos, ticket
médio, taxa e valor das contestações, e destino do dinheiro contestado
(`notebooks/01_analise_exploratoria.ipynb`).

**Dataset externo.** Para testar o método em dados que não foram gerados por nós, foi
usado o AMLworld (versão HI-Small) [@altman2023realistic], um conjunto sintético de
transações bancárias com rótulos de lavagem de dinheiro e a tipologia de cada tentativa
(fan-in, fan-out, ciclo, gather-scatter...). Foram mantidos só os pagamentos em dólar e,
na versão "à moda Pix", só as transferências eletrônicas (ACH e Wire).

## Modelagem em grafo

As contas são vértices e os Pix, arestas direcionadas da conta pagadora para a recebedora.
Vários Pix entre o mesmo par de contas são agregados numa aresta, com o valor total e o
número de transferências [@diestel2017graph; @easley2010networks]. A implementação usa a
biblioteca NetworkX [@hagberg2008networkx].

## Atributos

Cada conta é descrita por atributos agrupados em conjuntos, para comparar as abordagens:

| Conjunto | Atributos |
|----------|-----------|
| tabular | idade da conta, nº e valor de Pix enviados e recebidos, maior valor recebido, fração do dinheiro que atravessa a conta (*pass-through*), fração de Pix de madrugada |
| temporal | tempo mediano até o dinheiro recebido ser repassado; maior nº de pagadores distintos num dia |
| grafo | graus de entrada e saída, PageRank ponderado pelo valor, intermediação (aproximação de Brandes com 500 fontes) [@brandes2001faster], coeficiente de agrupamento, grau médio dos vizinhos |
| grafo avançado | grafo + k-núcleo, coeficiente de participação entre comunidades (Louvain) e escores OddBall de egonet [@akoglu2015graph] |
| combinado / completo | tabular + grafo / todos os anteriores |

## Detectores

Foram usados dois detectores não supervisionados, sobre os atributos transformados por
$\log(1 + x)$ e padronizados: o **Isolation Forest** [@liu2008isolation], com 300 árvores,
e o **DBSCAN** [@ester1996dbscan], com `min_samples` = 10 e `eps` igual ao quantil de 95%
das distâncias ao 10º vizinho. No DBSCAN, o escore de cada conta é a distância ao 10º
vizinho. A implementação é a do scikit-learn [@pedregosa2011sklearn].

## Avaliação

- **Métricas**: a principal é a *average precision* (AP), porque, com fraudes raras, a
  ROC-AUC fica perto de 1 para quase qualquer detector. Um detector ao acaso tem AP igual
  à taxa de fraude. Também foi usada a precision@k, com *k* igual ao número de fraudes.
- **Repetição**: cada configuração foi avaliada com 10 sementes (10 datasets diferentes).
  As abordagens foram comparadas semente a semente, com o teste de Wilcoxon pareado e a
  correção de Holm para as várias comparações. A diferença entre contas fraudulentas e
  normais em cada atributo foi medida pelo delta de Cliff.
- **Validação externa**: no AMLworld, a mesma configuração foi aplicada sem ajustes, em
  janelas consecutivas de 3 dias usadas como repetições. O recall de cada tipologia de
  lavagem entre as contas mais suspeitas também foi medido.
- **Detecção a tempo**: os detectores foram rodados a cada 6 horas, vendo só os Pix feitos
  até ali, com um analista revisando as *k* contas mais suspeitas a cada ponto de corte.
  Mediu-se o atraso até cada conta fraudulenta ser sinalizada e, reproduzindo os Pix da
  quadrilha com bloqueio das contas sinalizadas, a fração do dinheiro roubado que ficaria
  retida. Como o resultado depende do tempo até o dinheiro ser sacado, foram usados
  prazos de 1, 6 e 24 horas.
- **Culpa por associação**: considerando 10% ou 25% das contas fraudulentas já conhecidas
  (por exemplo, por contestações no MED), a propagação de risco por PageRank personalizado
  foi comparada com os detectores e combinada com eles, avaliando só as contas restantes.
- **Contribuição de cada atributo**: ablação (tirar um atributo de cada vez) e comparação
  com um teto supervisionado (Random Forest treinado com os rótulos, validação cruzada de
  5 partes).

Todos os parâmetros estão em `configs/`, e cada resultado grava um `*_meta.json` com o
commit, a configuração e as sementes usadas (ver `scripts/mapa-dos-scripts.md`).
