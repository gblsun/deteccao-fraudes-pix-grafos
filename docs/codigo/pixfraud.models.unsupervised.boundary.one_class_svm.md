---
tags: [codigo]
---

# `pixfraud.models.unsupervised.boundary.one_class_svm`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/boundary/one_class_svm.py`](../../src/pixfraud/models/unsupervised/boundary/one_class_svm.py) · [mapa do código](mapa-do-codigo.md)

One-Class SVM (Schölkopf et al., 2001): uma fronteira que envolve a maior parte das contas.

## Classes e funções

### `one_class_svm` (função)

```python
def one_class_svm(features: pd.DataFrame, nu: float=0.05, gamma: float | str='scale', max_exact: int=5000, n_components: int=300, seed: int=42) -> Detection
```

One-Class SVM: uma fronteira (núcleo RBF) que envolve a maior parte das contas.

`nu` é, aproximadamente, a fração de contas deixadas do lado de fora
(anômalas). O SVM exato custa entre o quadrado e o cubo do número de
contas; acima de `max_exact`, o núcleo é aproximado (Nyström, com
`n_components` pontos) e o SVM é treinado por gradiente estocástico,
com custo linear. O escore é a distância para dentro da fronteira, com o
sinal trocado: quanto maior, mais para fora.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.boundary`](pixfraud.models.unsupervised.boundary.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
