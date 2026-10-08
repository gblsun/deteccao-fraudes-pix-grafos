"""Modelos supervisionados de **árvores de decisão**, sobre a tabela de atributos.

* ``random_forest``: muitas árvores independentes votam;
* ``gradient_boosting``: árvores em sequência, cada uma corrigindo a anterior.
"""

from pixfraud.models.supervised.trees.gradient_boosting import gradient_boosting_scores, make_gradient_boosting
from pixfraud.models.supervised.trees.random_forest import (
    make_random_forest,
    random_forest_known_fraud_scores,
    random_forest_scores,
)

__all__ = [
    "gradient_boosting_scores", "make_gradient_boosting", "make_random_forest", "random_forest_known_fraud_scores",
    "random_forest_scores",
]
