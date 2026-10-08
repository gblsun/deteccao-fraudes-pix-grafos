---
tags: [mapa]
---

# Modelos

Esta nota explica **cada modelo da pesquisa**: a ideia, como ele vira um escore de risco,
quais hiperparâmetros tem, como eles foram otimizados e **como cada modelo se saiu** nas
redes sintéticas, das fáceis às mais realistas. Cada modelo está num arquivo `.py`
próprio nesta pasta. O porquê de cada escolha, com as referências, está em
[modelos.md](../../../docs/modelos.md); a história dos experimentos, em
[resultados.md](../../../docs/resultados.md).

## Supervisionado, semi-supervisionado ou não supervisionado?

Todo modelo daqui recebe as contas e devolve uma **fila de risco**: um escore por conta,
quanto maior mais suspeita. O que muda é **com o que ele aprende**.

- **Não supervisionados** ([`unsupervised/`](unsupervised/__init__.py)) nunca veem o
  gabarito (quem é fraude). Aprendem como é o *normal* e apontam o que destoa. É a aposta
  da pesquisa, porque no Pix real quase não há rótulos.
- **Semi-supervisionados** ([`semi_supervised/`](semi_supervised/__init__.py)) usam só as
  **poucas** fraudes já conhecidas, como um banco de verdade, que só descobre parte das
  fraudes, e tarde, pelas contestações (MED). Não são treinados: espalham a suspeita
  dessas contas pelo grafo.
- **Supervisionados** ([`supervised/`](supervised/__init__.py)) aprendem com o gabarito
  completo quais combinações de atributos marcam uma fraude. Entram como **teto**: mostram
  até onde se chegaria se todas as respostas fossem conhecidas. Sempre em validação
  cruzada ([`cross_validation.py`](supervised/cross_validation.py)): cada conta recebe a
  nota de um modelo que **não viu o rótulo dela**.

O gabarito também é usado para **dar a nota** de todos os modelos, depois que eles montam
a fila. A nota é a **average precision** (AP; ver
[glossário](../../../docs/glossario/average-precision.md)): de 0 a 1, quanto as fraudes de
verdade ficam no topo da fila. Um sorteio ao acaso tira AP igual à fração de fraudes da
rede, entre 0,1% e 2% aqui; esse é o piso.

## As pastas

```
models/
  base.py                    Detection (escore + rótulo) e prepare_matrix (log1p + padronização)
  torch_utils.py             o que as redes neurais para grafos compartilham (torch opcional)
  unsupervised/              não veem o gabarito
    proximity/               knn.py  dbscan.py  local_outlier_factor.py  kmeans.py
    statistical/             pca.py  ecod.py
    isolation/               isolation_forest.py
    boundary/                one_class_svm.py
    neural/                  autoencoder.py  dominant.py (torch)
    graph/                   fraudar.py  node2vec.py
  semi_supervised/           usam só as fraudes já conhecidas
    personalized_pagerank.py  label_spreading.py
  supervised/                aprendem com o gabarito, em validação cruzada
    cross_validation.py
    trees/                   random_forest.py  gradient_boosting.py
    neural/                  graphsage.py  graphsage_directed.py (torch)
```

Cada família tem um `__init__.py` que explica a ideia comum e exporta os modelos dela. Os
registros `DETECTORS`, `GRAPH_DETECTORS` e `FAMILIES` (em `unsupervised/__init__.py`) e
`SUPERVISED` (em `supervised/__init__.py`) ligam o nome de cada modelo, o mesmo da seção
`modelos` de [`configs/experimento.yaml`](../../../configs/experimento.yaml), à sua
função. Os módulos antigos `pixfraud.anomaly`, `pixfraud.graph_models`, `pixfraud.gnn` e
as funções de propagação de `pixfraud.flow` só reexportam daqui, para notebooks e scripts
antigos continuarem funcionando.

A otimização dos hiperparâmetros está no subpacote [`tuning/`](../tuning/__init__.py),
com as grades em [`configs/busca_hiperparametros.yaml`](../../../configs/busca_hiperparametros.yaml).

## Cada modelo

Todos os que usam a tabela de atributos recebem os mesmos 20 atributos por conta (o
conjunto `completo`: grau, PageRank, OddBall, k-núcleo, tempo de permanência...), com
`log1p` e padronização.

### Não supervisionados

