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
  (qui-quadrado), como "é fraude" × "foi de madrugada".
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
) -> pd.DataFrame:
    """Testes pareados entre conjuntos de atributos, semente a semente.

    ``runs`` tem uma linha por (semente, atributos, modelo), como a saída de
    ``pixfraud.experiment.run_seeds``; ``unit`` é a coluna que identifica a
    repetição (as janelas de tempo, num dataset externo). Para cada métrica, modelo e par
    ``(a, b)`` de ``comparisons``, aplica ``paired_comparison`` a ``a - b``.
    Cada métrica (dentro de cada grupo de ``by``) é uma família de testes, e
    a correção de Holm vale dentro dela: com 10 sementes, o menor p possível
    no Wilcoxon exato é 2/1024 ≈ 0,002, e corrigir por todas as métricas juntas
    tornaria qualquer diferença "não significativa".
    """
    rows = []
    groups = runs.groupby(list(by), sort=False) if by else [((), runs)]
    for key, group in groups:
        for metric in metrics:
            for model in group["modelo"].unique():
                wide = group[group["modelo"] == model].pivot(index=unit, columns="atributos", values=metric)
                for a, b in comparisons:
                    rows.append({
                        **dict(zip(by, key)),
                        "métrica": metric,
                        "modelo": model,
                        "comparação": f"{a} - {b}",
                        **paired_comparison(wide[a], wide[b]),
                    })
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
    """Teste qui-quadrado de independência entre duas variáveis categóricas, com o V de Cramér."""
    table = pd.crosstab(a, b)
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.to_numpy().sum()
    cramer = float(np.sqrt(chi2 / (n * (min(table.shape) - 1))))
    return {"tabela": table, "qui-quadrado": float(chi2), "gl": int(dof), "p-valor": float(p), "V de Cramér": cramer}
