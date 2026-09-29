---
tags: [resultado]
---

# Resultados

Resultados **preliminares**, obtidos só com o dataset sintético (`pixfraud.simulation`).
Todos os números abaixo saem dos arquivos de `reports/results/` e podem ser refeitos com:

```powershell
python scripts/reproduzir_tudo.py   # refaz tudo na ordem certa (ver scripts/mapa-dos-scripts.md)
```

Cada semente gera um dataset diferente (~2.140 contas e ~42 mil Pix no cenário base) e muda a semente do
Isolation Forest. Os parâmetros ficam em [`configs/experimento.yaml`](../configs/experimento.yaml)
e [`configs/cenarios.yaml`](../configs/cenarios.yaml).

## Como ler as métricas

* **[Average precision](glossario/average-precision.md) (AP)** é a métrica principal. Um
  detector que ordena as contas ao acaso tem AP igual à taxa de fraude (~0,019 no cenário
  base e 0,006 no `realista`), então 0,5 já é muito melhor que o acaso.
* **[ROC-AUC](glossario/roc-auc.md)** fica acima de 0,96 em quase todas as combinações e
  quase não diferencia nada. Com fraudes raras, ela é otimista: há contas normais demais
  para "empurrar" para baixo do ranking.
* **[Precision@k](glossario/precision-at-k.md)**: das *k* contas mais suspeitas (*k* = nº
  de fraudes reais), que fração é fraude.
* **Testes pareados**: a mesma semente é avaliada pelas duas abordagens. Com 10 sementes e
  10 comparações por métrica, o menor p de [Wilcoxon](glossario/teste-de-wilcoxon-pareado.md)
  ajustado por [Holm](glossario/correcao-de-holm.md) é ≈ 0,02. Esse valor quer dizer que
  **todas** as sementes apontaram para o mesmo lado.

## 1. Cenário base: o tabular parece bastar

Average precision média em 10 sementes, com IC 95% ([`robustez_resumo.csv`](../reports/results/robustez_resumo.csv)):

| Atributos        | Isolation Forest     | DBSCAN               |
|------------------|----------------------|----------------------|
| tabular          | 0,39 [0,34; 0,44]    | 0,76 [0,72; 0,79]    |
| grafo            | 0,35 [0,31; 0,39]    | 0,44 [0,40; 0,48]    |
| combinado        | 0,38 [0,35; 0,42]    | 0,71 [0,68; 0,73]    |
| temporal         | 0,55 [0,51; 0,59]    | 0,48 [0,46; 0,51]    |
| grafo_avancado   | 0,61 [0,58; 0,65]    | 0,58 [0,54; 0,62]    |
| completo         | 0,58 [0,52; 0,63]    | **0,78** [0,76; 0,79] |

Olhando só para este cenário, a conclusão seria que **os grafos não ajudam**:

* com o DBSCAN, os atributos de grafo ficam 0,32 abaixo dos tabulares (tabular vence nas
  10 sementes), e somar grafo ao tabular (`combinado`) até **piora** o resultado (−0,05);
* o conjunto `completo` não é significativamente melhor que o tabular (+0,02,
  IC [−0,01; 0,05], p = 0,46).

Duas exceções já aparecem: os atributos estruturais avançados
([k-núcleo](glossario/k-nucleo.md), [OddBall](glossario/egonet-e-oddball.md),
[participação](glossario/coeficiente-de-participacao.md)) melhoram muito os de grafo
clássicos (+0,27 no [Isolation Forest](glossario/isolation-forest.md) e +0,14 no
[DBSCAN](glossario/dbscan-e-k-distance.md), 10 de 10 sementes), e com o Isolation Forest o
`completo` supera o tabular (+0,19).