| Família | Modelo | Arquivo | A conta é suspeita quando... | Escore |
|---|---|---|---|---|
| proximidade | **kNN** | [`knn.py`](unsupervised/proximity/knn.py) | ...está longe dos seus `k` vizinhos mais próximos | distância média (ou a maior) aos `k` vizinhos |
| proximidade | DBSCAN | [`dbscan.py`](unsupervised/proximity/dbscan.py) | ...fica fora das regiões densas, com um raio único para todos ([glossário](../../../docs/glossario/dbscan-e-k-distance.md)) | distância ao `min_samples`-ésimo vizinho |
| proximidade | LOF | [`local_outlier_factor.py`](unsupervised/proximity/local_outlier_factor.py) | ...a vizinhança dela é menos densa que a dos vizinhos dela ([glossário](../../../docs/glossario/lof.md)) | fator de outlier local |
| proximidade | **k-means** | [`kmeans.py`](unsupervised/proximity/kmeans.py) | ...está longe do centro de todos os grupos grandes de perfis (regra do CBLOF, para um grupinho de laranjas não ganhar um centro só dele) | distância ao centro grande mais próximo |
| estatística | **PCA** | [`pca.py`](unsupervised/statistical/pca.py) | ...foge da correlação entre os atributos (ex.: recebe de muitas contas, mas quase nenhum dinheiro) | soma das projeções nas componentes principais, cada uma dividida pela variância |
| estatística | ECOD | [`ecod.py`](unsupervised/statistical/ecod.py) | ...está na cauda de vários atributos, cada um olhado sozinho | soma de `-log` das probabilidades de cauda |
| isolamento | Isolation Forest | [`isolation_forest.py`](unsupervised/isolation/isolation_forest.py) | ...é isolada com poucos cortes aleatórios ([glossário](../../../docs/glossario/isolation-forest.md)) | profundidade média até isolar, com sinal trocado |
| fronteira | One-Class SVM | [`one_class_svm.py`](unsupervised/boundary/one_class_svm.py) | ...fica fora da fronteira (núcleo RBF) que envolve a maioria | distância para fora da fronteira |
| rede neural | Autoencoder | [`autoencoder.py`](unsupervised/neural/autoencoder.py) | ...uma rede que aprendeu a reconstruir as contas típicas erra ao reconstruí-la | erro médio de reconstrução |
| rede neural | DOMINANT | [`dominant.py`](unsupervised/neural/dominant.py) | ...um autoencoder de grafo erra ao reconstruir os atributos **e as ligações** dela ([glossário](../../../docs/glossario/redes-neurais-para-grafos.md)) | erro de reconstrução combinado |
| estrutura do grafo | FRAUDAR | [`fraudar.py`](unsupervised/graph/fraudar.py) | ...está num bloco denso, como uma quadrilha em que várias laranjas pagam os mesmos intermediários ([glossário](../../../docs/glossario/fraudar.md)) | peso do núcleo na remoção gulosa |
| estrutura do grafo | node2vec + IF | [`node2vec.py`](unsupervised/graph/node2vec.py) | ...ocupa uma posição rara num vetor aprendido de passeios aleatórios | Isolation Forest sobre o vetor |

### Semi-supervisionados

| Modelo | Arquivo | Ideia |
|---|---|---|
| PageRank personalizado | [`personalized_pagerank.py`](semi_supervised/personalized_pagerank.py) | "culpa por associação": a suspeita parte das fraudes conhecidas e se espalha pelos caminhos do dinheiro; a versão relativa divide pelo PageRank comum, para não favorecer comércios ([glossário](../../../docs/glossario/propagacao-de-risco.md)) |
| Label spreading | [`label_spreading.py`](semi_supervised/label_spreading.py) | o mesmo, usando também as contas sabidamente legítimas, que puxam as vizinhas para baixo |

Nos estudos, cada um também é combinado com o DBSCAN, pela média dos percentis
(`combinado`), para juntar "parece estranha" com "está perto de uma fraude conhecida".

### Supervisionados (teto)

| Família | Modelo | Arquivo | Ideia |
|---|---|---|---|
| árvores | Random Forest | [`random_forest.py`](supervised/trees/random_forest.py) | muitas árvores de decisão independentes votam ([glossário](../../../docs/glossario/random-forest.md)) |
| árvores | Gradient boosting | [`gradient_boosting.py`](supervised/trees/gradient_boosting.py) | árvores em sequência, cada uma corrigindo o erro das anteriores (estilo LightGBM) |
| rede neural | GraphSAGE | [`graphsage.py`](supervised/neural/graphsage.py), [`graphsage_directed.py`](supervised/neural/graphsage_directed.py) | rede neural para grafos: cada conta mistura seus atributos com os dos vizinhos, e a rede aprende o que combinar |

