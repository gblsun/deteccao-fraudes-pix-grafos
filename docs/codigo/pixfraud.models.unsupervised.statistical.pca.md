---
tags: [codigo]
---

# `pixfraud.models.unsupervised.statistical.pca`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/models/unsupervised/statistical/pca.py`](../../src/pixfraud/models/unsupervised/statistical/pca.py) · [mapa do código](mapa-do-codigo.md)

PCA (Shyu et al., 2003): a conta foge da correlação entre os atributos.

## Classes e funções

### `pca` (função)

```python
def pca(features: pd.DataFrame, components: str='all', weighted: bool=True, contamination: float=0.05, tol: float=1e-09) -> Detection
```

PCA: soma das projeções da conta nas componentes principais, divididas pela variância delas.

As componentes principais resumem como os atributos variam juntos (quem
recebe de muitas contas também costuma receber mais dinheiro, por exemplo).
O escore soma o quadrado da projeção da conta em cada componente
(Shyu et al., 2003). As componentes maiores pegam a conta extrema na
direção comum; as menores, de variância quase nula, pegam a conta que
quebra a correlação, um desvio que nenhum atributo sozinho mostraria.

`components`: `"all"` (todas), `"major"` (as que somam 90% da
variância) ou `"minor"` (as demais). `weighted=True` divide cada
projeção pela variância da componente, o que dá peso grande às menores;
com `False`, a soma é só a distância ao centro. Componentes de variância
abaixo de `tol` (atributos constantes) ficam de fora. O rótulo binário
marca a fração `contamination` de maior escore.

## Quem usa este módulo

- [`pixfraud.models.unsupervised.statistical`](pixfraud.models.unsupervised.statistical.md)
- [`pixfraud.models.unsupervised`](pixfraud.models.unsupervised.md)
