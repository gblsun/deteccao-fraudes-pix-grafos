"""DOMINANT (Ding et al., 2019): autoencoder de grafo, uma rede neural não supervisionada.

Um codificador GCN comprime cada conta; um decodificador reconstrói os
atributos e outro reconstrói as ligações. A conta que a rede não consegue
reconstruir, nos atributos ou em quem ela conhece, é anômala. Precisa do
``torch`` (extra ``gnn``).
"""

from __future__ import annotations

import networkx as nx
import pandas as pd

from pixfraud.models import torch_utils
from pixfraud.models.base import prepare_matrix


def dominant_scores(
    graph: nx.Graph,
    features: pd.DataFrame,
    hidden: int = 64,
    latent: int = 32,
    epochs: int = 300,
    alpha: float = 0.5,
    learning_rate: float = 5e-3,
    seed: int = 42,
    max_nodes: int = 20_000,
) -> pd.Series:
    """Escore de anomalia do DOMINANT: erro de reconstrução dos atributos e das ligações.

    O escore é ``alpha`` × erro dos atributos + (1 - ``alpha``) × erro da
    estrutura, com os dois erros divididos pela própria média para ficarem na
    mesma escala. A reconstrução da estrutura compara a linha inteira da
    adjacência, o que custa memória proporcional ao **quadrado** do nº de
    contas; acima de ``max_nodes`` contas, a função recusa em vez de travar a
    máquina.
    """
    torch_utils.require_torch()
    torch, nn = torch_utils.torch, torch_utils.nn
    n = len(features)
    if n > max_nodes:
        raise ValueError(f"{n} contas: acima de max_nodes={max_nodes}, a matriz densa de adjacência não cabe")
    torch.manual_seed(seed)
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    gcn, _ = torch_utils.adjacency(graph, features.index)
    A = (gcn.to_dense() > 0).float() - torch.eye(n)  # adjacência 0/1 sem laços, alvo da reconstrução

    encoder = nn.ModuleList([nn.Linear(X.shape[1], hidden), nn.Linear(hidden, latent)])
    attribute_decoder = nn.ModuleList([nn.Linear(latent, hidden), nn.Linear(hidden, X.shape[1])])
    structure_decoder = nn.Linear(latent, latent)
    parameters = [*encoder.parameters(), *attribute_decoder.parameters(), *structure_decoder.parameters()]
    optimizer = torch.optim.Adam(parameters, lr=learning_rate)

    def forward():
        """Reconstrói atributos e ligações e devolve o erro de cada conta (o escore do DOMINANT)."""
        h = torch.relu(torch.sparse.mm(gcn, encoder[0](X)))
        z = torch.relu(torch.sparse.mm(gcn, encoder[1](h)))
        x_hat = torch.sparse.mm(gcn, attribute_decoder[1](torch.relu(torch.sparse.mm(gcn, attribute_decoder[0](z)))))
        s = torch.relu(torch.sparse.mm(gcn, structure_decoder(z)))
        a_hat = torch.sigmoid(s @ s.T)
        attribute_error = ((X - x_hat) ** 2).sum(dim=1).sqrt()
        structure_error = ((A - a_hat) ** 2).sum(dim=1).sqrt()
        return attribute_error, structure_error

    for _ in range(epochs):
        optimizer.zero_grad()
        attribute_error, structure_error = forward()
        loss = alpha * attribute_error.mean() + (1 - alpha) * structure_error.mean()
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        attribute_error, structure_error = forward()
        score = (alpha * attribute_error / attribute_error.mean().clamp_min(1e-12)
                 + (1 - alpha) * structure_error / structure_error.mean().clamp_min(1e-12))
    return pd.Series(score.numpy().astype(float), index=features.index, name="score")