## Como cada modelo se saiu

Average precision média e IC 95% em **10 redes de teste** (sementes 1 a 10) de cada
cenário, todos os modelos avaliados nas mesmas contas, com a configuração escolhida à mão
([`configs/experimento.yaml`](../../../configs/experimento.yaml)). Os semi-supervisionados
conhecem 25% das fraudes (ou as contestadas, no `calibrado`); essas contas, e 25% das
legítimas, ficam fora da nota de **todos** os modelos. Gerado por
`scripts/avaliar_modelos.py`; dados em `reports/results/modelos_resumo.csv`. Ordenado pela
AP no cenário `realista`.

| Modelo | base | realista | negativos_dificeis | quadrilhas_realistas | calibrado |
|---|---|---|---|---|---|
| Random Forest | 1,00 (1,00–1,00) | 0,99 (0,99–1,00) | 0,99 (0,98–1,00) | 0,95 (0,91–1,00) | 0,99 (0,96–1,01) |
| PageRank + DBSCAN | 0,77 (0,66–0,89) | 0,95 (0,83–1,06) | 0,94 (0,83–1,06) | 0,94 (0,90–0,98) | 0,95 (0,89–1,00) |
| Gradient boosting | 0,98 (0,97–0,99) | 0,90 (0,84–0,97) | 0,88 (0,82–0,94) | 0,93 (0,88–0,97) | 0,97 (0,94–1,00) |
| PageRank relativo | 0,60 (0,50–0,70) | 0,71 (0,57–0,84) | 0,73 (0,60–0,86) | 0,90 (0,82–0,97) | 0,87 (0,78–0,97) |
| **PCA** | 0,82 (0,79–0,85) | 0,62 (0,56–0,67) | 0,51 (0,45–0,57) | 0,59 (0,49–0,69) | 0,41 (0,36–0,47) |
| Autoencoder | 0,73 (0,66–0,79) | 0,50 (0,39–0,62) | 0,48 (0,36–0,59) | 0,47 (0,26–0,68) | 0,60 (0,48–0,72) |
| DBSCAN | 0,79 (0,75–0,83) | 0,49 (0,44–0,54) | 0,34 (0,29–0,39) | 0,37 (0,29–0,45) | 0,13 (0,10–0,16) |
| LOF | 0,16 (0,12–0,21) | 0,46 (0,41–0,50) | 0,35 (0,27–0,42) | 0,35 (0,27–0,42) | 0,08 (0,05–0,10) |
| **kNN** | 0,78 (0,74–0,82) | 0,44 (0,37–0,50) | 0,31 (0,24–0,37) | 0,26 (0,19–0,32) | 0,09 (0,07–0,11) |
| Label spreading + DBSCAN | 0,85 (0,81–0,88) | 0,32 (0,16–0,48) | 0,38 (0,25–0,51) | 0,63 (0,47–0,78) | 0,35 (0,21–0,49) |
| One-Class SVM | 0,64 (0,60–0,69) | 0,31 (0,27–0,36) | 0,22 (0,16–0,28) | 0,16 (0,13–0,19) | 0,18 (0,13–0,23) |
| Isolation Forest | 0,58 (0,52–0,64) | 0,25 (0,19–0,31) | 0,16 (0,12–0,19) | 0,35 (0,27–0,43) | 0,08 (0,06–0,09) |
| **k-means** | 0,34 (0,31–0,38) | 0,16 (0,12–0,20) | 0,16 (0,13–0,18) | 0,18 (0,14–0,21) | 0,10 (0,08–0,12) |
| Label spreading | 0,71 (0,66–0,75) | 0,13 (0,05–0,22) | 0,24 (0,11–0,37) | 0,52 (0,35–0,68) | 0,31 (0,17–0,45) |
| ECOD | 0,35 (0,29–0,42) | 0,08 (0,06–0,10) | 0,06 (0,04–0,07) | 0,10 (0,06–0,13) | 0,03 (0,02–0,03) |
| node2vec + IF | 0,05 (0,03–0,07) | 0,03 (0,00–0,07) | 0,02 (0,01–0,03) | 0,01 (0,01–0,01) | 0,00 (0,00–0,00) |
| FRAUDAR | 0,01 (0,01–0,01) | 0,00 (0,00–0,00) | 0,00 (0,00–0,00) | 0,00 (0,00–0,00) | 0,00 (0,00–0,00) |

