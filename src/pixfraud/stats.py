"""Inferência estatística para a pesquisa.

* ``compare_groups``: cada atributo difere entre contas fraudulentas e
  normais? Teste de Mann-Whitney, tamanho de efeito (delta de Cliff) e
  correção de Holm para múltiplos testes.
* ``bootstrap_metric``: intervalo de confiança de uma métrica de desempenho
  (reamostrando as contas).
* ``paired_comparison``: duas abordagens avaliadas nas mesmas sementes (ex.:
  tabular × grafo). Diferença média com IC, teste de Wilcoxon pareado e teste
  t pareado. ``compare_runs`` aplica o teste a vários pares de conjuntos de
  atributos, com correção de Holm, e ``summarize_runs`` resume as execuções.
* ``null_model_test``: uma estatística do grafo (reciprocidade, triângulos…) é
  maior do que o esperado por acaso? Compara com grafos aleatórios que
  preservam os graus (modelo nulo) e dá o escore z e o p-valor empírico.
* ``contingency_test``: associação entre duas variáveis categóricas
  (qui-quadrado; Fisher exato e razão de chances nas tabelas 2×2), como "é
  fraude" × "foi de madrugada".
* ``kruskal_groups`` e ``dunn_posthoc``: cada atributo difere entre três ou
  mais grupos **independentes** (os papéis das contas, os cenários)? Kruskal-
  Wallis com ε² e Holm; o teste de Dunn diz quais pares diferem.
* ``friedman_models``: vários modelos medidos nas **mesmas** sementes diferem?
  Teste de Friedman, W de Kendall, postos médios e a diferença crítica de
  Nemenyi (Demšar, 2006).
* ``permutation_test_metric`` e ``topk_hypergeom``: o modelo é melhor que o
  acaso (embaralhando o gabarito; contando as fraudes no top-k)?

Qual usar em cada etapa: ``docs/plano-de-testes-estatisticos.md``.
"""

from __future__ import annotations

from collections.abc import Callable

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score, roc_auc_score


def cliffs_delta(x, y) -> float:
    """Delta de Cliff: P(X > Y) - P(X < Y), de -1 a 1 (0 = distribuições iguais)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    u = stats.mannwhitneyu(x, y, alternative="two-sided").statistic
    return float(2 * u / (len(x) * len(y)) - 1)


def effect_size_label(delta: float) -> str:
    """Rótulo do tamanho de efeito de Cliff (limiares de Romano et al., 2006)."""
    size = abs(delta)
    if size < 0.147:
        return "desprezível"
    if size < 0.33:
        return "pequeno"
    if size < 0.474:
        return "médio"
    return "grande"


def holm_correction(p_values) -> np.ndarray:
    """p-valores ajustados pelo método de Holm-Bonferroni (controla o erro familiar)."""
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adjusted = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adjusted[i] = min(1.0, running)
    return adjusted


def compare_groups(features: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Compara cada atributo entre fraude (``labels`` verdadeiro) e normal.

    Mann-Whitney U testa se um grupo tende a ter valores maiores que o outro
    sem supor normalidade, o que é importante porque os atributos têm cauda
    pesada. Com milhares de contas quase tudo fica "significativo", então o
    **tamanho de efeito** (delta de Cliff) é o que diz se a diferença importa.
    """
    labels = labels.reindex(features.index).fillna(False).astype(bool)
    rows = []
    for column in features.columns:
        fraud, normal = features.loc[labels, column], features.loc[~labels, column]
        test = stats.mannwhitneyu(fraud, normal, alternative="two-sided")
        delta = float(2 * test.statistic / (len(fraud) * len(normal)) - 1)
        rows.append({
            "atributo": column,
            "mediana fraude": fraud.median(),
            "mediana normal": normal.median(),
            "U": test.statistic,
            "p-valor": test.pvalue,
            "delta de Cliff": delta,
            "efeito": effect_size_label(delta),
        })
    table = pd.DataFrame(rows).set_index("atributo")
    table.insert(table.columns.get_loc("p-valor") + 1, "p ajustado (Holm)", holm_correction(table["p-valor"]))
    return table.sort_values("delta de Cliff", key=np.abs, ascending=False)


