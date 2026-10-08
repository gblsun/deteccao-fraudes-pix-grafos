"""Modelos **supervisionados**: aprendem com o gabarito (quem é fraude), sempre em validação cruzada.

Cada conta recebe a probabilidade dada por um modelo que **não viu o rótulo
dela** (``cross_validation.out_of_fold_scores``). Na pesquisa eles são um
teto: mostram até onde se chegaria se as respostas fossem conhecidas, o que
no Pix real quase nunca acontece.

* ``trees/``: ``random_forest`` e ``gradient_boosting``, sobre a tabela de atributos;
* ``neural/``: ``graphsage`` e ``graphsage_directed``, redes neurais para grafos
  (precisam do ``torch``).

``SUPERVISED`` registra os de árvores, todos com a assinatura
``(features, labels, seed=42, folds=5, **hiperparâmetros) -> pd.Series``.
"""

from pixfraud.models.supervised.trees import (
    gradient_boosting_scores,
    make_gradient_boosting,
    make_random_forest,
    random_forest_known_fraud_scores,
    random_forest_scores,
)

SUPERVISED = {
    "random_forest": random_forest_scores,
    "gradient_boosting": gradient_boosting_scores,
}

# Fábrica do classificador de cada modelo: onde ficam os valores padrão dos hiperparâmetros.
FACTORIES = {
    "random_forest": make_random_forest,
    "gradient_boosting": make_gradient_boosting,
}

__all__ = [
    "FACTORIES", "SUPERVISED", "gradient_boosting_scores", "make_gradient_boosting", "make_random_forest",
    "random_forest_known_fraud_scores", "random_forest_scores",
]
