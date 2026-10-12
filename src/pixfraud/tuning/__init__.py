"""Otimização de hiperparâmetros: busca em grade que se amplia sozinha, escolhida em redes de **validação**.

O gabarito é usado para dar nota a cada combinação de hiperparâmetros, então a
escolha não pode ser feita nas mesmas redes em que os modelos são avaliados
depois: a nota sairia inflada, como estudar com a prova que vai cair. Por
isso ``scripts/03_modelos/otimizar_hiperparametros.py`` gera redes com sementes próprias
(a partir de ``VALIDATION_SEED``), escolhe os hiperparâmetros nelas e grava a
configuração; os estudos de avaliação usam as sementes 1, 2, 3..., que nunca
entram na escolha.

* ``search_space``: as grades (de ``configs/busca_hiperparametros.yaml``) e a
  ampliação de uma grade quando o vencedor cai na ponta;
* ``search``: a nota (average precision) de cada candidato e a escolha do vencedor.

A busca roda em rodadas: na primeira, a grade inteira; nas seguintes, só os
valores novos dos modelos cujo vencedor caiu na ponta da lista. Termina quando
nenhum vencedor está numa ponta que ainda possa crescer.
"""

from pixfraud.tuning.search import average_precision, choose, chosen_params, model_scores, score_candidates
from pixfraud.tuning.search_space import (
    DEFAULT_PATH,
    Param,
    candidates,
    expand,
    full_params,
    grid,
    load_search_spaces,
    model_function,
    params_key,
)

VALIDATION_SEED = 1001  # primeira semente das redes de validação: longe das sementes 1, 2, 3... dos estudos

__all__ = [
    "DEFAULT_PATH", "VALIDATION_SEED", "Param", "average_precision", "candidates", "choose", "chosen_params",
    "expand", "full_params", "grid", "load_search_spaces", "model_function", "model_scores", "params_key",
    "score_candidates",
]
