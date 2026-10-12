"""GraphSAGE direcionada, com PyTorch Geometric: uma convolução para quem pagou a conta e outra para quem recebeu.

Supervisionada, com parada antecipada pela average precision. É a usada por
``avaliar_atributos.py`` e ``avaliar_modelos.py``; precisa do
``torch_geometric`` (``torch_utils.available()`` diz se ele está instalado).
``graphsage.sage_supervised_scores`` e esta são duas implementações do mesmo
teto, feitas em paralelo (a primeira sustenta as seções 10 e 11 de
``docs/resultados.md``); a comparação entre elas ainda não foi feita.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from pixfraud.models.base import prepare_matrix


def graphsage_scores(
    graph: nx.DiGraph,
    features: pd.DataFrame,
    labels: pd.Series,
    seed: int = 42,
    folds: int = 5,
    hidden: int = 64,
    epochs: int = 200,
    learning_rate: float = 0.01,
    dropout: float = 0.3,
    patience: int = 20,
) -> pd.Series:
    """Probabilidade de fraude de cada conta dada por uma GraphSAGE treinada com os rótulos.

    Validação cruzada **transdutiva** de ``folds`` partes: a rede vê o grafo
    inteiro (quem pagou quem é conhecido também para as contas de teste), mas
    a perda só usa os rótulos das contas de treino, e cada conta recebe a
    previsão do modelo que não viu o rótulo dela. A perda pesa as fraudes pela
    raridade, e o treino para quando a average precision numa parte separada
    do treino deixa de melhorar por ``patience`` épocas.

    Os atributos de cada conta passam pela mesma preparação dos detectores
    (log1p e padronização). O grafo é direcionado: em cada camada, uma
    convolução junta quem pagou a conta e outra, quem recebeu dela.
    """
    import torch

    nodes = list(features.index)
    position = {v: i for i, v in enumerate(nodes)}
    x = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    pairs = [(position[u], position[v]) for u, v in graph.edges() if u != v and u in position and v in position]
    edges = torch.tensor(pairs, dtype=torch.long).t() if pairs else torch.empty((2, 0), dtype=torch.long)
    reverse = edges.flip(0)
    y = labels.reindex(nodes).astype(bool).to_numpy()
    target = torch.tensor(y, dtype=torch.float32)

    scores = np.zeros(len(nodes))
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (train, test) in enumerate(splitter.split(np.zeros(len(y)), y)):
        torch.manual_seed(seed * 100 + fold)
        if y[train].sum() >= 4:  # validação separada do treino, para a parada antecipada
            fit, check = train_test_split(train, test_size=0.2, stratify=y[train], random_state=seed + fold)
        else:
            fit, check = train, None
        model = directed_sage(x.shape[1], hidden, dropout)
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=5e-4)
        positives = max(float(y[fit].sum()), 1.0)
        loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor((len(fit) - positives) / positives))
        fit_t = torch.tensor(fit)
        best, best_state, waited = -1.0, None, 0
        for _ in range(epochs):
            model.train()
            optimizer.zero_grad()
            loss = loss_fn(model(x, edges, reverse)[fit_t], target[fit_t])
            loss.backward()
            optimizer.step()
            if check is None:
                continue
            model.eval()
            with torch.no_grad():
                logits = model(x, edges, reverse)[torch.tensor(check)].numpy()
            ap = average_precision_score(y[check], logits) if y[check].any() else 0.0
            if ap > best:
                best, best_state, waited = ap, {k: v.clone() for k, v in model.state_dict().items()}, 0
            else:
                waited += 1
                if waited >= patience:
                    break
        if best_state is not None:
            model.load_state_dict(best_state)
        model.eval()
        with torch.no_grad():
            scores[test] = torch.sigmoid(model(x, edges, reverse)[torch.tensor(test)]).numpy()
    return pd.Series(scores, index=nodes, name="score")


def directed_sage(in_dim: int, hidden: int, dropout: float):
    """GraphSAGE de 2 camadas com uma convolução para cada sentido do Pix."""
    import torch
    from torch_geometric.nn import SAGEConv

    class DirectedSAGE(torch.nn.Module):
        """GraphSAGE direcionada: agrega separado quem pagou a conta e a quem ela pagou."""
        def __init__(self):
            """Duas camadas para cada sentido do dinheiro e a saída de um escore por conta."""
            super().__init__()
            self.paid_by = torch.nn.ModuleList([SAGEConv(in_dim, hidden), SAGEConv(hidden, hidden)])
            self.paid_to = torch.nn.ModuleList([SAGEConv(in_dim, hidden), SAGEConv(hidden, hidden)])
            self.head = torch.nn.Linear(hidden, 1)

        def forward(self, x, edges, reverse):
            """Escore de cada conta somando as mensagens de entrada e de saída a cada camada."""
            h = x
            for incoming, outgoing in zip(self.paid_by, self.paid_to):
                h = torch.relu(incoming(h, edges) + outgoing(h, reverse))
                h = torch.nn.functional.dropout(h, p=dropout, training=self.training)
            return self.head(h).squeeze(-1)

    return DirectedSAGE()
