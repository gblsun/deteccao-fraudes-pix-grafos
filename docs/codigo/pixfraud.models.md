---
tags: [codigo]
---

# `pixfraud.models`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/__init__.py`](../../src/pixfraud/models/__init__.py) · [mapa do código](mapa-do-codigo.md)

Todos os modelos de detecção, um arquivo por modelo, agrupados por tipo e por família.

:

    models/
      base.py                  Detection, prepare_matrix: o que todos compartilham
      torch_utils.py           o que as redes neurais para grafos compartilham (torch opcional)
      unsupervised/            não veem o gabarito: procuram o que destoa
        proximity/             knn, dbscan, local_outlier_factor, kmeans
        statistical/           pca, ecod
        isolation/             isolation_forest
        boundary/              one_class_svm
        neural/                autoencoder, dominant (torch)
        graph/                 fraudar, node2vec
      semi_supervised/         usam só as poucas fraudes já conhecidas
        personalized_pagerank.py, label_spreading.py
      supervised/              aprendem com o gabarito, em validação cruzada
        cross_validation.py
        trees/                 random_forest, gradient_boosting
        neural/                graphsage, graphsage_directed (torch)

Os registros `DETECTORS`, `GRAPH_DETECTORS` e `SUPERVISED` ligam o nome
de cada modelo (o mesmo de `configs/experimento.yaml`) à função. Os módulos
antigos `pixfraud.anomaly`, `pixfraud.graph_models` e `pixfraud.gnn` (e
as funções de propagação em `pixfraud.flow`) continuam funcionando: só
reexportam o que está aqui.

## Quem usa este módulo

- [`pixfraud.evaluation`](pixfraud.evaluation.md)
- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`pixfraud.models.supervised.neural.graphsage`](pixfraud.models.supervised.neural.graphsage.md)
- [`pixfraud.models.unsupervised.neural.dominant`](pixfraud.models.unsupervised.neural.dominant.md)
- [`pixfraud.online`](pixfraud.online.md)
- [`pixfraud.tuning.search_space`](pixfraud.tuning.search_space.md)
- [`pixfraud.tuning.search`](pixfraud.tuning.search.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`tests/test_tuning.py`](testes.md)
