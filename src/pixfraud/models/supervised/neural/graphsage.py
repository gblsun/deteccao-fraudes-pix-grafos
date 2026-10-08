"""GraphSAGE (Hamilton, Ying e Leskovec, 2017), implementação própria: rede neural para grafos supervisionada.

Cada conta mistura os seus atributos com a média dos vizinhos, em duas
camadas, e a rede aprende o que combinar. Escrita sem PyTorch Geometric: o
grafo do Pix sintético cabe numa matriz esparsa. Precisa do ``torch`` (extra
``gnn``). Duas formas de usar:

* ``sage_supervised_scores``: treinada com os rótulos, em validação cruzada
  (um teto, como o Random Forest);
* ``sage_known_fraud_scores``: só com uma parte das fraudes conhecida e o
  resto das contas sem rótulo, como na culpa por associação.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold

from pixfraud.models import torch_utils
from pixfraud.models.base import prepare_matrix
from pixfraud.models.torch_utils import nn, torch


# Sem torch o módulo ainda importa (para os scripts que pulam a GNN); a classe
# só é usada depois de ``require_torch()``.
class GraphSAGE(nn.Module if nn is not None else object):
    """Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos vizinhos]."""

    def __init__(self, n_features: int, hidden: int, dropout: float):
        super().__init__()
        self.layer1 = nn.Linear(2 * n_features, hidden)
        self.layer2 = nn.Linear(2 * hidden, hidden)
        self.out = nn.Linear(hidden, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, X, mean):
        h = torch.relu(self.layer1(torch.cat([X, torch.sparse.mm(mean, X)], dim=1)))
        h = self.dropout(h)
        h = torch.relu(self.layer2(torch.cat([h, torch.sparse.mm(mean, h)], dim=1)))
        return self.out(self.dropout(h)).squeeze(1)


def sage_supervised_scores(
    graph: nx.Graph,
    features: pd.DataFrame,
    labels: pd.Series,
    folds: int = 5,
    hidden: int = 64,
    epochs: int = 200,
    dropout: float = 0.3,
    learning_rate: float = 1e-2,
    seed: int = 42,
) -> pd.Series:
    """Probabilidade de fraude fora da amostra, por uma GraphSAGE em validação cruzada.

    Transdutivo, como é comum em GNN: o grafo inteiro (e os atributos de todas
    as contas) é visto no treino, mas a perda usa só os rótulos das contas de
    treino da dobra, e cada conta recebe a previsão do modelo em que ela ficou
    de fora. As fraudes, raras, pesam mais na perda (``pos_weight``).
    """
    torch_utils.require_torch()
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    _, mean = torch_utils.adjacency(graph, features.index)
    y_np = labels.reindex(features.index).astype(bool).to_numpy()
    proba = np.zeros(len(features))
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (train, test) in enumerate(splitter.split(np.zeros(len(y_np)), y_np)):
        proba[test] = fit_sage(X, mean, y_np, train, hidden, epochs, dropout, learning_rate, seed + fold)[test]
    return pd.Series(proba, index=features.index, name="score")


def sage_known_fraud_scores(
    graph: nx.Graph,
    features: pd.DataFrame,
    known: list,
    folds: int = 5,
    hidden: int = 64,
    epochs: int = 200,
    dropout: float = 0.3,
    learning_rate: float = 1e-2,
    seed: int = 42,
) -> pd.Series:
    """GraphSAGE treinada só com as fraudes **já conhecidas**, como no Pix real.

    Numa instituição, só parte das contas fraudulentas vira conhecida (quando as
    vítimas contestam pelo MED); todas as outras aparecem como "não fraude",
    inclusive as fraudes ainda não descobertas. É um problema *positivo e não
    rotulado* (PU): aqui tratado do jeito mais simples, com as contas não
    rotuladas como negativas.

    Para a rede não decorar o "não fraude" das próprias contas que vai avaliar,
    as contas não rotuladas são divididas em ``folds`` dobras: cada dobra recebe
    a previsão de um modelo treinado com as fraudes conhecidas e as **outras**
    dobras. As contas de ``known`` recebem 1.0; avalie só nas demais.
    """
    torch_utils.require_torch()
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    _, mean = torch_utils.adjacency(graph, features.index)
    y_np = features.index.isin(known)
    positives, unlabeled = np.flatnonzero(y_np), np.flatnonzero(~y_np)
    proba = np.ones(len(features))
    splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (rest, held_out) in enumerate(splitter.split(unlabeled)):
        train = np.concatenate([positives, unlabeled[rest]])
        test = unlabeled[held_out]
        proba[test] = fit_sage(X, mean, y_np, train, hidden, epochs, dropout, learning_rate, seed + fold)[test]
    return pd.Series(proba, index=features.index, name="score")


def fit_sage(X, mean, y_np: np.ndarray, train: np.ndarray, hidden: int, epochs: int, dropout: float,
             learning_rate: float, seed: int) -> np.ndarray:
    """Treina uma GraphSAGE com os rótulos de ``train`` e devolve a probabilidade de todas as contas.

    As fraudes, raras, pesam mais na perda (``pos_weight``).
    """
    torch.manual_seed(seed)
    y = torch.tensor(y_np, dtype=torch.float32)
    model = GraphSAGE(X.shape[1], hidden, dropout)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=5e-4)
    positives = max(float(y_np[train].sum()), 1.0)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor((len(train) - positives) / positives))
    train_idx = torch.tensor(train)
    for _ in range(epochs):
        model.train()
        optimizer.zero_grad()
        loss = loss_fn(model(X, mean)[train_idx], y[train_idx])
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        return torch.sigmoid(model(X, mean)).numpy()
