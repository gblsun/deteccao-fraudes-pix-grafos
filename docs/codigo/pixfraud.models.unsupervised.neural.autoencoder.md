---
tags: [codigo]
---

# `pixfraud.models.unsupervised.neural.autoencoder`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/neural/autoencoder.py`](../../src/pixfraud/models/unsupervised/neural/autoencoder.py) · [mapa do código](mapa-do-codigo.md)

Autoencoder: uma rede neural que aprendeu a reconstruir as contas típicas erra ao reconstruir esta.

## Classes e funções

### `autoencoder` (função)

```python
def autoencoder(features: pd.DataFrame, max_iter: int=300, contamination: float=0.05, bottleneck: float=1 / 3, alpha: float=0.001, seed: int=42) -> Detection
```

Autoencoder: a conta que a rede não consegue reconstruir é anômala.

Uma rede neural pequena (`MLPRegressor` do scikit-learn) aprende a
devolver a própria entrada passando por uma camada estreita, com a fração
`bottleneck` do número de atributos (padrão: um terço). Como a maioria
das contas é legítima, ela aprende o que é típico; o escore é o erro médio
de reconstrução de cada conta. `alpha` é a regularização L2 dos pesos.
Para de treinar quando o erro de validação deixa de cair.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.neural`](pixfraud.models.unsupervised.neural.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
