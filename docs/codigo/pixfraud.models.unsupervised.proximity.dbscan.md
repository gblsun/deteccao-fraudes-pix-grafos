---
tags: [codigo]
---

# `pixfraud.models.unsupervised.proximity.dbscan`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/proximity/dbscan.py`](../../src/pixfraud/models/unsupervised/proximity/dbscan.py) · [mapa do código](mapa-do-codigo.md)

DBSCAN (Ester et al., 1996): a conta fora das regiões densas é anômala.

## Classes e funções

### `dbscan` (função)

```python
def dbscan(features: pd.DataFrame, eps: float | str='auto', min_samples: int=10, eps_quantile: float=0.95, max_exact: int=20000) -> Detection
```

DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.

Como o DBSCAN não produz um escore contínuo, usamos como escore a distância
ao `min_samples`-ésimo vizinho mais próximo (k-distance): um ponto é
núcleo de cluster exatamente quando essa distância é <= `eps`. Com
`eps="auto"`, `eps` é o quantil `eps_quantile` dessas distâncias.
Isso é só uma heurística; o ideal é escolher `eps` pelo gráfico de
k-distance (ver notebook de análise exploratória).

`max_exact`: acima desse número de contas, o rótulo binário deixa de sair
do DBSCAN e passa a ser "não é ponto de núcleo" (k-distance > `eps`). O
motivo é memória: o DBSCAN guarda a vizinhança de **cada** ponto e, com
`eps` no quantil 0,95, cada conta tem ~20% das contas como vizinhas, o
que cresce com o quadrado do número de contas (7 MB com 2 mil contas,
~16 GB com 100 mil). Os escores não mudam, então average precision e
precision@k são idênticas; muda só o rótulo binário, que passa a incluir os
pontos de borda (97,6% de concordância no dataset sintético).

## Quem usa este módulo

- [`pixfraud.models.unsupervised.proximity`](pixfraud.models.unsupervised.proximity.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
