# Resultados

Resultados **preliminares**, obtidos só com o dataset sintético (`pixfraud.simulation`).
Todos os números abaixo saem dos arquivos de `reports/results/` e podem ser refeitos com:

```powershell
python scripts/avaliar_robustez.py --sementes 10   # robustez_*.csv (cenário base)
python scripts/avaliar_cenarios.py --sementes 10   # cenarios_*.csv (todos os cenários)
```

Cada semente gera um dataset diferente (~2.140 contas e ~42 mil Pix no cenário base) e muda a semente do
Isolation Forest. Os parâmetros ficam em [`configs/experimento.yaml`](../configs/experimento.yaml)
e [`configs/cenarios.yaml`](../configs/cenarios.yaml).

## Como ler as métricas

* **Average precision (AP)** é a métrica principal. Um detector que ordena as contas ao
  acaso tem AP igual à taxa de fraude (~0,019 no cenário base e 0,006 no `realista`),
  então 0,5 já é muito melhor que o acaso.
* **ROC-AUC** fica acima de 0,96 em quase todas as combinações e quase não diferencia
  nada. Com fraudes raras, ela é otimista: há contas normais demais para "empurrar" para
  baixo do ranking.
* **precision@k**: das *k* contas mais suspeitas (*k* = nº de fraudes reais), que fração é
  fraude.
* **Testes pareados**: a mesma semente é avaliada pelas duas abordagens. Com 10 sementes e
  10 comparações por métrica, o menor p de Wilcoxon ajustado por Holm é ≈ 0,02. Esse
  valor quer dizer que **todas** as sementes apontaram para o mesmo lado.

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

Duas exceções já aparecem: os atributos estruturais avançados (k-núcleo, OddBall,
participação) melhoram muito os de grafo clássicos (+0,27 no Isolation Forest e +0,14 no
DBSCAN, 10 de 10 sementes), e com o Isolation Forest o `completo` supera o tabular (+0,19).

## 2. Cenários de dificuldade: a vantagem do tabular vinha dos atalhos do gerador

O gerador embute sinais "fáceis" por construção (ver "Limitações conhecidas" em
[`data/README.md`](../data/README.md)). Cada cenário desliga parte deles:

| Cenário         | O que muda em relação ao anterior                              | Fraude |
|-----------------|----------------------------------------------------------------|:------:|
| `base`          | nada: golpes a qualquer hora, 70% das contas fraudulentas novas | 1,8%   |
| `sem_horario`   | (a partir do base) golpes no mesmo perfil horário dos Pix legítimos | 1,9% |
| `sem_idade`     | (a partir do base) contas fraudulentas com a idade das legítimas | 1,8%   |
| `sem_atalhos`   | os dois atalhos desligados                                     | 1,9%   |
| `com_inativos`  | + 30% das pessoas quase não usam Pix                            | 1,9%   |
| `realista`      | + fraudes 3x mais raras                                         | 0,6%   |
| `repasse_lento` | + laranjas esperam ~6 h (e não ~30 min) antes de repassar       | 0,6%   |

![Average precision por cenário](../reports/figures/cenarios_average_precision.png)

**2.1. O desempenho do tabular desaba quando os atalhos somem.** Com o DBSCAN, a AP do
tabular cai de 0,76 (`base`) para 0,54 sem o horário, 0,59 sem a idade, 0,32 sem os dois,
0,17 com pessoas inativas e 0,10 no `realista`. Os atributos de grafo quase não mudam
nos quatro primeiros cenários (0,43 a 0,44). Em `sem_idade` eles são **idênticos** aos
do `base`, porque só a idade das contas muda e os Pix são os mesmos.

**2.2. A comparação tabular × grafo se inverte.** Diferença de AP `grafo − tabular`
([`cenarios_comparacoes.csv`](../reports/results/cenarios_comparacoes.csv)):

| Cenário        | Isolation Forest        | DBSCAN                  |
|----------------|-------------------------|-------------------------|
| `base`         | −0,04 (n.s.)            | −0,32 (tabular 10/10)   |
| `sem_horario`  | +0,14 (grafo 10/10)     | −0,11 (tabular 10/10)   |
| `sem_idade`    | +0,12 (grafo 10/10)     | −0,15 (tabular 10/10)   |
| `sem_atalhos`  | +0,26 (grafo 10/10)     | +0,11 (grafo 10/10)     |
| `com_inativos` | +0,19 (grafo 10/10)     | +0,16 (grafo 10/10)     |
| `realista`     | +0,13 (grafo 10/10)     | +0,09 (grafo 10/10)     |
| `repasse_lento`| +0,01 (n.s.)            | −0,04 (n.s.)            |

