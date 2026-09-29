---
tags: [metodo]
---

# Modelos usados na pesquisa (e outros que caberiam)

Este documento explica **o que cada modelo faz, por que ele está aqui e como está
configurado**. Os resultados de cada um estão em [resultados.md](resultados.md); os
parâmetros, em [`configs/experimento.yaml`](../configs/experimento.yaml).

As referências citadas estão em [`referencias.bib`](referencias.bib), com fichamento em
[`leituras/`](leituras/mapa-das-leituras.md).

A pesquisa é, por escolha da proposta, **não supervisionada**: o detector não vê rótulos.
Isso imita a situação real de um banco, em que a fraude só é conhecida depois (e em
parte), pelas contestações. Os modelos supervisionados que aparecem aqui servem de
**referência**, não de solução.

## Como as peças se encaixam

```mermaid
flowchart LR
    tx["Pix (tabela)"] --> grafo["grafo de contas"]
    grafo --> atributos["atributos por conta<br/>(tabulares, temporais, de grafo)"]
    louvain["Louvain<br/>(comunidades)"] --> atributos
    oddball["OddBall<br/>(egonets)"] --> atributos
    atributos --> escala["log1p + padronização"]
    escala --> iforest["Isolation Forest"]
    escala --> dbscan["DBSCAN"]
    escala --> lof["LOF"]
    iforest --> escore["escore de risco por conta"]
    dbscan --> escore
    lof --> escore
    escore --> metricas["AP, precision@k, figuras"]
    contestacoes["fraudes já conhecidas<br/>(MED)"] --> propagacao["PageRank personalizado"]
    propagacao --> escore
```

## 1. Preparação dos atributos

Antes de qualquer modelo, cada atributo passa por `log(1 + x)` e é padronizado
(`pixfraud.anomaly.prepare_matrix`).

* **Por que o log**: valores de Pix, graus e PageRank têm cauda muito pesada. Sem o log,
  uma única conta com R$ 1 milhão domina todas as distâncias.
* **Por que padronizar**: os dois detectores usam distância (o DBSCAN diretamente, o
  Isolation Forest ao escolher cortes); sem padronizar, o atributo de maior escala manda.
* **Consequência**: os atributos precisam ser não negativos. O código recusa valores
  negativos com mensagem explícita, em vez de deixar o `log1p` virar `NaN`.

## 2. [Isolation Forest](glossario/isolation-forest.md) (não supervisionado)

**Ideia.** Sorteia um atributo e um corte ao acaso, muitas vezes, montando árvores. Uma
conta anômala fica isolada com **poucos cortes**, porque está longe das outras; o escore é
o inverso da profundidade média de isolamento (Liu, Ting e Zhou, 2008).

**Por que é adequado.** Não supõe formato de grupo (nem esférico, nem denso), lida bem com
muitos atributos e é rápido: 300 árvores em 2 mil contas levam menos de 1 segundo.

**Configuração** (`modelos.isolation_forest`): `n_estimators: 300` (mais árvores, menos
variação entre execuções), `contamination: auto` (não fixamos a fração esperada de
fraudes, que na prática não se conhece) e `seed`.

**Onde ele é melhor.** Nos conjuntos com muitos atributos estruturais
(`grafo_avancado`: AP 0,63) e nos temporais (0,57). Ele erra mais quando os atributos são
poucos e redundantes.

## 3. [DBSCAN](glossario/dbscan-e-k-distance.md) (não supervisionado)

**Ideia.** Agrupa pontos em regiões densas: uma conta é **núcleo** se tem ao menos
`min_samples` vizinhos dentro do raio `eps`; quem não é núcleo nem está perto de um é
**ruído**, e ruído é o que chamamos de anomalia (Ester et al., 1996).

**O escore.** O DBSCAN só devolve rótulos, não um escore contínuo. Usamos como escore a
**distância ao `min_samples`-ésimo vizinho** (k-distance), que é exatamente a grandeza que
define se a conta é núcleo. Assim conseguimos ordenar as contas e calcular average
precision e precision@k.

**Configuração** (`modelos.dbscan`):

| Parâmetro | Valor | Por quê |
|---|---|---|
| `min_samples` | 10 | quantos vizinhos definem "região densa" |
| `eps` | `auto` | escolhido pelo quantil das k-distances, para não depender da escala |
| `eps_quantile` | 0,95 | ~5% das contas ficam fora dos núcleos |
| `max_exact` | 20.000 | **até quantas contas gastar memória** com o rótulo exato (ver abaixo) |

**Memória.** O DBSCAN guarda a vizinhança de cada ponto. Com `eps` no quantil 0,95, cada
conta tem em média ~20% das contas por vizinha, então a memória cresce com o **quadrado**
do número de contas: 7 MB com 2.142 contas, ~4 GB com 50 mil, ~16 GB com 100 mil. Acima de
`max_exact`, o rótulo binário passa a ser "não é ponto de núcleo" (`k-distance > eps`),
que concorda com o DBSCAN em 97,6% das contas; o escore não muda, então **AP e
precision@k ficam idênticas**. Aumente `max_exact` se tiver RAM sobrando.

