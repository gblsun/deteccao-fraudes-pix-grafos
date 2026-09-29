"""Redes neurais para grafos (GNN) aplicadas às contas, com PyTorch.

Depende do ``torch``, que é opcional: ``pip install -e ".[gnn]"`` (a versão só
para CPU basta: ``--index-url https://download.pytorch.org/whl/cpu``). As
camadas são escritas aqui mesmo, sem PyTorch Geometric: o grafo do Pix
sintético cabe numa matriz esparsa, e duas camadas são poucas linhas.

Uma GNN aprende a representação de cada conta misturando os atributos dela com
os dos vizinhos (*message passing*): em vez de a gente calcular grau, PageRank
ou intermediação à mão, a rede decide o que combinar. Duas formas de usar:

* ``dominant_scores`` (**não supervisionado**, como os detectores de
  ``pixfraud.anomaly``): um autoencoder de grafo, o DOMINANT (Ding et al.,
  2019). Um codificador GCN comprime cada conta; um decodificador reconstrói os
  atributos e outro reconstrói as ligações. A conta que a rede não consegue
  reconstruir, nos atributos ou em quem ela conhece, é anômala.
* ``sage_supervised_scores`` (**supervisionado**, um teto como o Random Forest de
  ``pixfraud.experiment.supervised_scores``): uma GraphSAGE (Hamilton, Ying e
  Leskovec, 2017) treinada com os rótulos, em validação cruzada. Mostra o que se
  ganharia com rótulos e com a estrutura aprendida.
* ``sage_known_fraud_scores`` (**poucos rótulos**): a mesma GraphSAGE, mas só
  com uma parte das fraudes conhecida e o resto das contas sem rótulo, como na
  culpa por associação (``pixfraud.flow.propagate_risk``).

* ``graphsage_scores`` (**supervisionado**, variante **direcionada**): GraphSAGE
  com uma convolução para quem pagou a conta e outra para quem recebeu dela,
  feita com o PyTorch Geometric e com parada antecipada pela average precision.
  É a usada por ``avaliar_atributos.py`` e ``avaliar_modelos.py``; precisa do
  ``torch_geometric`` (``available()`` diz se ele está instalado).

Todos devolvem um escore por conta (quanto maior, mais suspeita), alinhado
com o índice de ``features``. ``sage_supervised_scores`` e ``graphsage_scores``
são duas implementações do mesmo teto, feitas em paralelo (a primeira sustenta as
seções 10 e 11 de ``docs/resultados.md``); a comparação entre elas ainda não foi
feita.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split

from pixfraud.anomaly import prepare_matrix
from pixfraud.communities import undirected_simple

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover - depende do ambiente
    torch = None


def _require_torch() -> None:
    if torch is None:
        raise ImportError('o módulo pixfraud.gnn precisa do torch: pip install -e ".[gnn]"')


def _adjacency(graph: nx.Graph, index: pd.Index) -> tuple[torch.Tensor, torch.Tensor]:
    """Matrizes esparsas do grafo não direcionado, na ordem de ``index``.

    Devolve a adjacência normalizada da GCN, $\\hat A = D^{-1/2}(A + I)D^{-1/2}$,
    e a média dos vizinhos da GraphSAGE, $D^{-1}A$ (linha zerada para conta sem
    vizinhos).
    """
    simple = undirected_simple(graph)
    position = {v: i for i, v in enumerate(index)}
    edges = np.array([(position[u], position[v]) for u, v in simple.edges() if u in position and v in position],
                     dtype=np.int64).reshape(-1, 2)
    n = len(index)
    rows = np.concatenate([edges[:, 0], edges[:, 1]])
    cols = np.concatenate([edges[:, 1], edges[:, 0]])
    degree = np.bincount(rows, minlength=n).astype(np.float32)

    self_loops = np.arange(n)
    gcn_rows, gcn_cols = np.concatenate([rows, self_loops]), np.concatenate([cols, self_loops])
    inv_sqrt = 1.0 / np.sqrt(degree + 1.0)
    gcn_values = inv_sqrt[gcn_rows] * inv_sqrt[gcn_cols]
    gcn = torch.sparse_coo_tensor(np.vstack([gcn_rows, gcn_cols]), gcn_values.astype(np.float32), (n, n),
                                  check_invariants=False)

    mean_values = 1.0 / np.maximum(degree[rows], 1.0)
    mean = torch.sparse_coo_tensor(np.vstack([rows, cols]), mean_values.astype(np.float32), (n, n),
                                   check_invariants=False)
    return gcn.coalesce(), mean.coalesce()


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
    _require_torch()
    n = len(features)
    if n > max_nodes:
        raise ValueError(f"{n} contas: acima de max_nodes={max_nodes}, a matriz densa de adjacência não cabe")
    torch.manual_seed(seed)
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    gcn, _ = _adjacency(graph, features.index)
    A = (gcn.to_dense() > 0).float() - torch.eye(n)  # adjacência 0/1 sem laços, alvo da reconstrução

    encoder = nn.ModuleList([nn.Linear(X.shape[1], hidden), nn.Linear(hidden, latent)])
    attribute_decoder = nn.ModuleList([nn.Linear(latent, hidden), nn.Linear(hidden, X.shape[1])])
    structure_decoder = nn.Linear(latent, latent)
    parameters = [*encoder.parameters(), *attribute_decoder.parameters(), *structure_decoder.parameters()]
    optimizer = torch.optim.Adam(parameters, lr=learning_rate)

    def forward():
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


class _GraphSAGE(nn.Module):
    """Duas camadas GraphSAGE com agregação pela média: [própria conta ‖ média dos vizinhos]."""

    def __init__(self, n_features: int, hidden: int, dropout: float):
        super().__init__()
        self.layer1 = nn.Linear(2 * n_features, hidden)
        self.layer2 = nn.Linear(2 * hidden, hidden)
        self.out = nn.Linear(hidden, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, X: torch.Tensor, mean: torch.Tensor) -> torch.Tensor:
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
    _require_torch()
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    _, mean = _adjacency(graph, features.index)
    y_np = labels.reindex(features.index).astype(bool).to_numpy()
    proba = np.zeros(len(features))
    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (train, test) in enumerate(splitter.split(np.zeros(len(y_np)), y_np)):
        proba[test] = _fit_sage(X, mean, y_np, train, hidden, epochs, dropout, learning_rate, seed + fold)[test]
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
    _require_torch()
    X = torch.tensor(prepare_matrix(features), dtype=torch.float32)
    _, mean = _adjacency(graph, features.index)
    y_np = features.index.isin(known)
    positives, unlabeled = np.flatnonzero(y_np), np.flatnonzero(~y_np)
    proba = np.ones(len(features))
    splitter = KFold(n_splits=folds, shuffle=True, random_state=seed)
    for fold, (rest, held_out) in enumerate(splitter.split(unlabeled)):
        train = np.concatenate([positives, unlabeled[rest]])
        test = unlabeled[held_out]
        proba[test] = _fit_sage(X, mean, y_np, train, hidden, epochs, dropout, learning_rate, seed + fold)[test]
    return pd.Series(proba, index=features.index, name="score")


def _fit_sage(X, mean, y_np: np.ndarray, train: np.ndarray, hidden: int, epochs: int, dropout: float,
              learning_rate: float, seed: int) -> np.ndarray:
    """Treina uma GraphSAGE com os rótulos de ``train`` e devolve a probabilidade de todas as contas.

    As fraudes, raras, pesam mais na perda (``pos_weight``).
    """
    torch.manual_seed(seed)
    y = torch.tensor(y_np, dtype=torch.float32)
    model = _GraphSAGE(X.shape[1], hidden, dropout)
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


# --- GraphSAGE direcionada (PyTorch Geometric) -----------------------------------


def available() -> bool:
    """O PyTorch e o PyTorch Geometric estão instalados?"""
    try:
        import torch  # noqa: F401
        import torch_geometric  # noqa: F401
    except ImportError:
        return False
    return True


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
        model = _DirectedSAGE(x.shape[1], hidden, dropout)
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


def _DirectedSAGE(in_dim: int, hidden: int, dropout: float):
    """GraphSAGE de 2 camadas com uma convolução para cada sentido do Pix."""
    import torch
    from torch_geometric.nn import SAGEConv

    class DirectedSAGE(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.paid_by = torch.nn.ModuleList([SAGEConv(in_dim, hidden), SAGEConv(hidden, hidden)])
            self.paid_to = torch.nn.ModuleList([SAGEConv(in_dim, hidden), SAGEConv(hidden, hidden)])
            self.head = torch.nn.Linear(hidden, 1)

        def forward(self, x, edges, reverse):
            h = x
            for incoming, outgoing in zip(self.paid_by, self.paid_to):
                h = torch.relu(incoming(h, edges) + outgoing(h, reverse))
                h = torch.nn.functional.dropout(h, p=dropout, training=self.training)
            return self.head(h).squeeze(-1)

    return DirectedSAGE()