Com o DBSCAN, um atalho sozinho basta para o tabular vencer. Quando os dois são
desligados, o grafo vence em todas as sementes, com os dois detectores.

**2.3. Juntar tudo é o mais robusto.** O `completo` com DBSCAN tem a maior AP em cinco
dos sete cenários. As exceções são `com_inativos` (5º lugar) e `realista` (2º lugar),
em que o `temporal` com Isolation Forest vence. Ele supera o tabular em todos os
cenários, exceto no `base` (onde empata), e no `realista` ainda tem AP 0,49
[0,44; 0,55], cerca de 80 vezes o acaso, com precision@k 0,54.

**2.4. Os atributos temporais são fortes, mas dependem do repasse rápido.** O conjunto
`temporal` (tempo de permanência do dinheiro e pico diário de pagadores) é o mais estável
nos seis primeiros cenários e o melhor sozinho no `realista` (Isolation Forest: AP 0,58).
Quando as laranjas esperam ~6 h, ele cai para 0,37.

**2.5. Contas inativas também afetam os atributos de grafo.** Pessoas que quase não usam
Pix têm grau e k-núcleo baixos, como as contas de fraude. Com elas, o efeito do
`out_degree` cai de −0,86 para −0,45, o do `core_number` de −0,94 para −0,73, e a
intermediação (`betweenness`) deixa de separar os grupos (de −0,36 para ~0). O
`grafo_avancado` com Isolation Forest cai de 0,63 para 0,47.

### Quais atributos separam fraude de normal em cada cenário

Delta de Cliff médio (fraude × normal) de cada atributo
([`cenarios_efeitos.csv`](../reports/results/cenarios_efeitos.csv)):

![Delta de Cliff por cenário](../reports/figures/cenarios_efeitos.png)

* `night_ratio` (0,63 → 0,08) e `account_age_days` (−0,72 → 0,02) perdem o efeito
  exatamente nos cenários que desligam o atalho correspondente. Isso confirma que esses
  sinais eram construídos.
* Separam bem (|δ| ≥ 0,47) em **todos** os cenários: `clustering` (≈ −0,9),
  `avg_neighbor_degree`, `oddball_ew`, `oddball_en`, `pagerank`, `amount_received`,
  `max_amount_received`, `pass_through`, `dwell_time_min` e `core_number`.

## 3. Cuidados na interpretação

* **O cenário `repasse_lento` não está "limpo".** Com esperas de ~6 h, os repasses caem em
  qualquer hora, inclusive de madrugada, e o `night_ratio` volta a separar fortemente
  (δ = 0,71). É por isso que o tabular melhora nesse cenário (DBSCAN: 0,10 → 0,23). O
  gerador precisa aplicar o perfil horário também aos repasses.
* **Vários sinais que sobrevivem ainda são hipóteses do gerador.** Os golpes valem ~4,5x
  um Pix típico (`fraud_amount_shift`), o que alimenta `amount_received`,
  `max_amount_received`, o PageRank (ponderado pelo valor) e o `oddball_ew`. O
  `clustering` baixo vem de a laranja receber de vítimas que, em geral, não se conhecem,
  e o `pass_through` alto vem de ela repassar quase tudo. São padrões plausíveis, mas
  suas intensidades foram escolhidas por nós.
* A taxa de fraude do `realista` (0,6% das contas) ainda é muito maior que a real.
* Tudo aqui é sintético. A pergunta "grafo ajuda?" só fica respondida de verdade com dados
  que não fomos nós que geramos.

## 4. Conclusão parcial

No dataset sintético, **a vantagem aparente dos atributos tabulares vinha de sinais que o
próprio gerador embute**. Com esses atalhos desligados, os atributos de grafo superam os
tabulares em todas as sementes e com os dois detectores, e a combinação de todos os
grupos (`completo`) é a abordagem mais robusta. Isso reforça a hipótese da pesquisa, com
as ressalvas da seção 3.

## 5. Próximos passos

1. Fazer os repasses seguirem o perfil horário, para o `repasse_lento` isolar só o efeito
   da demora.
2. Um cenário com `fraud_amount_shift: 0` (golpes do tamanho de um Pix comum), para medir
   quanto dos resultados vem do valor.
3. Rodar o pipeline no AMLworld (`scripts/importar_dataset.py`), onde os padrões não foram
   definidos por nós.
4. Calibrar valores e taxas do gerador com os dados abertos do BCB (`pixfraud.bcb`).
5. Ablação por atributo (tirar um de cada vez do `completo`), para medir a contribuição de
   cada um.