**Sobre o terceiro detector.** Um [LOF](glossario/lof.md) também foi avaliado nos mesmos
estudos (todas as seções abaixo continuam comparando só Isolation Forest e DBSCAN, que
sustentam as conclusões). Ele nunca superou os outros dois em nenhum cenário — seu melhor
resultado é AP 0,51 com `tabular` no cenário base, e cai para 0,06–0,08 nos conjuntos de
grafo. Os números completos e a hipótese para o desempenho fraco estão em
[modelos.md](modelos.md#4-local-outlier-factor--lof-não-supervisionado).

## 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador

O gerador embute sinais "fáceis" por construção (ver "Limitações conhecidas" em
[`data/README.md`](../data/README.md)). Cada cenário desliga parte deles:

| Cenário         | O que muda                                                      | Fraude |
|-----------------|-----------------------------------------------------------------|:------:|
| `base`          | nada: golpes a qualquer hora, 70% das contas fraudulentas novas | 1,8%   |
| `sem_horario`   | (a partir do base) golpes e repasses no perfil horário dos Pix legítimos | 1,9% |
| `sem_idade`     | (a partir do base) contas fraudulentas com a idade das legítimas | 1,8%  |
| `sem_atalhos`   | os dois atalhos desligados                                      | 1,9%   |
| `sem_valor`     | (a partir do sem_atalhos) golpes do tamanho de um Pix comum, e não ~4,5x | 1,9% |
| `com_inativos`  | (a partir do sem_atalhos) + 30% das pessoas quase não usam Pix  | 1,9%   |
| `realista`      | + fraudes 3x mais raras                                         | 0,6%   |
| `repasse_lento` | + laranjas esperam ~6 h de atividade (e não ~30 min) antes de repassar | 0,6% |

Com os golpes no horário comercial, os repasses também seguem o perfil horário: o atraso
de cada repasse é contado num "relógio de atividade", que anda devagar de madrugada.

![Average precision por cenário](../reports/figures/cenarios_average_precision.png)

**2.1. O desempenho do tabular desaba quando os atalhos somem.** Com o DBSCAN, a AP do
tabular cai de 0,76 (`base`) para 0,45 sem o horário, 0,59 sem a idade, 0,25 sem os dois,
0,13 com pessoas inativas e 0,09 no `realista`. Os atributos de grafo quase não mudam
nos quatro primeiros cenários (0,43 a 0,44). Em `sem_idade` eles são **idênticos** aos
do `base`, porque só a idade das contas muda e os Pix são os mesmos.

**2.2. A comparação tabular × grafo se inverte.** Diferença de AP `grafo − tabular`
([`cenarios_comparacoes.csv`](../reports/results/cenarios_comparacoes.csv)):

| Cenário         | Isolation Forest        | DBSCAN                  |
|-----------------|-------------------------|-------------------------|
| `base`          | −0,04 (n.s.)            | −0,32 (tabular 10/10)   |
| `sem_horario`   | +0,18 (grafo 10/10)     | −0,02 (n.s.)            |
| `sem_idade`     | +0,12 (grafo 10/10)     | −0,15 (tabular 10/10)   |
| `sem_atalhos`   | +0,28 (grafo 10/10)     | +0,19 (grafo 10/10)     |
| `sem_valor`     | +0,24 (grafo 10/10)     | +0,26 (grafo 10/10)     |
| `com_inativos`  | +0,22 (grafo 10/10)     | +0,21 (grafo 10/10)     |
| `realista`      | +0,13 (grafo 10/10)     | +0,10 (grafo 10/10)     |
| `repasse_lento` | +0,13 (grafo 10/10)     | +0,11 (grafo 10/10)     |

Com o DBSCAN, a idade da conta sozinha já basta para o tabular vencer, e sem o horário os
dois empatam. Com os dois atalhos desligados, o grafo vence em todas as sementes, com os
dois detectores, em **todos** os cenários seguintes.

**2.3. O valor inflado dos golpes não explica a vantagem do grafo.** No `sem_valor`, os
atributos de valor perdem o sinal: o efeito de `amount_received` vai de 0,76 para −0,07,
o do [PageRank](glossario/pagerank.md) (ponderado pelo valor) de 0,73 para 0,15 e o do `oddball_ew` de 0,94 para
0,39. O tabular cai de 0,25 para 0,15 (DBSCAN), mas o grafo quase não muda (0,43 → 0,41)
e o `completo` com DBSCAN fica igual (0,63 → 0,64).

**2.4. Juntar tudo é o mais robusto.** O `completo` com DBSCAN tem a maior AP em seis dos
oito cenários. As exceções são `com_inativos` (5º lugar) e `realista` (2º lugar), em que o
`temporal` com Isolation Forest vence. Ele supera o tabular em todos os cenários, exceto
no `base` (onde empata). No `realista`, tem AP 0,50 [0,45; 0,55], cerca de 80 vezes o
acaso, e precision@k 0,55.

**2.5. Os atributos temporais são fortes, mas dependem do repasse rápido.** O conjunto
`temporal` ([tempo de permanência](glossario/tempo-de-permanencia.md) do dinheiro e pico
diário de pagadores) é o mais estável
nos sete primeiros cenários (Isolation Forest: AP de 0,55 a 0,61) e o melhor sozinho no
`realista` (0,59). Quando as laranjas esperam ~6 h, cai para 0,41. Mesmo assim, o tempo de
permanência continua separando bem (δ = −0,77): 6 h ainda é rápido perto das pessoas
comuns, que passam dias sem repassar.

**2.6. Contas inativas também afetam os atributos de grafo.** Pessoas que quase não usam
Pix têm grau e k-núcleo baixos, como as contas de fraude. Com elas, o efeito do
`out_degree` cai de −0,86 para −0,45, o do `core_number` de −0,93 para −0,73, e a
intermediação (`betweenness`) deixa de separar os grupos (de −0,31 para ~0). O
`grafo_avancado` com Isolation Forest cai de 0,63 para 0,47.

### Quais atributos separam fraude de normal em cada cenário

[Delta de Cliff](glossario/delta-de-cliff.md) médio (fraude × normal) de cada atributo
([`cenarios_efeitos.csv`](../reports/results/cenarios_efeitos.csv)):

![Delta de Cliff por cenário](../reports/figures/cenarios_efeitos.png)

* `night_ratio` (0,63 → −0,09) e `account_age_days` (−0,72 → 0,02) perdem o efeito
  exatamente nos cenários que desligam o atalho correspondente. Isso confirma que esses
  sinais eram construídos. No `repasse_lento`, o `night_ratio` fica em 0,03: o cenário
  mede só o efeito da demora.
* Separam bem (|δ| ≥ 0,47) em **todos** os cenários: `clustering` (≈ −0,9),
  `avg_neighbor_degree`, `core_number`, `oddball_en` e `dwell_time_min`. O
  `max_amount_received` também, mas o sinal se inverte no `sem_valor` (as contas
  fraudulentas recebem poucos Pix, então o maior deles fica menor que o das pessoas comuns).

## 3. O gerador comparado com o Pix real

O [notebook 01](../notebooks/01_analise_exploratoria.ipynb) confronta o gerador com as
estatísticas abertas do Pix [`data/bcb/`](../data/README.md):

| | BCB (06/2025 a 04/2026) | Gerador |
|---|---|---|
| Pix de pessoa física para empresa | 49% | 40% |
| Ticket médio P2P / P2B | R$ 257 / R$ 114 | R$ 101 / R$ 99 |
| Golpes (contestações aceitas) a cada 100 mil Pix | ~5 | ~530 |
| Valor médio de um golpe | R$ 2.277 (~9x o P2P) | R$ 305 (~3x) |

Duas leituras importam para o resto do relatório:

* a taxa de fraude do gerador é ~110 vezes a real (de propósito, para haver exemplos); o
  cenário `realista` reduz isso só 3 vezes, então **todas as métricas aqui são otimistas**;
* o gerador **não exagera** o valor dos golpes: se algo, subestima. O cenário `sem_valor`
  já tinha mostrado que a vantagem do grafo não depende desse valor.

**Para onde vai o dinheiro dos golpes.** Das contestações aceitas, só **11% do valor volta**
à vítima pelo [MED](glossario/med.md). Metade (51%) não volta por **saldo insuficiente**, ou seja, o dinheiro
já tinha saído da conta, e outros 28% são o que faltou nas devoluções parciais. É esse
problema que a seção 5 mede.

## 4. Perfis: o que distingue cada papel, e quem os detectores encontram

No cenário `sem_atalhos` ([notebook 02](../notebooks/02_perfis_de_fraude.ipynb)):

| Papel | Assinatura (delta de Cliff contra as contas legítimas) |
|-------|--------------------------------------------------------|
| laranja | repassa quase na hora (tempo de permanência −1,00), `pass_through` +0,83, vizinhança em estrela (OddBall +0,84, agrupamento −0,82, k-núcleo −0,87) |
| intermediário | extremo em quase tudo: valores +0,98, `pass_through` +0,96, um único pagador (grau de entrada −0,99) |
| coletora | recebe muito (+0,97) e **não repassa** (`pass_through` −0,88) |
| vítima | não se distingue das pessoas comuns (todos os \|δ\| < 0,25) |

Fração de cada papel entre as *k* contas mais suspeitas (*k* = nº de fraudes):

| Conjunto e modelo | laranja | intermediário | coletora | vítima |
|---|:---:|:---:|:---:|:---:|
| tabular, Isolation Forest | 0% | 33% | 33% | 0% |
| grafo, DBSCAN | 25% | 100% | 100% | 0% |
| temporal, Isolation Forest | **79%** | 100% | 0% | 0% |
| completo, DBSCAN | 50% | 100% | 100% | 0% |

* os atributos de **grafo** encontram todos os intermediários e coletoras;
* as **laranjas são as mais difíceis**, e só os atributos **temporais** encontram a
  maioria. Isso importa porque a laranja é o primeiro salto: é nela que o dinheiro ainda
  pode ser bloqueado;
* **nenhum detector sinaliza vítimas**, o que é essencial para uso real.

## 5. Detecção a tempo: o dinheiro ainda estava lá?

Rodando os detectores a cada 6 horas (só com os Pix feitos até ali) e bloqueando cada
conta no corte em que ela é sinalizada
([`avaliar_deteccao_online.py`](../scripts/avaliar_deteccao_online.py), 3 sementes por
cenário). O "oráculo" sinaliza toda conta fraudulenta no primeiro corte depois do golpe:
é o teto imposto pela frequência dos cortes.

![Detecção a tempo](../reports/figures/online_deteccao.png)

No cenário `sem_atalhos` (43 contas fraudulentas e ~R$ 70 mil roubados por semente):

| Conjunto e modelo | detectadas em 72 h | atraso mediano | dinheiro retido (saque em 1 h) |
|---|:---:|:---:|:---:|
| tabular, DBSCAN | 46% | 22 h | 45% |
| grafo, DBSCAN | 64% | 13 h | 68% |
| temporal, DBSCAN | 87% | **3,0 h** | 83% |
| completo, DBSCAN | **93%** | 3,0 h | 82% |
| oráculo | 100% | 2,5 h | 90% |

* o **atraso** é o que separa as abordagens: com atributos tabulares, a conta só é
  sinalizada quase um dia depois do golpe, quando o dinheiro já saiu; com os temporais, em
  cerca de 3 horas, perto do teto de 2,5 h imposto pelos cortes de 6 h;
* mesmo o oráculo não retém 100% com saque em 1 h: as laranjas repassam em ~30 minutos,
  antes do primeiro corte. O que o bloqueio salva, em boa parte, são os **golpes
  seguintes** que chegariam à mesma conta;
* no `realista` tudo piora, e os atributos temporais passam à frente: o melhor detecta 65%
  em 72 h (temporal, Isolation Forest) e o melhor retém 59% do dinheiro (temporal,
  DBSCAN), contra 93% e 82% do `completo` no `sem_atalhos`;
* com 3 sementes, essas diferenças são descritivas: o menor p possível no teste pareado é
  0,25.

## 6. Culpa por associação: usar as contestações que já existem

Se parte das contas fraudulentas já é conhecida (por contestações no MED), a
[propagação de risco](glossario/propagacao-de-risco.md) a partir delas
([`flow.propagate_risk`](../src/pixfraud/flow.py)) encontra as
demais? Avaliação **só nas contas ainda desconhecidas**, 10 sementes
([`avaliar_propagacao.py`](../scripts/avaliar_propagacao.py)):

| Cenário | Conhecidas | Propagação | `completo`/DBSCAN | Propagação + detector |
|---|:---:|:---:|:---:|:---:|
| `sem_atalhos` | 10% | 0,45 | 0,61 | 0,63 |
| `sem_atalhos` | 25% | 0,62 | 0,57 | **0,83** |
| `realista` | 10% | 0,55 | 0,48 | **0,70** |
| `realista` | 25% | 0,70 | 0,46 | **0,95** |

A combinação (média dos percentis dos dois escores) vence o detector sozinho em todos os
casos, e com folga quando um quarto das fraudes já é conhecido: +0,26 no `sem_atalhos`
(9 de 10 sementes) e +0,49 no `realista` (10 de 10, p de Holm 0,006). Normalizar a
propagação pelo PageRank comum (`propagacao_relativa`) não ajudou.

Isso sugere um uso prático: as contestações que o banco já recebe podem alimentar a busca
pelo resto da quadrilha, sem precisar de rótulos novos.

## 7. Contribuição de cada atributo e o teto supervisionado

Tirando um atributo de cada vez do conjunto `completo`
([`avaliar_atributos.py`](../scripts/avaliar_atributos.py), 5 sementes):

![Ablação por atributo](../reports/figures/atributos_ablacao.png)

* os que mais fazem falta: **tempo de permanência** (queda de até 0,11 de AP),
  **k-núcleo** (0,09) e **OddBall de valor** (0,09);
* o **PageRank atrapalha o DBSCAN**: tirá-lo **melhora** a AP em 0,09 (`sem_atalhos`) e
  0,15 (`realista`). Ponderado pelo valor, ele tem cauda muito pesada e distorce as
  distâncias. Vale testar um conjunto `completo` sem ele;
* o grau de entrada atrapalha o Isolation Forest (melhora de 0,06 a 0,09 ao sair).

**Teto supervisionado.** Um [Random Forest](glossario/random-forest.md) treinado com os
rótulos ([validação cruzada](glossario/validacao-cruzada.md) de 5 partes) chega a AP 1,00
no `sem_atalhos` e 0,99 no `realista` com o conjunto `completo`,
contra 0,62 e 0,53 do melhor detector não supervisionado. A distância mostra quanto se
perde por não ter rótulos, e explica por que a seção 6 melhora tanto com poucos rótulos.
Mesmo supervisionado, o grafo supera o tabular (0,78 contra 0,66 no `realista`).

## 8. Validação externa: AMLworld

Mesma configuração, sem reajuste, sobre o AMLworld (HI-Small, só pagamentos em dólar e
transferências ACH/Wire, as mais parecidas com Pix), em 4 janelas de 3 dias
([`avaliar_externo.py`](../scripts/avaliar_externo.py)). A taxa de contas envolvidas em
lavagem é de 1,6% por janela.

| Conjunto e modelo | AP média | vezes o acaso |
|---|:---:|:---:|
| grafo_avancado, DBSCAN | 0,042 | 2,7 |
| completo, DBSCAN | 0,041 | 2,5 |
| grafo, Isolation Forest | 0,039 | 2,5 |
| tabular, DBSCAN | 0,026 | 1,6 |
| temporal, DBSCAN | 0,024 | 1,5 |

* o desempenho absoluto é **baixo**: o melhor fica em 2,7 vezes o acaso, longe dos 0,5 a
  0,8 de AP do dataset sintético;
* mesmo assim, o grafo supera o tabular nas **4 janelas**, com os dois detectores
  (+0,010 e +0,012 de AP); com só 4 repetições, o teste pareado não alcança significância
  (o menor p possível é 0,125);
* por tipologia, as encontradas são as de formato: espalha e junta (`scatter_gather` 20%,
  `gather_scatter` 14%) e leque (`fan_out` 16%, `fan_in` 11%), quase sempre com atributos
  de grafo. Cadeias, grupos bipartidos e padrões aleatórios passam quase despercebidos.

A diferença para o sintético é grande e tem explicações plausíveis: o AMLworld trata de
lavagem (não de golpes contra vítimas), as contas de lavagem têm bastante movimento
comum, e o rótulo marca como suspeita toda conta que tocou uma transação de lavagem.

**Com todas as formas de pagamento** (sem restringir a ACH/Wire; mesmas 4 janelas, agora
de 1 dia, por causa do tamanho — 100 a 134 mil contas cada), a fraude fica ainda mais rara
(0,33% das contas, contra 1,6% na versão só-transferências) e a AP cai junto: a melhor
combinação (`completo`, Isolation Forest) fica em 0,011, ainda assim **3,5 vezes o acaso**.
A vantagem do grafo fica mais fraca e menos consistente aqui: com o Isolation Forest,
`grafo` supera `tabular` nas 4 janelas (+0,006 de AP); com o DBSCAN, empata (2 de 4,
diferença de −0,001). Cheque, dinheiro em espécie e cartão parecem diluir o sinal
estrutural que as transferências eletrônicas preservam — mais um motivo para preferir
ACH/Wire como a comparação principal com o Pix.

## 9. FRAUDAR: blocos densos acham quadrilhas, mas não sozinhos

O [FRAUDAR](glossario/fraudar.md) procura, um depois do outro, os subgrafos mais densos,
com pesos que ignoram pagamentos a contas muito procuradas (camuflagem). Não usa rótulos
nem atributos, só a estrutura ([`avaliar_fraudar.py`](../scripts/avaliar_fraudar.py), 10
sementes). Cada conta recebe a densidade do bloco em que está; blocos com mais de 5% das
contas não pontuam, porque no Pix o primeiro "bloco" é quase a rede legítima inteira.

| AP média | `base` | `sem_atalhos` | `com_inativos` | `realista` |
|---|:---:|:---:|:---:|:---:|
| FRAUDAR | 0,55 | 0,54 | 0,15 | 0,04 |
| completo, DBSCAN | 0,78 | 0,63 | 0,42 | 0,50 |
| **combinado** (média dos percentis) | **0,89** | **0,82** | **0,52** | 0,35 |

* **Sozinho, perde** para o melhor detector em todos os cenários; no `sem_atalhos` a
  diferença não é significativa (vence em 4 das 10 sementes, p de Holm 0,28).
* **Combinado, ganha**: soma +0,12 no `base` e +0,19 no `sem_atalhos` sobre o DBSCAN
  (vence em 9 de 10 sementes, p de Holm 0,008). Estrutura densa e atributos erram em
  contas diferentes.
* **Quebra quando a rede legítima se parte**: com 30% de pessoas quase inativas
  (`com_inativos`, `realista`), sobram muitos círculos de contatos pequenos e densos, que
  competem com as quadrilhas. O FRAUDAR ainda cobre ~60% das fraudes, mas diluídas entre
  ~170 a 195 contas marcadas (contra ~35 no `base`). No `realista`, com só 2 quadrilhas, a
  combinação chega a piorar o DBSCAN (−0,15).

## 10. Redes neurais para grafos (GNN)

Primeira avaliação de GNN, decidida na [reunião de 24/09](reunioes/2026-09-24.md)
([`avaliar_gnn.py`](../scripts/avaliar_gnn.py), 5 sementes; ver
[redes neurais para grafos](glossario/redes-neurais-para-grafos.md)). Duas perguntas
diferentes:

| AP média (5 sementes) | `sem_atalhos` | `realista` |
|---|:---:|:---:|
| *não supervisionados* | | |
| completo, DBSCAN | 0,62 | 0,53 |
| DOMINANT, atributos completos | 0,30 | 0,26 |
| DOMINANT, atributos tabulares | 0,07 | 0,04 |
| *supervisionados (tetos, validação cruzada)* | | |
| Random Forest, tabular | 0,94 | 0,66 |
| **GraphSAGE, tabular** | **0,99** | **0,92** |
| Random Forest, completo | 1,00 | 0,99 |
| GraphSAGE, completo | 1,00 | 1,00 |

* **Sem rótulos, a GNN não ajuda (ainda).** O autoencoder DOMINANT fica bem abaixo do
  DBSCAN nas 5 sementes dos dois cenários. Reconstruir a rede inteira não isola uma
  quadrilha pequena: o erro de reconstrução é dominado por contas normais atípicas.
* **Com rótulos, a GNN aprende sozinha o que os atributos de grafo capturam.** Vendo só os
  atributos tabulares, a GraphSAGE chega a 0,92 no `realista`, contra 0,66 do Random
  Forest com os mesmos atributos (vence nas 5 sementes). É quase o teto com todos os
  atributos feitos à mão (0,99), sem que nenhum deles tenha sido calculado.
* Com todos os atributos, os dois tetos saturam (~1,00): não há espaço para a GNN mostrar
  ganho.
* **Estatística:** com 5 sementes, o menor p possível no Wilcoxon exato é 0,0625, e 0,25
  depois de Holm; as vitórias de 5 em 5 são consistentes, mas não "significativas" por
  construção. Para o relatório, vale rodar com 10 sementes (~35 min).

## 11. GNN com poucos rótulos: a vantagem da GraphSAGE não sobrevive

Na seção 10, a GraphSAGE treina com os rótulos de 80% das contas. No Pix, só parte das
fraudes vira conhecida (as contestações do MED) e todo o resto aparece como "não fraude".
Aqui, como na culpa por associação (seção 6),
10% ou 25% das contas fraudulentas são sorteadas como conhecidas; os modelos treinam só com
elas e a AP é medida **só nas contas restantes**
([`avaliar_gnn_rotulos.py`](../scripts/avaliar_gnn_rotulos.py), 10 sementes;
[`gnn.sage_known_fraud_scores`](../src/pixfraud/gnn.py) e
[`experiment.known_fraud_scores`](../src/pixfraud/experiment.py)).

| AP média (10 sementes) | `sem_atalhos` 10% | `sem_atalhos` 25% | `realista` 10% | `realista` 25% |
|---|:---:|:---:|:---:|:---:|
| completo, DBSCAN (sem rótulos) | 0,61 | 0,56 | 0,48 | 0,46 |
| propagação + DBSCAN (seção 6) | 0,63 | 0,83 | **0,70** | 0,95 |
| Random Forest, tabular | 0,43 | 0,64 | 0,22 | 0,41 |
| GraphSAGE, tabular | 0,46 | 0,71 | 0,29 | 0,43 |
| Random Forest, completo | **0,89** | **0,97** | 0,65 | **0,97** |
| GraphSAGE, completo | 0,65 | 0,87 | 0,55 | 0,65 |

* **A estrutura aprendida deixa de compensar.** Com os atributos tabulares, a GraphSAGE
  ainda fica um pouco acima do Random Forest (+0,02 a +0,07, vence em 6 ou 7 de 10
  sementes, sem significância), mas longe do salto de 0,66 → 0,92 da seção 10. Com poucos
  exemplos de fraude, a rede não tem de onde aprender o padrão da vizinhança.
* **Com todos os atributos, a GNN perde para o Random Forest** nos quatro casos (−0,10 a
  −0,31; perde em todas as sementes em três deles, p ≤ 0,016 com Holm). Os atributos de
  grafo feitos à mão carregam a estrutura de um jeito que pouco rótulo já basta para usar;
  a GraphSAGE mistura os atributos dos vizinhos, e as "fraudes não descobertas" rotuladas
  como normais contaminam essa mistura.
* **O método simples de grafo é o mais robusto sem atributos supervisionados**: a
  propagação de risco + DBSCAN supera a GraphSAGE completa no `realista` (0,70 contra 0,55
  com 10%; 0,95 contra 0,65 com 25%).
* A GraphSAGE completa ainda bate o DBSCAN sem rótulos (+0,31 no `sem_atalhos` com 25%,
  10 de 10 sementes): qualquer rótulo ajuda, mas não a coloca no topo.
* **Limite do desenho:** as contas não rotuladas contam como normais (a forma mais simples
  de aprendizado *positivo e não rotulado*). Uma perda própria para esse caso, ou a
  GraphSAGE partindo do escore da propagação, são o próximo teste natural.

## 12. Quantas sementes bastam? A AP média com 10, 100, 500 e 1000

Pedido da [reunião de 24/09](reunioes/2026-09-24.md): as seções 1 e 2 usam 10 sementes por
chave (atributos, modelo). O cenário `base` foi repetido com **1000 sementes**
([`avaliar_sementes.py`](../scripts/avaliar_sementes.py), 4 processos, ~2 h;
[`sementes_convergencia.csv`](../reports/results/sementes_convergencia.csv),
[`sementes_sorteios.csv`](../reports/results/sementes_sorteios.csv) e
[`sementes_pareadas.csv`](../reports/results/sementes_pareadas.csv); Figura 15).

| AP média (IC 95%) | 10 sementes | 100 | 1000 |
|---|:---:|:---:|:---:|
| completo, DBSCAN | 0,776 ± 0,016 | 0,769 ± 0,005 | 0,770 ± 0,002 |
| tabular, DBSCAN | 0,755 ± 0,036 | 0,755 ± 0,010 | 0,753 ± 0,003 |
| completo, Isolation Forest | 0,576 ± 0,055 | 0,563 ± 0,013 | 0,561 ± 0,004 |
| grafo_avancado, Isolation Forest | 0,615 ± 0,033 | 0,593 ± 0,010 | 0,588 ± 0,004 |
| tabular, LOF | 0,513 ± 0,085 | 0,511 ± 0,026 | 0,518 ± 0,008 |

* **A média de 10 sementes já estava certa.** Nas 18 chaves, ela fica a no máximo 0,026 da
  média de 1000 (o pior caso é `grafo_avancado` com Isolation Forest, 0,615 contra 0,588), e
  sempre dentro do IC 95% das 10 sementes. Nenhuma conclusão das seções 1 e 2 muda de
  sentido.
* **O IC encolhe como $1/\sqrt n$** (Figura 15): de ±0,013–0,085 com 10 sementes para
  ±0,005–0,026 com 100 e ±0,001–0,008 com 1000. Cada fator 10 em sementes (e em tempo)
  deixa o IC só ~3 vezes mais estreito.
* **Sorteando 10 sementes quaisquer** entre as 1000 (2000 sorteios), a média do melhor
  detector (completo, DBSCAN) cai entre 0,754 e 0,783 em 95% das vezes; a do LOF tabular,
  a mais instável, entre 0,44 e 0,59. As 10 sementes apontam a mesma melhor chave que as
  1000 em 86% dos sorteios; nos outros, o empate é entre `completo` (0,770) e `tabular`
  (0,753) com DBSCAN.
* **O que decide o nº de sementes é o tamanho da diferença que se quer detectar.** Para um
  teste pareado com poder de 80%:

  | comparação (AP) | diferença média | sementes necessárias |
  |---|:---:|:---:|
  | grafo_avancado − grafo, Isolation Forest | +0,229 | 6 (o mínimo do Wilcoxon) |
  | completo − combinado, DBSCAN | +0,062 | 6 |
  | combinado − tabular, DBSCAN | −0,045 | 9 |
  | grafo_avancado − grafo, LOF | +0,015 | 26 |
  | **completo − tabular, DBSCAN** | **+0,017** | **68** |
  | grafo − tabular, Isolation Forest | −0,019 | 95 |
  | combinado − tabular, Isolation Forest | +0,006 | 584 |

  O único ponto da seção 1 que muda de status é `completo − tabular` com DBSCAN: com 10
  sementes, "não significativo (p = 0,46)"; com 1000, o `completo` vence em 61% das
  sementes e a diferença é real, mas de só **+0,017** de AP. Com sementes suficientes,
  qualquer diferença vira "significativa", e o que importa passa a ser o tamanho do efeito
  (diferença e IC), não o p-valor.
* **Mais sementes reduzem o acaso do sorteio, não o viés do gerador.** As 1000 sementes saem
  do mesmo simulador, com as mesmas hipóteses. A média fica precisa sobre o mundo
  sintético, mas não chega mais perto do Pix real; para isso servem os cenários (seção 2) e
  a validação externa (seção 8).

**Recomendação** (a levar ao orientador): 10 sementes para explorar ideias, **100 nos
números do relatório** (IC de ±0,005 a ±0,026) e, quando uma comparação específica importar,
o número dado pela coluna `sementes_necessarias`. Mil sementes serviram uma vez, como
referência.

## 13. Tipo de rede, passeios aleatórios, cosseno e a coletora que esvazia o dinheiro

Pedidos da [reunião de 24/09](reunioes/2026-09-24.md): estudar o tipo de rede, a lei de
potência, o Barabási–Albert, a componente gigante, o passeio aleatório e a similaridade de
cosseno, e depois implementar; e aumentar a movimentação do vértice do coletor. Estudo no
[notebook 06](../estudos/06_tipo_de_rede.ipynb); código em
[`pixfraud.network`](../src/pixfraud/network.py) e [`algorithms`](../src/pixfraud/algorithms.py);
números de [`analisar_tipo_de_rede.py`](../scripts/analisar_tipo_de_rede.py) (5 sementes por
cenário) e de `avaliar_cenarios.py --cenarios realista coletor_ativo --sementes 10`
(em `reports/coletor_ativo/`).

**Que tipo de rede é.** Semente 1 do `base`, a rede tratada como não direcionada, ao lado de
modelos com o mesmo nº de vértices e arestas:

| | rede Pix sintética | Erdős–Rényi | Barabási–Albert |
|---|:---:|:---:|:---:|
| grau máximo | 1573 | 48 | 278 |
| agrupamento médio | **0,25** | 0,01 | 0,04 |
| distância média | 2,2 | 2,7 | 2,6 |
| componente gigante | 100% | 100% | 100% |

* **As arestas são direcionadas, e isso muda a resposta.** O grau de **entrada** tem cauda
  de lei de potência com $\alpha = 2{,}0$ (KS ≈ 0,05, igual nos três cenários): são os
  comércios, sorteados com popularidade de Zipf. O grau de **saída** não tem cauda
  ($\alpha \approx 8$): ninguém paga milhares de contas. O $\alpha$ do grau total oscila
  entre 2 e 4 de uma semente para outra, porque mistura as duas distribuições; por isso
  ele não é reportado como "o" expoente da rede (Figura 16).
* A rede **não é um Barabási–Albert**: tem hubs de recebimento (grau máximo quase 6 vezes o
  do BA) e um agrupamento 6 vezes maior, que vem dos círculos de contatos. É uma mistura de
  cauda pesada nos recebimentos com comunidades, como em Watts–Strogatz.
* **Componente gigante:** a fraca tem todas as contas em todos os cenários. A **forte** (dá
  para ir e voltar seguindo o dinheiro) tem 95% no `base` e 85% no `realista`: quem só
  recebe fica fora: os 100 comércios e, no `realista`, ~230 pessoas (quase metade delas não
  fez nenhum Pix no mês, só recebeu; as outras não têm caminho de volta até elas a partir
  do núcleo da rede). As contas
  de fraude ficam dentro, por causa dos Pix de camuflagem.

**Passeios aleatórios que seguem o dinheiro** (20 por vítima, próximo Pix sorteado com
probabilidade proporcional ao valor):

* Os passeios **terminam** nos comércios (91 a 100%): eles nunca pagam ninguém, então são
  sorvedouros. Nenhum termina numa coletora, que também faz Pix de camuflagem.
* No caminho, **20 a 30% dos passeios passam por alguma coletora** (0,21 no `base`, 0,28 no
  `realista`, 0,30 no `coletor_ativo`), sendo que há só 2 a 6 coletoras entre ~2100
  contas. Por conta, um intermediário ou uma coletora recebe ~40 vezes mais visitas que uma
  pessoa comum (notebook 06). É a mesma intuição da culpa por associação (seção 6), agora
  partindo das vítimas e sem nenhum rótulo de fraude.

**Cosseno × Jaccard.** Para cada laranja, a fração de fraudes entre as 5 contas mais
parecidas com ela:

| | `base` | `realista` | `coletor_ativo` |
|---|:---:|:---:|:---:|
| Jaccard (só **quem** recebe) | 0,59 | 0,50 | 0,48 |
| **cosseno** (quem recebe **e quanto**) | **0,61** | **0,63** | **0,60** |

A similaridade de cosseno é o cosseno do ângulo entre os vetores de valores pagos por cada
conta. Ela acha mais "irmãs" fraudulentas, sobretudo nos cenários difíceis (+0,13 no
`realista`): as laranjas repassam quase tudo para o mesmo destino, e os Pix de camuflagem,
de valor pequeno, pesam pouco no ângulo, mas contam inteiros no Jaccard.

**A coletora que esvazia o dinheiro** (`collector_payouts = 20`, cenário `coletor_ativo`;
o parâmetro se chamava `collector_cashout` quando os resultados foram gerados, e foi
renomeado na integração de 29/09, porque o branch integrado já usava esse nome para o
saque numa corretora. O dataset gerado é o mesmo).
No gerador padrão a coletora só recebe. Com o parâmetro, ela repassa ~90% do recebido em
~20 Pix para pessoas e comércios (arestas com o rótulo `saida_coletor`).

* O grau de saída médio das coletoras vai de 3,4 para 22,2, e o `pass_through` (fração do
  recebido que sai) vai de 0,03 para 0,93: a coletora deixa de ser um sorvedouro e vira uma
  conta de passagem com muito dinheiro.
* **A detecção não piora.** A AP média sobe um pouco na maioria das combinações (+0,01 a
  +0,03) e fica igual no melhor detector (completo com DBSCAN: 0,50 nos dois). As vantagens
  do grafo sobre o tabular continuam significativas (Isolation Forest +0,13 e DBSCAN +0,10,
  p = 0,03 com Holm, nos dois cenários).
* As coletoras continuam, em média, acima do percentil 98,9 do escore nos dois cenários. Muda o
  detector que as põe no top-k: o DBSCAN perde um pouco (100% → 85% das coletoras) e o
  Isolation Forest ganha (10% → 25%). A amostra é pequena (20 coletoras em 10 sementes), e
  essa medida foi uma conferência avulsa, ainda fora de um script.
* Ressalva: ligar o parâmetro muda o sorteio das quadrilhas seguintes, então as sementes dos
  dois cenários não geram as mesmas contas. A comparação é entre médias, não pareada.

## 14. Cuidados na interpretação

* **A taxa de fraude é muito maior que a real** (seção 3), o que torna a tarefa mais fácil
  aqui do que num banco.
* **Os sinais que sobrevivem ainda são hipóteses do gerador**: as laranjas repassam em
  ~30 min, as vítimas de um mesmo golpe não se conhecem, a coletora não movimenta o
  dinheiro depois. O cenário `repasse_lento` testa a primeira e o `coletor_ativo` a
  terceira (seção 13); a segunda, não.
* **O MED é modelado de forma simples**: a recuperação depende do prazo de saque, que é um
  parâmetro nosso (1, 6 ou 24 h), e o bloqueio é instantâneo e perfeito.
* **O AMLworld também é sintético** e trata de lavagem; serve para testar o método, não
  para estimar desempenho no Pix.
* Nada aqui foi avaliado em dados reais de transações, que não são públicos.

## 15. Conclusão parcial

1. No dataset sintético, **a vantagem aparente dos atributos tabulares vinha de sinais que
   o próprio gerador embute**. Sem esses atalhos, o grafo vence em todas as sementes e nos
   dois detectores, e a combinação de todos os grupos é a mais robusta.
2. **Grafo e tempo se complementam**: a estrutura denuncia intermediários e coletoras; o
   tempo de permanência denuncia as laranjas, que são as contas em que o dinheiro ainda
   pode ser bloqueado.
3. **Detectar não basta: é preciso detectar rápido.** Com atributos temporais, a conta é
   sinalizada ~3 h depois do golpe, contra quase um dia com os tabulares; isso muda o
   quanto do dinheiro ficaria retido.
4. **Poucos rótulos rendem muito**: com 25% das fraudes conhecidas, combinar a propagação
   de risco com o detector leva a AP de 0,46 para 0,95 no cenário mais difícil.
5. Fora do gerador, no AMLworld, a tarefa é bem mais difícil, mas a ordem entre as
   abordagens se mantém.
6. **Estrutura densa e atributos se complementam**: o FRAUDAR sozinho perde, mas combinado
   com o detector soma até +0,19 de AP, enquanto a rede legítima não se partir em círculos
   pequenos e densos (seção 9).
7. **Uma GNN supervisionada aprende a estrutura sozinha**: com só os atributos tabulares,
   chega a 0,92 de AP no `realista`, contra 0,66 do Random Forest (seção 10). Sem rótulos,
   o autoencoder de grafo ainda não compete com os detectores.
8. **Mas a vantagem da GNN depende de muitos rótulos**: com só 10% ou 25% das fraudes
   conhecidas, a GraphSAGE fica abaixo do Random Forest com todos os atributos e da
   propagação de risco (seção 11). No cenário realista do Pix, o método simples de grafo
   ainda é o melhor.
9. **10 sementes bastavam para as conclusões**: com 1000, nenhuma muda de sentido, e o IC
   só encolhe como $1/\sqrt n$. Diferenças pequenas (~0,02 de AP) pedem ~70 a 100 sementes
   (seção 12).
10. **A rede Pix sintética não é livre de escala**: só os recebimentos têm cauda de lei de
    potência. A similaridade de cosseno acha mais contas fraudulentas parecidas que o
    Jaccard, e uma coletora que esvazia o dinheiro continua no topo do ranking (seção 13).

## 16. Próximos passos

1. Testar o conjunto `completo` **sem o PageRank** (seção 7) e recalibrar o gerador com os
   números do BCB (`p_merchant` ≈ 0,49, valores de P2P e P2B separados).
2. Novas tipologias no gerador, guiadas pelo AMLworld: espalha e junta, ciclo e bipartido.
3. Detecção em janelas mais curtas (cortes de 1 h), já que o atraso é o que decide a
   recuperação; e atributos temporais novos (rajadas de pagadores em minutos).
4. Aprofundar a culpa por associação: propagação com decaimento no tempo, e um cenário em
   que as contestações chegam com atraso, como no MED real.
5. GNN: rodar com 10 sementes; com poucos rótulos (seção 11), testar uma perda para
   aprendizado positivo e não rotulado e a GraphSAGE partindo do escore da propagação; e tentar um detector não supervisionado de grafo mais
   adequado a quadrilhas pequenas que o DOMINANT (por exemplo, contraste entre a conta e a
   vizinhança).
6. FRAUDAR: um critério de parada melhor que "5% das contas" e pesos que levem em conta o
   tempo (quadrilhas agem em poucas horas; círculos de contatos, ao longo do mês).
7. Sementes: usar 100 nos números do relatório (seção 12) e refazer as seções 1 e 2 com
   elas; o número exato de cada comparação sai de `sementes_pareadas.csv`.
8. Cosseno como atributo ou como propagação: similaridade de cada conta com as fraudes já
   conhecidas (seção 6), e passeios aleatórios a partir das vítimas como escore sem rótulo
   (seção 13).
9. Coletora ativa: levar a conferência por papel (percentil das coletoras) para um script, e
   decidir se `collector_payouts` passa a valer no gerador padrão.