A fração de fraudes, que é a AP de um sorteio ao acaso, é de 1,8% no `base`, entre 0,5% e
0,7% nos três do meio e 0,1% no `calibrado`.

### O que a tabela diz

- **O que a pesquisa propõe funciona nos cenários realistas:** conhecer algumas fraudes e
  espalhar a suspeita pelo grafo, combinado com um detector (PageRank + DBSCAN), fica perto
  do teto supervisionado (0,94 a 0,95 contra 0,95 a 0,99), sem precisar do gabarito inteiro.
- **Entre os não supervisionados puros, o PCA é o melhor** em quase todos os cenários; o
  autoencoder é o mais estável no `calibrado`. Os detectores de proximidade (DBSCAN, kNN,
  LOF) perdem muito quando o gerador deixa de embutir atalhos.
- **O Random Forest tira ~1,00 porque a rede sintética é fácil para quem tem o gabarito:**
  nenhum atributo sozinho separa as laranjas (o melhor, o tempo de permanência, tem AP 0,86
  sozinho), mas a combinação "repassa rápido, sem círculo de amigos, paga poucas contas"
  só existe nelas, e nenhum cenário desliga essa assinatura. É uma limitação do gerador, a
  registrar no relatório, não um mérito do modelo.
- **Só a estrutura não basta:** FRAUDAR e node2vec ficam no nível do acaso, porque as
  quadrilhas do gerador não formam blocos densos.
- **Cuidado com os intervalos:** nos cenários realistas cada rede tem só ~8 a 10 fraudes
  avaliadas, e os IC são largos; diferenças de poucos centésimos não são conclusivas.

## Otimização dos hiperparâmetros

As grades estão em
[`configs/busca_hiperparametros.yaml`](../../../configs/busca_hiperparametros.yaml). A
busca ([`tuning/`](../tuning/__init__.py), `scripts/otimizar_hiperparametros.py`) usa 6
redes de **validação** (sementes 1001 e 1002 dos cenários `realista`, `negativos_dificeis`
e `quadrilhas_realistas`), nunca as de teste. Ela roda em rodadas: quando o vencedor cai
na ponta da grade, a grade cresce naquela direção, até o vencedor ficar no meio ou bater num
limite. Foram 4 rodadas e 173 combinações. Ver
[otimização de hiperparâmetros](../../../docs/glossario/otimizacao-de-hiperparametros.md).

| Modelo | AP na validação: padrão → otimizado | O que mudou |
|---|---|---|
| Random Forest | 0,99 → 0,99 | manteve |
| Gradient boosting | 0,93 → 0,98 | `learning_rate` 1,0, `max_leaf_nodes` 2, `min_samples_leaf` 80 |
| Autoencoder | 0,49 → 0,73 | `alpha` 0,1, `bottleneck` 0,5 |
| PCA | 0,54 → 0,59 | só as componentes menores (`components: minor`) |
| LOF | 0,45 → 0,53 | `n_neighbors` 100 |
| k-means | 0,15 → 0,46 | `large_fraction` 0,99 (16 grupos) |
| kNN | 0,38 → 0,44 | a maior das `k` distâncias, em vez da média |
| DBSCAN | 0,44 → 0,44 | manteve |
| Isolation Forest | 0,26 → 0,41 | metade dos atributos por árvore, todas as contas por árvore |
| One-Class SVM | 0,26 → 0,30 | `gamma` 0,03 |
| node2vec + IF | 0,03 → 0,03 | manteve |

Alguns vencedores pararam num **limite** que não faz sentido passar, e não no meio da
grade: `large_fraction` 0,99 (quase todos os grupos contam como "grandes"), `max_samples`
1,0 (todas as contas) e o gradient boosting com árvores de um corte só e passo 1,0. Esses
são o melhor dentro do possível. Detalhes de cada candidato em
`reports/results/otimizacao_resumo.csv`.

### O ganho de verdade: nas redes de teste

A nota na validação é otimista, porque a configuração foi escolhida nela. O que vale é a AP
nas **mesmas 10 redes de teste** da tabela acima, com
[`configs/experimento_otimizado.yaml`](../../../configs/experimento_otimizado.yaml): padrão →
otimizado, e `*` quando a diferença pareada por semente é significativa (Wilcoxon, p <
0,05). Dados em `reports/otimizado/results/`.