**Onde ele é melhor.** Com muitos atributos combinados (`completo`: AP 0,78 no cenário
base e 0,50 no realista), e é o melhor dos dois na maioria dos cenários.

## 4. [Local Outlier Factor — LOF](glossario/lof.md) (não supervisionado)

**Ideia.** Em vez de um raio único para toda a base (como o [DBSCAN](#3-dbscan-não-supervisionado)),
compara a densidade em volta de cada conta com a densidade em volta dos seus vizinhos.
Acha anomalias **locais**: uma conta pode estar numa região esparsa da rede sem ser
anômala, se seus vizinhos também estiverem espalhados.

**Configuração** (`modelos.local_outlier_factor`): `n_neighbors: 20`.

**Resultado.** Foi o terceiro detector avaliado nos mesmos estudos (10 sementes,
[`avaliar_robustez.py`](../scripts/mapa-dos-scripts.md) e
[`avaliar_cenarios.py`](../scripts/mapa-dos-scripts.md)), e **não superou os outros dois em
nenhum cenário**. No cenário base, `tabular` é o melhor conjunto para ele (AP 0,51,
comparável ao DBSCAN antes do ajuste dos atalhos), mas nos conjuntos de grafo ele fica bem
abaixo (`grafo`: 0,06; `grafo_avancado`: 0,08) — justamente onde o DBSCAN e o Isolation
Forest se destacam. A causa provável: em vários conjuntos, sobretudo o `temporal`, há
muitas contas com atributos praticamente idênticos (ex.: pessoas que nunca repassam
dinheiro), o que degenera o cálculo de densidade local do LOF (o scikit-learn avisa disso
em tempo de execução). Mantido no código como terceiro detector — útil como contraponto —,
mas os resultados principais da pesquisa continuam se apoiando no Isolation Forest e no
DBSCAN.

## 5. Louvain e OddBall (dentro dos atributos)

Não são detectores, mas dois algoritmos de grafo que **produzem atributos**:

* **[Louvain](glossario/comunidades-e-modularidade.md)** (`pixfraud.communities`): encontra comunidades
  maximizando a modularidade. Dele sai o *[coeficiente de participação](glossario/coeficiente-de-participacao.md)*: quanto as ligações de uma conta se espalham
  por comunidades diferentes. As contas da quadrilha têm participação um pouco maior que
  as legítimas (efeito pequeno, delta de Cliff entre 0,26 e 0,43).
* **[OddBall](glossario/egonet-e-oddball.md)** (Akoglu, Tong e Koutra, 2015): em redes reais, o número de arestas e o valor
  movimentado na vizinhança de uma conta seguem leis de potência em função do número de
  vizinhos. O escore mede o quanto a conta **foge dessas leis**: vizinhança em estrela
  (vítimas que não se conhecem) ou dinheiro demais para o tamanho da vizinhança. Foi o
  atributo com maior efeito em todos os cenários.

## 6. [PageRank](glossario/pagerank.md) personalizado, para "[culpa por associação](glossario/propagacao-de-risco.md)" (semi-supervisionado)

**Ideia.** Partindo das contas já conhecidas como fraudulentas (as contestações do MED),
um passeio aleatório que sempre volta para elas mede o quanto cada outra conta está
**perto** delas, e por quantos caminhos (Easley e Kleinberg, 2010). É o
`pixfraud.flow.propagate_risk`.

**Por que importa.** É o único modelo aqui que usa rótulos, e usa os que um banco já tem.
Combinado com o detector (média dos percentis), levou a average precision de 0,46 para
0,95 no cenário mais realista, com 25% das fraudes conhecidas.

## 7. [Random Forest](glossario/random-forest.md), como teto (supervisionado)

Serve só de referência: treinado **com os rótulos** ([validação cruzada](glossario/validacao-cruzada.md) de 5 partes), mostra
até onde daria para chegar se eles existissem. Chega a AP 0,99 contra 0,53 do melhor não
supervisionado. A distância entre os dois é o custo de não ter rótulos, e é o que
justifica a seção anterior.

## 8. [FRAUDAR](glossario/fraudar.md) (não supervisionado, só estrutura)

**Ideia.** Procura blocos densos um depois do outro (Hooi et al., 2016), com arestas que
valem menos quando chegam a contas muito procuradas, para resistir a camuflagem. É o
`communities.fraudar_blocks`; `communities.fraudar_scores` transforma os blocos num escore
por conta (a densidade do bloco), ignorando blocos com mais de 5% das contas.

**Configuração.** `--blocos 10` e `--fatia-maxima 0.05` em
[`avaliar_fraudar.py`](../scripts/avaliar_fraudar.py). Sem rótulos e sem atributos.

**Onde é melhor.** Sozinho, perde para o DBSCAN; combinado com ele, é a melhor opção não
supervisionada enquanto a rede legítima não se parte em muitos círculos pequenos e densos
(ver [resultados, seção 9](resultados.md)).

## 9. [Redes neurais para grafos](glossario/redes-neurais-para-grafos.md) (GNN)

**Ideia.** A conta ganha uma representação aprendida a partir dos próprios atributos e dos
vizinhos, em duas camadas. Está em [`pixfraud.gnn`](../src/pixfraud/gnn.py), com PyTorch e
sem PyTorch Geometric (dependência opcional: `pip install -e ".[gnn]"`):

* `dominant_scores`: autoencoder de grafo DOMINANT (Ding et al., 2019), **não
  supervisionado**; o escore é o erro de reconstrução dos atributos e das ligações;
* `sage_supervised_scores`: GraphSAGE (Hamilton, Ying e Leskovec, 2017), **supervisionada**,
  em validação cruzada de 5 partes, como teto ao lado do Random Forest.

**Configuração.** Duas camadas de 64 unidades (DOMINANT: 64 e 32), Adam, 300 épocas no
DOMINANT e 200 na GraphSAGE, fraudes com peso maior na perda. Nenhum ajuste fino ainda.

**Onde é melhor.** A GraphSAGE com só os atributos tabulares chega perto do teto com todos
os atributos feitos à mão (0,92 contra 0,99 no `realista`): a rede aprende a estrutura. O
DOMINANT, sem rótulos, ainda fica abaixo do DBSCAN (ver [resultados, seção
10](resultados.md)).

---

## Outros modelos que caberiam nesta pesquisa

Ordenados pelo que rende mais com o esforço que exigem. Todos entram pelo mesmo lugar:
uma função em [`anomaly.py`](../src/pixfraud/anomaly.py) que devolve `Detection` e uma
entrada em `DETECTORS`; as comparações e figuras funcionam sem mudança.

> O [LOF](#4-local-outlier-factor--lof-não-supervisionado) (seção 4), o FRAUDAR (seção 8)
> e as GNN (seção 9) já estão implementados e avaliados; aparecem na tabela só com o que
> falta fazer com eles.

| Modelo | O que traria de novo | Esforço | Cuidado |
|---|---|---|---|
| **ECOD / COPOD** | anomalia pela cauda da distribuição de cada atributo; não tem parâmetro para ajustar e é muito rápido | baixo (biblioteca PyOD) | ignora a relação entre atributos |
| **One-Class SVM** | fronteira não linear em volta do "normal" | baixo | custo cresce rápido com o nº de contas |
| **Autoencoder** | aprende a reconstruir contas normais; o erro de reconstrução vira o escore | médio (PyTorch) | precisa de mais dados e de ajuste; menos interpretável |
| **node2vec + detector** | transforma a vizinhança de cada conta num vetor aprendido, em vez de atributos escolhidos à mão | médio | o vetor não é interpretável, o que conflita com o objetivo de explicar |
| **GNN: GAT, PNA, poucos rótulos** | a GraphSAGE já foi avaliada (seção 9); faltam atenção entre vizinhos (GAT), agregadores múltiplos (PNA, estado da arte em lavagem; Altman et al., 2023) e o cenário real de poucos rótulos | médio (a base em `pixfraud.gnn` já existe) | vazamento de informação; o vetor aprendido não é interpretável |
| **FRAUDAR com tempo** | o FRAUDAR já foi avaliado (seção 8); falta um peso que favoreça ligações feitas em poucas horas, como as das quadrilhas | baixo | o critério de "bloco grande demais" (5%) ainda é heurístico |
| **Propagação de rótulos (label spreading)** | alternativa à propagação por PageRank, com rótulos positivos e negativos | baixo | precisa de exemplos negativos confiáveis |
| **Modelos de séries temporais por conta** (por exemplo, detecção de rajadas) | trata a sequência de Pix como sinal no tempo, em vez de agregados | médio | mais complexo de avaliar junto com o grafo |
| **Gradient boosting (XGBoost, LightGBM)** | teto supervisionado mais forte que o Random Forest | baixo | mesma limitação: depende de rótulos |

**Sugestão de ordem**, se for para acrescentar algum:

1. **ECOD**: barato, entra como mais uma coluna nas comparações que já existem. O LOF já
   foi testado (seção 4) e não superou o Isolation Forest nem o DBSCAN; o ECOD, por ignorar
   a relação entre atributos, é um contraponto diferente, não uma repetição.
2. **GNN com poucos rótulos**: treinar a GraphSAGE só com as contestações do MED (10% a
   25% das fraudes), para comparar com a culpa por associação da seção 6 no mesmo cenário.
3. **FRAUDAR com tempo**: pesos que favoreçam ligações feitas em poucas horas.
