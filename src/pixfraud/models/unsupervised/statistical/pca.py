"""PCA (Shyu et al., 2003): a conta foge da correlação entre os atributos."""

from __future__ import annotations

import pandas as pd
from sklearn.decomposition import PCA

from pixfraud.models.base import Detection, detection, prepare_matrix, top_fraction


def pca(
    features: pd.DataFrame,
    components: str = "all",
    weighted: bool = True,
    contamination: float = 0.05,
    tol: float = 1e-9,
) -> Detection:
    """PCA: soma das projeções da conta nas componentes principais, divididas pela variância delas.

    As componentes principais resumem como os atributos variam juntos (quem
    recebe de muitas contas também costuma receber mais dinheiro, por exemplo).
    O escore soma o quadrado da projeção da conta em cada componente
    (Shyu et al., 2003). As componentes maiores pegam a conta extrema na
    direção comum; as menores, de variância quase nula, pegam a conta que
    quebra a correlação, um desvio que nenhum atributo sozinho mostraria.

    ``components``: ``"all"`` (todas), ``"major"`` (as que somam 90% da
    variância) ou ``"minor"`` (as demais). ``weighted=True`` divide cada
    projeção pela variância da componente, o que dá peso grande às menores;
    com ``False``, a soma é só a distância ao centro. Componentes de variância
    abaixo de ``tol`` (atributos constantes) ficam de fora. O rótulo binário
    marca a fração ``contamination`` de maior escore.
    """
    if components not in ("all", "major", "minor"):
        raise ValueError(f"components deve ser 'all', 'major' ou 'minor', não {components!r}")
    X = prepare_matrix(features)
    model = PCA().fit(X)
    variance = model.explained_variance_
    keep = variance > tol
    if components != "all" and keep.sum() > 1:
        major = (model.explained_variance_ratio_.cumsum() - model.explained_variance_ratio_) < 0.9
        keep &= major if components == "major" else ~major
        if not keep.any():  # com poucos atributos, uma das partes pode ficar vazia
            keep = variance > tol
    projections = model.transform(X)[:, keep] ** 2
    scores = (projections / variance[keep] if weighted else projections).sum(axis=1)
    return detection(scores, top_fraction(scores, contamination), features.index)
