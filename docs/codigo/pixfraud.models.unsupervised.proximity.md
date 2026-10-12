---
tags: [codigo]
---

# `pixfraud.models.unsupervised.proximity`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/proximity/__init__.py`](../../src/pixfraud/models/unsupervised/proximity/__init__.py) · [mapa do código](mapa-do-codigo.md)

Modelos de **proximidade**: a conta suspeita está longe das outras ou numa região pouco densa.

Todos medem distâncias entre contas no espaço dos atributos; muda a régua.

* `knn`: distância aos `k` vizinhos mais próximos;
* `dbscan`: fora das regiões densas, com um raio único para todos;
* `local_outlier_factor`: densidade da conta comparada com a dos vizinhos;
* `kmeans`: distância ao centro do grupo grande de perfis mais próximo.

## Quem usa este módulo

- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
