---
tags: [codigo]
---

# `pixfraud.models.unsupervised`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/__init__.py`](../../src/pixfraud/models/unsupervised/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos **não supervisionados**: não veem o gabarito, procuram as contas que destoam das outras.

Organizados por família, cada uma num subpacote:

* `proximity/`: `knn`, `dbscan`, `local_outlier_factor` e `kmeans`
  (a conta está longe das outras ou numa região pouco densa);
* `statistical/`: `pca` e `ecod` (a conta é rara pela distribuição dos atributos);
* `isolation/`: `isolation_forest` (poucos cortes aleatórios isolam a conta);
* `boundary/`: `one_class_svm` (a conta fica fora da fronteira das normais);
* `neural/`: `autoencoder` e `dominant` (a rede erra ao reconstruir a conta);
* `graph/`: `fraudar` e `node2vec` (só a estrutura do grafo).

Dois registros, com a mesma saída (`base.Detection`):

* `DETECTORS`: recebem a tabela de atributos das contas, sempre preparada por
  `base.prepare_matrix` (log1p e padronização);
* `GRAPH_DETECTORS`: recebem o grafo.

Fora dos registros, por precisar do `torch` e devolver só o escore:
`neural.dominant_scores`.

## Quem usa este módulo

- [`pixfraud.anomaly`](pixfraud.anomaly.md)
- [`pixfraud.graph_models`](pixfraud.graph_models.md)
- [`pixfraud.models`](pixfraud.models.md)
