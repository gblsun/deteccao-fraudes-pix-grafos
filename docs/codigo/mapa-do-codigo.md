---
tags: [mapa]
---

# Mapa do código

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Uma nota por módulo do pacote `pixfraud`, por pasta de scripts e por diretório, geradas a partir das docstrings. Cada nota de módulo diz quem o usa, e esses links aparecem no grafo do Obsidian. Para o desenho de como as peças se encaixam, ver o [README do pacote](../../src/pixfraud/README.md); para a ordem da pesquisa, o [fluxo da pesquisa](../fluxo-da-pesquisa.md).

- [Diretórios](diretorios.md): todos, com o que guardam

## Pacote `pixfraud`

| Módulo | O que faz |
|---|---|
| [`pixfraud`](pixfraud.md) | Detecção de fraudes em transações PIX com teoria dos grafos e machine learning. |
| [`pixfraud.algorithms`](pixfraud.algorithms.md) | Algoritmos clássicos de teoria dos grafos aplicados às transações. |
| [`pixfraud.anomaly`](pixfraud.anomaly.md) | Detectores de anomalia não supervisionados aplicados aos atributos das contas. |
| [`pixfraud.bcb`](pixfraud.bcb.md) | Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil. |
| [`pixfraud.communities`](pixfraud.communities.md) | Comunidades, núcleos, subgrafos densos e egonets. |
| [`pixfraud.evaluation`](pixfraud.evaluation.md) | Métricas de desempenho dos detectores, calculadas por conta. |
| [`pixfraud.experiment`](pixfraud.experiment.md) | Núcleo do experimento: transações -> grafo -> atributos -> detectores -> métricas. |
| [`pixfraud.exploration`](pixfraud.exploration.md) | O que o explorador interativo (`app/explorador.py`) e a página da rede precisam calcular. |
| [`pixfraud.explorer`](pixfraud.explorer.md) | Explorador interativo da rede inteira: uma página HTML com sigma.js (WebGL). |
| [`pixfraud.external`](pixfraud.external.md) | Carregadores de datasets públicos de fraude e lavagem de dinheiro. |
| [`pixfraud.features`](pixfraud.features.md) | Atributos por conta usados pelos detectores de anomalia. |
| [`pixfraud.flow`](pixfraud.flow.md) | Fluxo de dinheiro, cortes mínimos ("onde bloquear") e propagação de risco. |
| [`pixfraud.gnn`](pixfraud.gnn.md) | Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch. |
| [`pixfraud.graph`](pixfraud.graph.md) | Criação e manipulação dos grafos: contas são vértices e transferências são arestas. |
| [`pixfraud.graph_models`](pixfraud.graph_models.md) | Detectores que olham só para a estrutura do grafo, sem a tabela de atributos. |
| [`pixfraud.models`](pixfraud.models.md) | Todos os modelos de detecção, um arquivo por modelo, agrupados por tipo e por família. |
| [`pixfraud.models.base`](pixfraud.models.base.md) | O que todos os modelos compartilham: o formato da saída e a preparação dos atributos. |
| [`pixfraud.models.semi_supervised`](pixfraud.models.semi_supervised.md) | Modelos **semi-supervisionados**: usam só as poucas fraudes já conhecidas, como um banco de verdade. |
| [`pixfraud.models.semi_supervised.label_spreading`](pixfraud.models.semi_supervised.label_spreading.md) | Label spreading (Zhou et al., 2004): fraudes **e** contas legítimas conhecidas espalham o rótulo pelo grafo. |
| [`pixfraud.models.semi_supervised.personalized_pagerank`](pixfraud.models.semi_supervised.personalized_pagerank.md) | PageRank personalizado ("culpa por associação"): a suspeita parte das fraudes já conhecidas. |
| [`pixfraud.models.supervised`](pixfraud.models.supervised.md) | Modelos **supervisionados**: aprendem com o gabarito (quem é fraude), sempre em validação cruzada. |
| [`pixfraud.models.supervised.cross_validation`](pixfraud.models.supervised.cross_validation.md) | Validação cruzada dos modelos supervisionados: nenhuma conta recebe a nota de um modelo que viu o rótulo dela. |
| [`pixfraud.models.supervised.neural`](pixfraud.models.supervised.neural.md) | Redes neurais **para grafos** supervisionadas (precisam do `torch`, extra `gnn`). |
| [`pixfraud.models.supervised.neural.graphsage`](pixfraud.models.supervised.neural.graphsage.md) | GraphSAGE (Hamilton, Ying e Leskovec, 2017), implementação própria: rede neural para grafos supervisionada. |
| [`pixfraud.models.supervised.neural.graphsage_directed`](pixfraud.models.supervised.neural.graphsage_directed.md) | GraphSAGE direcionada, com PyTorch Geometric: uma convolução para quem pagou a conta e outra para quem recebeu. |
| [`pixfraud.models.supervised.trees`](pixfraud.models.supervised.trees.md) | Modelos supervisionados de **árvores de decisão**, sobre a tabela de atributos. |
| [`pixfraud.models.supervised.trees.gradient_boosting`](pixfraud.models.supervised.trees.gradient_boosting.md) | Gradient boosting (estilo LightGBM): árvores em sequência, cada uma corrigindo o erro das anteriores. |
| [`pixfraud.models.supervised.trees.random_forest`](pixfraud.models.supervised.trees.random_forest.md) | Random Forest (Breiman, 2001): muitas árvores de decisão, cada uma vendo uma amostra das contas, votam. |
| [`pixfraud.models.torch_utils`](pixfraud.models.torch_utils.md) | O que as redes neurais para grafos (DOMINANT e GraphSAGE) compartilham. |
| [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md) | Modelos **não supervisionados**: não veem o gabarito, procuram as contas que destoam das outras. |
| [`pixfraud.models.unsupervised.boundary`](pixfraud.models.unsupervised.boundary.md) | Modelos de **fronteira**: uma superfície envolve as contas normais, e a suspeita fica do lado de fora. |
| [`pixfraud.models.unsupervised.boundary.one_class_svm`](pixfraud.models.unsupervised.boundary.one_class_svm.md) | One-Class SVM (Schölkopf et al., 2001): uma fronteira que envolve a maior parte das contas. |
| [`pixfraud.models.unsupervised.graph`](pixfraud.models.unsupervised.graph.md) | Modelos de **estrutura do grafo**: recebem o grafo, não a tabela de atributos. |
| [`pixfraud.models.unsupervised.graph.fraudar`](pixfraud.models.unsupervised.graph.fraudar.md) | FRAUDAR (Hooi et al., 2016): contas em blocos densos, como uma quadrilha, ficam no topo. |
| [`pixfraud.models.unsupervised.graph.node2vec`](pixfraud.models.unsupervised.graph.node2vec.md) | node2vec + Isolation Forest: cada conta vira um vetor aprendido da sua vizinhança. |
| [`pixfraud.models.unsupervised.isolation`](pixfraud.models.unsupervised.isolation.md) | Modelos de **isolamento**: a conta suspeita se separa das outras com poucos cortes aleatórios. |
| [`pixfraud.models.unsupervised.isolation.isolation_forest`](pixfraud.models.unsupervised.isolation.isolation_forest.md) | Isolation Forest (Liu, Ting e Zhou, 2008): a conta isolada com poucos cortes aleatórios é anômala. |
| [`pixfraud.models.unsupervised.neural`](pixfraud.models.unsupervised.neural.md) | Redes neurais **de reconstrução**: aprendem a reconstruir as contas típicas e erram na suspeita. |
| [`pixfraud.models.unsupervised.neural.autoencoder`](pixfraud.models.unsupervised.neural.autoencoder.md) | Autoencoder: uma rede neural que aprendeu a reconstruir as contas típicas erra ao reconstruir esta. |
| [`pixfraud.models.unsupervised.neural.dominant`](pixfraud.models.unsupervised.neural.dominant.md) | DOMINANT (Ding et al., 2019): autoencoder de grafo, uma rede neural não supervisionada. |
| [`pixfraud.models.unsupervised.proximity`](pixfraud.models.unsupervised.proximity.md) | Modelos de **proximidade**: a conta suspeita está longe das outras ou numa região pouco densa. |
| [`pixfraud.models.unsupervised.proximity.dbscan`](pixfraud.models.unsupervised.proximity.dbscan.md) | DBSCAN (Ester et al., 1996): a conta fora das regiões densas é anômala. |
| [`pixfraud.models.unsupervised.proximity.kmeans`](pixfraud.models.unsupervised.proximity.kmeans.md) | k-means com a regra do CBLOF (He, Xu e Deng, 2003): a conta está longe dos grupos grandes. |
| [`pixfraud.models.unsupervised.proximity.knn`](pixfraud.models.unsupervised.proximity.knn.md) | kNN (Ramaswamy, Rastogi e Shim, 2000): a conta está longe dos seus vizinhos mais próximos. |
| [`pixfraud.models.unsupervised.proximity.local_outlier_factor`](pixfraud.models.unsupervised.proximity.local_outlier_factor.md) | Local Outlier Factor (Breunig et al., 2000): a vizinhança da conta é menos densa que a dos vizinhos. |
| [`pixfraud.models.unsupervised.statistical`](pixfraud.models.unsupervised.statistical.md) | Modelos **estatísticos**: a conta suspeita é rara segundo a distribuição dos atributos. |
| [`pixfraud.models.unsupervised.statistical.ecod`](pixfraud.models.unsupervised.statistical.ecod.md) | ECOD (Li et al., 2022): a conta está na cauda de vários atributos ao mesmo tempo. |
| [`pixfraud.models.unsupervised.statistical.pca`](pixfraud.models.unsupervised.statistical.pca.md) | PCA (Shyu et al., 2003): a conta foge da correlação entre os atributos. |
| [`pixfraud.network`](pixfraud.network.md) | Que tipo de rede é a do Pix? Lei de potência, componente gigante e passeios aleatórios. |
| [`pixfraud.online`](pixfraud.online.md) | Detecção ao longo do tempo: a conta foi sinalizada a tempo de bloquear o dinheiro? |
| [`pixfraud.patterns`](pixfraud.patterns.md) | Padrões de fraude como pequenos grafos, para estudo e para injetar em redes maiores. |
| [`pixfraud.simulation`](pixfraud.simulation.md) | Gerador de um dataset sintético de transações PIX com cenários de fraude. |
| [`pixfraud.stats`](pixfraud.stats.md) | Inferência estatística para a pesquisa. |
| [`pixfraud.temporal`](pixfraud.temporal.md) | Grafos temporais: caminhos que respeitam a ordem cronológica dos Pix. |
| [`pixfraud.tuning`](pixfraud.tuning.md) | Otimização de hiperparâmetros: busca em grade que se amplia sozinha, escolhida em redes de **validação**. |
| [`pixfraud.tuning.search`](pixfraud.tuning.search.md) | Dar nota a cada candidato numa rede de validação e escolher o vencedor. |
| [`pixfraud.tuning.search_space`](pixfraud.tuning.search_space.md) | O espaço de busca: quais valores de cada hiperparâmetro testar, e como ampliá-lo. |
| [`pixfraud.visualization`](pixfraud.visualization.md) | Visualizações dos grafos. |

## Scripts

| Pasta | O que guarda |
|---|---|
| [`scripts/ (raiz)`](scripts.raiz.md) | pontos de entrada da pesquisa, uma pasta por etapa |
| [`scripts/01_dados/`](scripts.01_dados.md) | etapa 1: gerar, importar e baixar dados, auditar o gabarito, validar o realismo |
| [`scripts/02_exploracao/`](scripts.02_exploracao.md) | etapa 2: forma da rede, inferência sobre os atributos e visualização |
| [`scripts/03_modelos/`](scripts.03_modelos.md) | etapa 3: rodada única, otimização dos hiperparâmetros e vitrine dos modelos |
| [`scripts/04_avaliacao/`](scripts.04_avaliacao.md) | etapa 4: repetições com sementes e cenários e comparações com inferência |
| [`scripts/05_interpretacao/`](scripts.05_interpretacao.md) | etapa 5: os erros dos modelos |
| [`scripts/ferramentas/`](scripts.ferramentas.md) | busca, grafo de notas, ilustrações, documentação do código e relatório |

## App e testes

- [`app/explorador.py`](app.md): o explorador interativo em Streamlit
- [Testes](testes.md): cada arquivo de teste e o que ele confere
