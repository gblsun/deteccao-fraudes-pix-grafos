---
tags: [codigo]
---

# `pixfraud.models.unsupervised.statistical.ecod`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/statistical/ecod.py`](../../src/pixfraud/models/unsupervised/statistical/ecod.py) · [mapa do código](mapa-do-codigo.md)

ECOD (Li et al., 2022): a conta está na cauda de vários atributos ao mesmo tempo.

## Classes e funções

### `ecod` (função)

```python
def ecod(features: pd.DataFrame, contamination: float=0.05) -> Detection
```

ECOD: probabilidade de cauda empírica, atributo por atributo (Li et al., 2022).

Para cada atributo, a função de distribuição empírica diz quão rara é a
conta pela esquerda e pela direita; o escore soma `-log` dessas
probabilidades em todos os atributos. Faz isso três vezes (cauda esquerda,
direita e a indicada pela assimetria de cada atributo) e fica com a maior.
Não tem parâmetro para ajustar e é muito rápido, mas ignora a relação entre
atributos: uma conta comum em cada atributo e rara na combinação passa.
O rótulo binário marca a fração `contamination` de maior escore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.statistical`](pixfraud.models.unsupervised.statistical.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