| Modelo | base | realista | negativos_dificeis | quadrilhas_realistas | calibrado |
|---|---|---|---|---|---|
| Random Forest | 1,00 → 1,00 | 0,99 → 0,99 | 0,99 → 0,99 | 0,95 → 0,95 | 0,99 → 0,99 |
| Gradient boosting | 0,98 → 1,00 * | 0,90 → 0,98 | 0,88 → 0,97 * | 0,93 → 0,94 | 0,97 → 0,99 |
| PageRank + DBSCAN | 0,77 → 0,77 | 0,95 → 0,95 | 0,94 → 0,94 | 0,94 → 0,94 | 0,95 → 0,95 |
| **PCA** | 0,82 → 0,82 | 0,62 → **0,72** * | 0,51 → 0,59 * | 0,59 → 0,67 * | 0,41 → 0,53 * |
| PageRank relativo | 0,60 → 0,60 | 0,71 → 0,71 | 0,73 → 0,73 | 0,90 → 0,90 | 0,87 → 0,87 |
| Autoencoder | 0,73 → 0,72 | 0,50 → 0,64 | 0,48 → 0,50 | 0,47 → 0,39 | 0,60 → **0,25** * |
| LOF | 0,16 → 0,94 * | 0,46 → 0,58 * | 0,35 → 0,37 | 0,35 → 0,57 * | 0,08 → 0,22 * |
| **k-means** | 0,34 → 0,51 * | 0,16 → 0,56 * | 0,16 → 0,25 | 0,18 → 0,47 * | 0,10 → 0,18 * |
| DBSCAN | 0,79 → 0,79 | 0,49 → 0,49 | 0,34 → 0,34 | 0,37 → 0,37 | 0,13 → 0,13 |
| **kNN** | 0,78 → 0,79 | 0,44 → 0,48 * | 0,31 → 0,34 * | 0,26 → 0,39 * | 0,09 → 0,14 * |
| Isolation Forest | 0,58 → 0,72 * | 0,25 → 0,45 * | 0,16 → 0,28 * | 0,35 → 0,44 | 0,08 → 0,26 * |
| One-Class SVM | 0,64 → 0,65 | 0,31 → 0,36 * | 0,22 → 0,22 | 0,16 → 0,26 * | 0,18 → 0,17 |
| Label spreading + DBSCAN | 0,85 → 0,85 | 0,32 → 0,32 | 0,38 → 0,38 | 0,63 → 0,63 | 0,35 → 0,35 |
| Label spreading | 0,71 → 0,71 | 0,13 → 0,13 | 0,24 → 0,24 | 0,52 → 0,52 | 0,31 → 0,31 |
| ECOD | 0,35 → 0,35 | 0,08 → 0,08 | 0,06 → 0,06 | 0,10 → 0,10 | 0,03 → 0,03 |
| node2vec + IF | 0,05 → 0,05 | 0,03 → 0,03 | 0,02 → 0,02 | 0,01 → 0,01 | 0,00 → 0,00 |
| FRAUDAR | 0,01 → 0,01 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 | 0,00 → 0,00 |

- **A otimização ajudou quase todos os não supervisionados, e o ganho se confirmou no
  teste.** O PCA, usando só as componentes menores, passou de 0,62 para 0,72 no `realista`
  e segue o melhor não supervisionado. O k-means, que era um dos piores, mais que triplicou
  no `realista` (0,16 → 0,56). LOF, Isolation Forest e kNN também subiram com significância
  na maioria dos cenários.
- **O autoencoder é o alerta:** melhorou na validação (0,49 → 0,73), mas no teste caiu de
  0,60 para 0,25 no `calibrado`, a rede maior e com fraudes mais raras, que não entrou na
  validação. A regularização forte escolhida (`alpha` 0,1) não se generalizou. É o motivo de
  separar validação e teste, e por isso **a configuração otimizada não deve ser usada para
  o autoencoder no `calibrado`**.
- **Os semi-supervisionados não mudam**, porque não têm hiperparâmetros na grade; as
  combinações usam o DBSCAN, que manteve a configuração. "PageRank + DBSCAN" continua o
  melhor sem o gabarito completo.
- **O teto quase não muda:** o gradient boosting encosta no Random Forest, e os dois ficam
  em ~0,95 a 1,00.

## Como reproduzir

```powershell
python scripts/avaliar_modelos.py --cenarios base realista negativos_dificeis quadrilhas_realistas calibrado --sementes 10 --processos 4
python scripts/otimizar_hiperparametros.py --processos 4
python scripts/avaliar_modelos.py --config configs/experimento_otimizado.yaml --saida reports/otimizado --cenarios base realista negativos_dificeis quadrilhas_realistas calibrado --sementes 10 --processos 4
```

Cerca de 40 min, 1 h e 40 min, com 4 processos.