def _precision_at_k(y: np.ndarray, scores: np.ndarray, k: int | None = None) -> float:
    """Fração de fraudes entre as ``k`` contas de maior escore (``k`` padrão: nº de fraudes)."""
    k = int(y.sum()) if k is None else k
    return float(y[np.argsort(-scores)[:k]].mean()) if k else 0.0


METRICS: dict[str, Callable] = {
    "average_precision": average_precision_score,
    "roc_auc": roc_auc_score,
    "precision_at_k": _precision_at_k,
}


def bootstrap_metric(
    labels: pd.Series,
    scores: pd.Series,
    metric: str = "average_precision",
    n_boot: int = 1000,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict[str, float]:
    """Estimativa pontual e IC por bootstrap percentil de uma métrica de desempenho.

    Reamostra as contas com reposição separadamente em fraude e normal
    (bootstrap estratificado), para toda réplica ter a mesma proporção de
    fraudes do dado original.
    """
    y = labels.reindex(scores.index).fillna(False).astype(bool).to_numpy()
    s = scores.to_numpy(dtype=float)
    func = METRICS[metric]
    rng = np.random.default_rng(seed)
    positives, negatives = np.flatnonzero(y), np.flatnonzero(~y)
    replicas = np.empty(n_boot)
    for b in range(n_boot):
        idx = np.concatenate([rng.choice(positives, positives.size), rng.choice(negatives, negatives.size)])
        replicas[b] = func(y[idx], s[idx])
    alpha = (1 - confidence) / 2
    low, high = np.quantile(replicas, [alpha, 1 - alpha])
    return {"estimativa": float(func(y, s)), "ic_inferior": float(low), "ic_superior": float(high)}


def paired_comparison(a: pd.Series, b: pd.Series, confidence: float = 0.95) -> dict[str, float]:
    """Compara duas abordagens medidas nas mesmas unidades (ex.: mesmas sementes).

    Devolve a diferença média ``a - b`` com IC t de Student, o p-valor do
    teste de Wilcoxon pareado (não paramétrico) e o do teste t pareado.
    """
    a, b = a.align(b, join="inner")
    diff = (a - b).to_numpy(dtype=float)
    n = diff.size
    mean = float(diff.mean())
    sem = float(diff.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    t_crit = stats.t.ppf(0.5 + confidence / 2, df=n - 1) if n > 1 else float("nan")
    wilcoxon = stats.wilcoxon(diff).pvalue if n > 1 and np.any(diff != 0) else 1.0
    ttest = stats.ttest_rel(a, b).pvalue if n > 1 and np.any(diff != 0) else 1.0
    return {
        "n": n,
        "diferença média": mean,
        "ic_inferior": mean - t_crit * sem,
        "ic_superior": mean + t_crit * sem,
        "p Wilcoxon": float(wilcoxon),
        "p t pareado": float(ttest),
        "a vence em": int((diff > 0).sum()),
    }


def summarize_runs(runs: pd.DataFrame, metric: str, confidence: float = 0.95, by: list[str] = ()) -> pd.DataFrame:
    """Média, desvio e IC t de ``metric`` por (atributos, modelo) em várias execuções.

    ``by`` acrescenta colunas ao agrupamento (ex.: ``["cenario"]``); nesse caso
    a ordenação pela média é feita dentro de cada grupo.
    """
    grouped = runs.groupby([*by, "atributos", "modelo"], sort=not by)[metric]
    summary = grouped.agg(["mean", "std", "count"])
    t_crit = stats.t.ppf(0.5 + confidence / 2, df=summary["count"] - 1)
    half = t_crit * summary["std"] / np.sqrt(summary["count"])
    summary["ic_inferior"] = summary["mean"] - half
    summary["ic_superior"] = summary["mean"] + half
    if not by:
        return summary.sort_values("mean", ascending=False)
    return summary.groupby(list(by), sort=False, group_keys=False).apply(
        lambda group: group.sort_values("mean", ascending=False)
    )


def compare_runs(
    runs: pd.DataFrame,
    comparisons: list[tuple[str, str]],
    metrics: list[str],
    by: list[str] = (),
    unit: str = "semente",
    between: str = "atributos",
) -> pd.DataFrame:
    """Testes pareados, semente a semente, entre conjuntos de atributos ou entre modelos.

    ``runs`` tem uma linha por (semente, atributos, modelo), como a saída de
    ``pixfraud.experiment.run_seeds``; ``unit`` é a coluna que identifica a
    repetição (as janelas de tempo, num dataset externo). Com
    ``between="atributos"`` (padrão), os pares ``(a, b)`` de ``comparisons`` são
    conjuntos de atributos, comparados dentro de cada modelo; com
    ``between="modelo"``, são modelos, comparados dentro de cada conjunto. Um
    par que não aparece num grupo é pulado. Aplica ``paired_comparison`` a ``a - b``.
    Cada métrica (dentro de cada grupo de ``by``) é uma família de testes, e
    a correção de Holm vale dentro dela: com 10 sementes, o menor p possível
    no Wilcoxon exato é 2/1024 ≈ 0,002, e corrigir por todas as métricas juntas
    tornaria qualquer diferença "não significativa".
    """
    fixed = "modelo" if between == "atributos" else "atributos"
    rows = []
    groups = runs.groupby(list(by), sort=False) if by else [((), runs)]
    for key, group in groups:
        for metric in metrics:
            for value in group[fixed].unique():
                wide = group[group[fixed] == value].pivot(index=unit, columns=between, values=metric)
                for a, b in comparisons:
                    if a not in wide or b not in wide:
                        continue
                    rows.append({
                        **dict(zip(by, key)),
                        "métrica": metric,
                        fixed: value,
                        "comparação": f"{a} - {b}",
                        **paired_comparison(wide[a], wide[b]),
                    })
    if not rows:
        return pd.DataFrame()
    table = pd.DataFrame(rows)
    table["p Wilcoxon (Holm)"] = table.groupby([*by, "métrica"])["p Wilcoxon"].transform(
        lambda p: holm_correction(p.to_numpy())
    )
    return table


def null_model_test(
    graph: nx.DiGraph,
    statistic: Callable[[nx.DiGraph], float],
    n_samples: int = 100,
    seed: int = 0,
) -> dict[str, float]:
    """Compara ``statistic(graph)`` com grafos aleatórios de mesmos graus de entrada e saída.

    O modelo nulo é o modelo de configuração direcionado: cada conta mantém
    exatamente seus graus e as ligações são sorteadas (laços e arestas
    paralelas são descartados). Devolve o valor observado, a média e o desvio
    do nulo, o escore z e o p-valor empírico bilateral.
    """
    observed = float(statistic(graph))
    nodes = list(graph)
    in_seq = [graph.in_degree(v) for v in nodes]
    out_seq = [graph.out_degree(v) for v in nodes]
    rng = np.random.default_rng(seed)
    null = np.empty(n_samples)
    for i in range(n_samples):
        multi = nx.directed_configuration_model(in_seq, out_seq, seed=int(rng.integers(2**31)))
        simple = nx.DiGraph(multi)
        simple.remove_edges_from(nx.selfloop_edges(simple))
        null[i] = statistic(simple)
    mean, std = float(null.mean()), float(null.std(ddof=1))
    extreme = np.abs(null - mean) >= abs(observed - mean)
    return {
        "observado": observed,
        "média nula": mean,
        "desvio nulo": std,
        "z": (observed - mean) / std if std > 0 else float("inf"),
        "p empírico": float((extreme.sum() + 1) / (n_samples + 1)),
    }


def contingency_test(a: pd.Series, b: pd.Series) -> dict:
    """Teste qui-quadrado de independência entre duas variáveis categóricas, com o V de Cramér.

    Numa tabela 2×2 acrescenta o teste exato de Fisher (que vale também com
    contagens pequenas, como as fraudes num top-k) e a razão de chances.
    """
    table = pd.crosstab(a, b)
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.to_numpy().sum()
    cramer = float(np.sqrt(chi2 / (n * (min(table.shape) - 1))))
    result = {"tabela": table, "qui-quadrado": float(chi2), "gl": int(dof), "p-valor": float(p), "V de Cramér": cramer}
    if table.shape == (2, 2):
        fisher = stats.fisher_exact(table.to_numpy())
        result |= {"razão de chances": float(fisher.statistic), "p Fisher": float(fisher.pvalue)}
    return result


def epsilon_squared_label(eps2: float) -> str:
    """Rótulo do ε² do Kruskal-Wallis (limiares usuais de η²: 0,01, 0,06 e 0,14)."""
    if eps2 < 0.01:
        return "desprezível"
    if eps2 < 0.06:
        return "pequeno"
    if eps2 < 0.14:
        return "médio"
    return "grande"


def kruskal_groups(features: pd.DataFrame, groups: pd.Series) -> pd.DataFrame:
    """Kruskal-Wallis de cada atributo entre os grupos de ``groups`` (ex.: o papel da conta).

    Generaliza o ``compare_groups`` para três ou mais grupos **independentes**.
    Devolve H, p, p ajustado por Holm (entre os atributos), o tamanho de efeito
    ε² = H / (n − 1) e o grupo de maior mediana. Um resultado significativo diz
    que *algum* grupo difere; ``dunn_posthoc`` diz quais.
    """
    groups = groups.reindex(features.index)
    keep = groups.notna()
    features, groups = features[keep], groups[keep]
    rows = []
    for column in features.columns:
        samples = [values.to_numpy(dtype=float) for _, values in features[column].groupby(groups)]
        n = sum(len(s) for s in samples)
        try:
            test = stats.kruskal(*samples)
            h, p = float(test.statistic), float(test.pvalue)
        except ValueError:  # todos os valores iguais: nada a distinguir
            h, p = 0.0, 1.0
        eps2 = h / (n - 1) if n > 1 else float("nan")
        medians = features[column].groupby(groups).median()
        rows.append({"atributo": column, "grupos": len(samples), "n": n, "H": h, "p-valor": p,
                     "ε²": eps2, "efeito": epsilon_squared_label(eps2), "maior mediana": medians.idxmax()})
    table = pd.DataFrame(rows).set_index("atributo")
    table.insert(table.columns.get_loc("p-valor") + 1, "p ajustado (Holm)", holm_correction(table["p-valor"]))
    return table.sort_values("ε²", ascending=False)


def dunn_posthoc(values: pd.Series, groups: pd.Series) -> pd.DataFrame:
    """Teste de Dunn (1964): que pares de grupos diferem, depois de um Kruskal-Wallis significativo.

    Compara os postos médios de cada par usando a mesma ordenação do Kruskal-
    Wallis, com a correção para empates, e ajusta os p-valores por Holm entre
    os pares. ``postos médios a - b`` > 0: ``a`` tende a ter valores maiores.
    """
    groups = groups.reindex(values.index)
    keep = groups.notna() & values.notna()
    values, groups = values[keep].astype(float), groups[keep]
    ranks = pd.Series(stats.rankdata(values), index=values.index)
    n = len(values)
    _, ties = np.unique(values, return_counts=True)
    tie_term = float((ties**3 - ties).sum()) / (12 * (n - 1))
    mean_rank, size = ranks.groupby(groups).mean(), ranks.groupby(groups).size()
    names = list(mean_rank.index)
    rows = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            se = np.sqrt((n * (n + 1) / 12 - tie_term) * (1 / size[a] + 1 / size[b]))
            z = (mean_rank[a] - mean_rank[b]) / se if se > 0 else 0.0
            rows.append({"grupo a": a, "grupo b": b, "postos médios a - b": float(mean_rank[a] - mean_rank[b]),
                         "z": float(z), "p-valor": float(2 * stats.norm.sf(abs(z)))})
    table = pd.DataFrame(rows)
    if not table.empty:
        table["p ajustado (Holm)"] = holm_correction(table["p-valor"])
    return table


def friedman_models(
    runs: pd.DataFrame,
    metric: str,
    by: list[str] = (),
    unit: str = "semente",
    between: str = "modelo",
    alpha: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Teste de Friedman entre vários modelos medidos nas mesmas unidades (sementes).

    É o equivalente pareado do Kruskal-Wallis: dentro de cada semente os
    modelos são ordenados (posto 1 = maior ``metric``), e o teste pergunta se
    os postos médios diferem mais do que o acaso explicaria. Só entram as
    sementes em que todos os modelos do grupo têm valor.

    Devolve duas tabelas, uma linha por grupo de ``by``:

    * testes: nº de modelos (k) e de sementes (N), χ², p, W de Kendall
      (concordância entre as sementes, de 0 a 1) e a **diferença crítica** de
      Nemenyi, CD = q_α · √(k(k+1) / 6N): dois modelos cujos postos médios
      diferem menos que CD não se distinguem (Demšar, 2006);
    * postos: o posto médio de cada modelo, do melhor para o pior.
    """
    tests, ranks = [], []
    groups = runs.groupby(list(by), sort=False) if by else [((), runs)]
    for key, group in groups:
        key = key if isinstance(key, tuple) else (key,)
        wide = group.pivot_table(index=unit, columns=between, values=metric, aggfunc="mean").dropna()
        k, n = wide.shape[1], wide.shape[0]
        if k < 3 or n < 2:
            continue
        ranked = wide.rank(axis=1, ascending=False)
        try:
            chi2, p = stats.friedmanchisquare(*(wide[c].to_numpy() for c in wide.columns))
        except ValueError:
            chi2, p = 0.0, 1.0
        q_alpha = stats.studentized_range.ppf(1 - alpha, k, np.inf) / np.sqrt(2)
        labels = dict(zip(by, key))
        tests.append({**labels, "métrica": metric, "k": k, "N": n, "qui-quadrado": float(chi2),
                      "p-valor": float(p), "W de Kendall": float(chi2 / (n * (k - 1))),
                      "diferença crítica": float(q_alpha * np.sqrt(k * (k + 1) / (6 * n)))})
        mean_ranks = ranked.mean().sort_values()
        ranks += [{**labels, "métrica": metric, between: model, "posto médio": float(r),
                   "média": float(wide[model].mean())} for model, r in mean_ranks.items()]
    return pd.DataFrame(tests), pd.DataFrame(ranks)


def permutation_test_metric(
    labels: pd.Series,
    scores: pd.Series,
    metric: str = "average_precision",
    n_perm: int = 1000,
    seed: int = 0,
) -> dict[str, float]:
    """O modelo é melhor que o acaso? Teste de permutação da métrica.

    Embaralha o gabarito ``n_perm`` vezes, recalcula a métrica e conta quantas
    vezes ela igualou ou superou a real: p = (b + 1) / (n_perm + 1). Vale para
    qualquer métrica de ``METRICS``; na AP, a média nula fica perto da taxa de fraude.
    """
    y = labels.reindex(scores.index).fillna(False).astype(bool).to_numpy()
    s = scores.to_numpy(dtype=float)
    func = METRICS[metric]
    observed = float(func(y, s))
    rng = np.random.default_rng(seed)
    null = np.array([func(rng.permutation(y), s) for _ in range(n_perm)])
    return {"estimativa": observed, "média nula": float(null.mean()),
            "p permutação": float(((null >= observed).sum() + 1) / (n_perm + 1))}


def topk_hypergeom(labels: pd.Series, scores: pd.Series, k: int | None = None) -> dict[str, float]:
    """Fraudes entre as ``k`` contas de maior escore contra um sorteio de ``k`` contas.

    Sob a hipótese nula (o top-k é um sorteio), o nº de fraudes no top-k segue
    a distribuição hipergeométrica; p = P(X ≥ observado). ``k`` padrão: o nº de fraudes.
    """
    y = labels.reindex(scores.index).fillna(False).astype(bool).to_numpy()
    total, positives = len(y), int(y.sum())
    k = positives if k is None else int(k)
    hits = int(y[np.argsort(-scores.to_numpy(dtype=float), kind="stable")[:k]].sum())
    return {"k": k, "fraudes no top-k": hits, "esperado ao acaso": k * positives / total if total else 0.0,
            "p hipergeométrico": float(stats.hypergeom.sf(hits - 1, total, positives, k))}
