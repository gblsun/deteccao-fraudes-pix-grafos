"""Detectores de anomalia não supervisionados aplicados aos atributos das contas.

Todos partem da mesma matriz (``prepare_matrix``: log1p e padronização) e
devolvem um ``Detection``: um escore contínuo, que ordena as contas, e um
rótulo binário. O que muda é a ideia de "anômalo":

* ``isolation_forest``: a conta é isolada com poucos cortes aleatórios;
* ``dbscan``: a conta está fora das regiões densas (raio único para todos);
* ``local_outlier_factor``: a vizinhança da conta é menos densa que a dos
  seus vizinhos, o que acha anomalias **locais**, em regiões de densidade
  diferente, que um raio único não pega;
* ``ecod``: a conta está na cauda da distribuição de vários atributos ao mesmo
  tempo (cada atributo olhado sozinho, sem parâmetro para ajustar);
* ``one_class_svm``: a conta fica fora da fronteira que envolve a maior parte
  dos dados;
* ``autoencoder``: uma rede que aprendeu a reconstruir as contas típicas erra
  muito ao reconstruir esta;
* ``knn``: a conta está longe, em média, das suas k contas mais parecidas;
* ``kmeans``: a conta está longe do centro do grupo (K-Means) mais próximo;
* ``pca``: a conta não é bem descrita pelas poucas direções (componentes
  principais) que resumem a maior parte da variação das contas.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import rankdata, skew
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.exceptions import ConvergenceWarning
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import SGDOneClassSVM
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


@dataclass
class Detection:
    """Resultado de um detector: um escore contínuo e um rótulo binário por conta.

    Os escores servem para ordenar as contas (AP, precision@k, grafo de calor); a
    escala depende do modelo, então só a ordem é comparável entre detectores.
    """

    scores: pd.Series  # quanto maior, mais anômala a conta
    is_anomaly: pd.Series  # rótulo binário atribuído pelo modelo


def prepare_matrix(features: pd.DataFrame) -> np.ndarray:
    """Aplica log1p (os atributos são não negativos e de cauda pesada) e padroniza cada coluna."""
    values = features.to_numpy(dtype=float)
    negativas = features.columns[(values < 0).any(axis=0)]
    if len(negativas):  # log1p de valor negativo vira NaN, e o erro só apareceria lá na frente
        raise ValueError(f"atributos com valores negativos não são aceitos: {list(negativas)}")
    return StandardScaler().fit_transform(np.log1p(values))


def isolation_forest(
    features: pd.DataFrame,
    n_estimators: int = 300,
    contamination: float | str = "auto",
    seed: int = 42,
) -> Detection:
    """Isolation Forest: contas isoladas com poucas partições aleatórias são anômalas."""
    X = prepare_matrix(features)
    model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=seed).fit(X)
    return Detection(
        scores=pd.Series(-model.score_samples(X), index=features.index, name="score"),
        is_anomaly=pd.Series(model.predict(X) == -1, index=features.index, name="is_anomaly"),
    )


def dbscan(
    features: pd.DataFrame,
    eps: float | str = "auto",
    min_samples: int = 10,
    eps_quantile: float = 0.95,
    max_exact: int = 20_000,
) -> Detection:
    """DBSCAN: contas classificadas como ruído (fora de regiões densas) são anômalas.

    Como o DBSCAN não produz um escore contínuo, usamos como escore a distância
    ao ``min_samples``-ésimo vizinho mais próximo (k-distance): um ponto é
    núcleo de cluster exatamente quando essa distância é <= ``eps``. Com
    ``eps="auto"``, ``eps`` é o quantil ``eps_quantile`` dessas distâncias.
    Isso é só uma heurística; o ideal é escolher ``eps`` pelo gráfico de
    k-distance (ver notebook de análise exploratória).

    ``max_exact``: acima desse número de contas, o rótulo binário deixa de sair
    do DBSCAN e passa a ser "não é ponto de núcleo" (k-distance > ``eps``). O
    motivo é memória: o DBSCAN guarda a vizinhança de **cada** ponto e, com
    ``eps`` no quantil 0,95, cada conta tem ~20% das contas como vizinhas, o
    que cresce com o quadrado do número de contas (7 MB com 2 mil contas,
    ~16 GB com 100 mil). Os escores não mudam, então average precision e
    precision@k são idênticas; muda só o rótulo binário, que passa a incluir os
    pontos de borda (97,6% de concordância no dataset sintético).
    """
    X = prepare_matrix(features)
    distances, _ = NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)
    k_distance = distances[:, -1]
    if eps == "auto":
        # Com muitas contas idênticas (ex.: poucos atributos numa janela curta), o
        # quantil pode ser 0, que o DBSCAN recusa. Um eps mínimo mantém as contas
        # idênticas como vizinhas, e qualquer conta diferente delas vira ruído.
        eps = max(float(np.quantile(k_distance, eps_quantile)), 1e-9)
    if len(X) <= max_exact:
        is_anomaly = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(X) == -1
    else:
        is_anomaly = k_distance > eps  # aproximação barata: não é ponto de núcleo
    return Detection(
        scores=pd.Series(k_distance, index=features.index, name="score"),
        is_anomaly=pd.Series(is_anomaly, index=features.index, name="is_anomaly"),
    )


def local_outlier_factor(features: pd.DataFrame, n_neighbors: int = 20) -> Detection:
    """Local Outlier Factor: compara a densidade da conta com a dos seus vizinhos.

    Enquanto o DBSCAN usa o mesmo raio para toda a base, o LOF olha para cada
    conta em relação à sua vizinhança: uma conta em região esparsa não é
    anômala se os vizinhos também estão espalhados. O escore é o fator de
    outlier (1 = igual aos vizinhos; quanto maior, mais isolada), e o rótulo
    binário é o do próprio LOF.

    Gasta memória proporcional a ``n_neighbors`` por conta, e não ao quadrado
    do número de contas como o rótulo exato do DBSCAN.
    """
    X = prepare_matrix(features)
    model = LocalOutlierFactor(n_neighbors=min(n_neighbors, len(X) - 1))
    labels = model.fit_predict(X)
    return Detection(
        scores=pd.Series(-model.negative_outlier_factor_, index=features.index, name="score"),
        is_anomaly=pd.Series(labels == -1, index=features.index, name="is_anomaly"),
    )


def ecod(features: pd.DataFrame, contamination: float = 0.05) -> Detection:
    """ECOD: probabilidade de cauda empírica, atributo por atributo (Li et al., 2022).

    Para cada atributo, a função de distribuição empírica diz quão rara é a
    conta pela esquerda e pela direita; o escore soma ``-log`` dessas
    probabilidades em todos os atributos. Faz isso três vezes (cauda esquerda,
    direita e a indicada pela assimetria de cada atributo) e fica com a maior.
    Não tem parâmetro para ajustar e é muito rápido, mas ignora a relação entre
    atributos: uma conta comum em cada atributo e rara na combinação passa.
    O rótulo binário marca a fração ``contamination`` de maior escore.
    """
    X = prepare_matrix(features)
    n = len(X)
    left = rankdata(X, method="max", axis=0) / n  # P(X <= x)
    right = (n - rankdata(X, method="min", axis=0) + 1) / n  # P(X >= x)
    tail_left, tail_right = -np.log(left), -np.log(right)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # atributo constante: assimetria indefinida
        skewness = np.nan_to_num(skew(X, axis=0))
    tail_auto = np.where(skewness < 0, tail_left, tail_right)
    scores = np.max([tail_left.sum(axis=1), tail_right.sum(axis=1), tail_auto.sum(axis=1)], axis=0)
    return _detection(scores, _top_fraction(scores, contamination), features.index)


def one_class_svm(
    features: pd.DataFrame,
    nu: float = 0.05,
    gamma: float | str = "scale",
    max_exact: int = 5_000,
    n_components: int = 300,
    seed: int = 42,
) -> Detection:
    """One-Class SVM: uma fronteira (núcleo RBF) que envolve a maior parte das contas.

    ``nu`` é, aproximadamente, a fração de contas deixadas do lado de fora
    (anômalas). O SVM exato custa entre o quadrado e o cubo do número de
    contas; acima de ``max_exact``, o núcleo é aproximado (Nyström, com
    ``n_components`` pontos) e o SVM é treinado por gradiente estocástico,
    com custo linear. O escore é a distância para dentro da fronteira, com o
    sinal trocado: quanto maior, mais para fora.
    """
    X = prepare_matrix(features)
    if len(X) <= max_exact:
        model = OneClassSVM(nu=nu, gamma=gamma).fit(X)
        Z = X
    else:
        if gamma == "scale":  # a mesma regra do scikit-learn para o núcleo exato
            gamma = 1.0 / (X.shape[1] * (X.var() or 1.0))
        Z = Nystroem(gamma=gamma, n_components=min(n_components, len(X)), random_state=seed).fit_transform(X)
        model = SGDOneClassSVM(nu=nu, random_state=seed).fit(Z)
    scores = -model.decision_function(Z)
    return _detection(scores, model.predict(Z) == -1, features.index)


def autoencoder(
    features: pd.DataFrame,
    max_iter: int = 300,
    contamination: float = 0.05,
    seed: int = 42,
) -> Detection:
    """Autoencoder: a conta que a rede não consegue reconstruir é anômala.

    Uma rede neural pequena (``MLPRegressor`` do scikit-learn) aprende a
    devolver a própria entrada passando por uma camada estreita, com cerca de
    um terço do número de atributos. Como a maioria das contas é legítima, ela
    aprende o que é típico; o escore é o erro médio de reconstrução de cada
    conta. Para de treinar quando o erro de validação deixa de cair.
    """
    X = prepare_matrix(features)
    n_features = X.shape[1]
    bottleneck = max(1, n_features // 3)
    hidden = max(bottleneck + 1, (n_features + 1) // 2)
    model = MLPRegressor(hidden_layer_sizes=(hidden, bottleneck, hidden), alpha=1e-3, max_iter=max_iter,
                         early_stopping=len(X) >= 50, n_iter_no_change=10, random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(X, X)
    reconstruction = model.predict(X).reshape(X.shape)
    scores = ((reconstruction - X) ** 2).mean(axis=1)
    return _detection(scores, _top_fraction(scores, contamination), features.index)


def knn(features: pd.DataFrame, n_neighbors: int = 10, contamination: float = 0.05) -> Detection:
    """KNN: distância média da conta às suas ``n_neighbors`` vizinhas mais próximas.

    É a versão não supervisionada do KNN (Ramaswamy et al., 2000; Angiulli e
    Pizzuti, 2002): ninguém diz o que é fraude, e a conta é anômala quando até as
    contas mais parecidas com ela estão longe. O DBSCAN usa só a distância à
    k-ésima vizinha (o raio do núcleo); a média de todas as k é menos sensível a
    uma única vizinha coincidente. O rótulo binário marca a fração
    ``contamination`` de maior escore. A versão supervisionada (que vota com os
    rótulos das vizinhas) fica em ``experiment.supervised_scores``.
    """
    X = prepare_matrix(features)
    k = min(n_neighbors, len(X) - 1)
    distances, _ = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X)
    scores = distances[:, 1:].mean(axis=1)  # a coluna 0 é a própria conta
    return _detection(scores, _top_fraction(scores, contamination), features.index)


def kmeans(
    features: pd.DataFrame,
    n_clusters: int = 8,
    min_cluster_fraction: float = 0.01,
    contamination: float = 0.05,
    seed: int = 42,
) -> Detection:
    """K-Means: distância da conta ao centro do grupo grande mais próximo.

    O K-Means divide as contas em ``n_clusters`` grupos; uma conta típica fica
    perto do centro do seu grupo. Um cuidado: contas anômalas parecidas entre si
    (as laranjas de uma quadrilha, por exemplo) podem formar um grupo próprio e
    ficar perto do centro dele. Por isso, grupos com menos de
    ``min_cluster_fraction`` das contas não contam como "normais": a distância é
    medida até o centro de um grupo grande (a ideia do CBLOF, He et al., 2003).
    """
    X = prepare_matrix(features)
    k = max(1, min(n_clusters, len(X)))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)  # contas repetidas: menos grupos distintos que k
        model = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
    sizes = np.bincount(model.labels_, minlength=k)
    large = sizes >= max(min_cluster_fraction * len(X), 1)
    centers = model.cluster_centers_[large] if large.any() else model.cluster_centers_
    distances = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
    scores = distances.min(axis=1)
    return _detection(scores, _top_fraction(scores, contamination), features.index)


def pca(features: pd.DataFrame, variance: float = 0.9, contamination: float = 0.05) -> Detection:
    """PCA: erro de reconstrução com os componentes principais que explicam ``variance`` da variação.

    As contas típicas são bem resumidas por poucas direções (combinações de
    atributos que variam juntos, como grau de entrada e volume recebido). O
    escore é o quanto da conta fica de fora desse resumo: o erro médio ao
    reconstruí-la só com esses componentes. É o "autoencoder linear", sem
    treino iterativo nem semente (Shyu et al., 2003).
    """
    X = prepare_matrix(features)
    n_features = X.shape[1]
    model = PCA(n_components=variance, svd_solver="full").fit(X) if n_features > 1 else None
    if model is None or model.n_components_ >= n_features:  # ao menos uma direção fica de fora
        model = PCA(n_components=max(n_features - 1, 1), svd_solver="full").fit(X)
    reconstruction = model.inverse_transform(model.transform(X))
    scores = ((X - reconstruction) ** 2).mean(axis=1)
    return _detection(scores, _top_fraction(scores, contamination), features.index)


def _top_fraction(scores: np.ndarray, fraction: float) -> np.ndarray:
    """Rótulo binário dos detectores que só dão escore: a fração ``fraction`` de maior escore."""
    return scores > np.quantile(scores, 1.0 - fraction)


def _detection(scores, is_anomaly, index) -> Detection:
    return Detection(
        scores=pd.Series(np.asarray(scores, dtype=float), index=index, name="score"),
        is_anomaly=pd.Series(np.asarray(is_anomaly, dtype=bool), index=index, name="is_anomaly"),
    )


DETECTORS = {
    "isolation_forest": isolation_forest,
    "dbscan": dbscan,
    "local_outlier_factor": local_outlier_factor,
    "ecod": ecod,
    "one_class_svm": one_class_svm,
    "autoencoder": autoencoder,
    "knn": knn,
    "kmeans": kmeans,
    "pca": pca,
}
