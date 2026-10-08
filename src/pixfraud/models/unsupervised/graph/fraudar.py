"""FRAUDAR (Hooi et al., 2016): contas em blocos densos, como uma quadrilha, ficam no topo.

Olha só para a estrutura do grafo, sem a tabela de atributos.
"""

from __future__ import annotations

import networkx as nx

from pixfraud.communities import peeling_scores
from pixfraud.models.base import Detection, detection, top_fraction


def fraudar(graph: nx.Graph, contamination: float = 0.05) -> Detection:
    """FRAUDAR como escore por conta (``communities.peeling_scores``).

    O núcleo ponderado da remoção gulosa com os pesos do FRAUDAR: contas em
    blocos densos, como uma quadrilha em que várias laranjas mandam para os
    mesmos intermediários, ficam no topo; os pesos fazem Pix para comércios
    muito procurados valerem pouco, e assim "pagar a padaria" não camufla a
    quadrilha. O rótulo binário marca a fração ``contamination`` de maior
    escore. Não usa valores nem horários, só quem pagou quem.
    """
    scores = peeling_scores(graph, fraudar=True)
    return detection(scores.to_numpy(), top_fraction(scores.to_numpy(), contamination), scores.index)
