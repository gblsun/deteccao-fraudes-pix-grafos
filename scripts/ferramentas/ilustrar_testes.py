"""Figuras didáticas dos testes de hipótese: uma por etapa da pesquisa.

Cada figura tem três partes (ver docs/plano-de-testes-estatisticos.md):

1. **a estatística do teste sob a hipótese nula**, com a zona crítica de
   α = 5% sombreada e o valor observado como linha vertical: dá para ver se o
   resultado caiu na zona crítica;
2. **os dados contra a curva normal**: histograma com a normal ajustada, Q-Q
   plot e o teste de Shapiro-Wilk. A cauda pesada é o que justifica os testes
   não paramétricos (Mann-Whitney, Kruskal-Wallis, Wilcoxon) no lugar do t;
3. a ressalva: com milhares de contas, quase tudo cai muito além da zona
   crítica, e por isso o tamanho do efeito importa mais que o p.

As estatísticas de cada etapa:

* 01_dados: o z do modelo nulo (reciprocidade da rede contra grafos aleatórios
  de mesmos graus);
* 02_exploracao: o z do Mann-Whitney (fraude × legítima) e o H do
  Kruskal-Wallis (6 papéis) contra a χ², no atributo de maior efeito;
* 03_modelos: a AP do DBSCAN contra o nulo da permutação do gabarito;
* 04_avaliacao: o t pareado e o z do Wilcoxon entre dois modelos e o χ² do
  Friedman entre todos, a partir de reports/03_modelos/results/modelos_execucoes.csv.

As etapas 01 a 03 usam uma rede de validação (semente 1001), gerada na hora.

Saídas: reports/<etapa>/figures/testes_<etapa>.png

Uso:
    python scripts/ferramentas/ilustrar_testes.py
    python scripts/ferramentas/ilustrar_testes.py --cenario realista --etapas 02_exploracao
"""

import argparse
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats as sps  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import load_experiment_config, load_scenarios, prepare  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_groups, friedman_models, null_model_test  # noqa: E402
from pixfraud.visualization import (  # noqa: E402
    INK,
    INK_SECONDARY,
    SURFACE,
    model_label,
    plot_normality,
    plot_test_statistic,
)

STAGES = ("01_dados", "02_exploracao", "03_modelos", "04_avaliacao")
VALIDATION_SEED = 1001
CAVEAT = ("Ressalva: com milhares de contas, quase todo teste cai muito além da zona crítica. O p diz só que o efeito "
          "existe;\no tamanho do efeito (delta de Cliff, ε², diferença de AP) é o que diz se ele importa.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Figuras didáticas dos testes de hipótese, uma por etapa.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenario", default="calibrado")
    parser.add_argument("--etapas", nargs="+", default=list(STAGES), choices=STAGES)
    parser.add_argument("--execucoes", default="reports/03_modelos/results/modelos_execucoes.csv",
                        help="AP por (cenário, semente, modelo), para a etapa 04")
    parser.add_argument("--saida", default="reports", help="pasta com uma subpasta por etapa")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    simulation = replace(with_overrides(load_config(args.config), scenarios[args.cenario]), seed=VALIDATION_SEED)
    accounts, tx = generate_dataset(simulation)
    prepared = prepare(accounts, tx, config)
    info = accounts.set_index("account_id")
    roles = info["role"].where(~info["is_victim"], "vitima").reindex(prepared.features.index)
    where = f"cenário {args.cenario}, semente {VALIDATION_SEED}"

    drawers = {
        "01_dados": lambda fig: _stage_data(fig, prepared, where),
        "02_exploracao": lambda fig: _stage_exploration(fig, prepared, roles, where),
        "03_modelos": lambda fig: _stage_models(fig, prepared, config, where),
        "04_avaliacao": lambda fig: _stage_evaluation(fig, Path(args.execucoes)),
    }
    for stage in args.etapas:
        fig = plt.figure(figsize=(11, 7.2), layout="constrained")
        title = drawers[stage](fig)
        if title is None:
            plt.close(fig)
            print(f"{stage}: pulado (faltam dados)")
            continue
        fig.suptitle(title, color=INK, fontsize=11, x=0.01, ha="left")
        fig.text(0.01, 0.005, CAVEAT, fontsize=7.5, color=INK_SECONDARY, va="bottom")
        out = Path(args.saida) / stage / "figures" / f"testes_{stage}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=150, facecolor=SURFACE)
        plt.close(fig)
        print(f"{stage}: {out}")


def _grid(fig, top: int):
    """Linha de cima: ``top`` painéis da estatística; linha de baixo: histograma e Q-Q plot."""
    spec = fig.add_gridspec(3, max(top, 2), height_ratios=[1, 1, 0.12])
    stats_axes = [fig.add_subplot(spec[0, i]) for i in range(top)]
    hist, qq = fig.add_subplot(spec[1, 0]), fig.add_subplot(spec[1, 1])
    return stats_axes, hist, qq


def _stage_data(fig, prepared, where):
    (ax,), hist, qq = _grid(fig, 1)
    result = null_model_test(prepared.graph, nx.reciprocity, n_samples=50, seed=VALIDATION_SEED)
    plot_test_statistic(ax, sps.norm(), result["z"], "z do modelo nulo")
    ax.set_title(f"Reciprocidade: observada {result['observado']:.3f} × nula {result['média nula']:.3f} "
                 f"(z = {result['z']:.1f})", fontsize=9, color=INK, loc="left")
    degrees = np.array([d for _, d in prepared.graph.in_degree()])
    plot_normality(hist, qq, degrees, "grau de entrada das contas")
    return f"1. Dados: a estrutura da rede é diferente do acaso? ({where})"


def _stage_exploration(fig, prepared, roles, where):
    (ax_mw, ax_kw), hist, qq = _grid(fig, 2)
    table = compare_groups(prepared.features, prepared.labels)
    attribute = table.index[0]
    values, labels = prepared.features[attribute], prepared.labels.reindex(prepared.features.index)
    fraud, legit = values[labels], values[~labels]
    n1, n2 = len(fraud), len(legit)
    u = sps.mannwhitneyu(fraud, legit, alternative="two-sided").statistic
    z = (u - n1 * n2 / 2) / np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    plot_test_statistic(ax_mw, sps.norm(), z, "z do Mann-Whitney")
    delta = table.loc[attribute, "delta de Cliff"]
    ax_mw.set_title(f"Fraude × legítima em {attribute}\n(delta de Cliff = {delta:+.2f})", fontsize=9, color=INK,
                    loc="left")
    groups = [values[roles == r] for r in roles.dropna().unique()]
    h = sps.kruskal(*groups).statistic
    plot_test_statistic(ax_kw, sps.chi2(len(groups) - 1), h, f"H do Kruskal-Wallis (χ², {len(groups) - 1} gl)",
                        two_sided=False)
    ax_kw.set_title(f"Os {len(groups)} papéis em {attribute}\n(ε² = {h / (len(values) - 1):.2f})", fontsize=9,
                    color=INK, loc="left")
    plot_normality(hist, qq, values, attribute)
    return f"2. Exploração: o atributo de maior efeito separa fraude e papéis? ({where})"


def _stage_models(fig, prepared, config, where):
    (ax,), hist, qq = _grid(fig, 1)
    features = prepared.features[FEATURE_SETS["completo"]]
    scores = DETECTORS["dbscan"](features, **config["modelos"].get("dbscan", {})).scores
    labels = prepared.labels.reindex(scores.index)
    y, s = labels.to_numpy(), scores.to_numpy(dtype=float)
    rng = np.random.default_rng(VALIDATION_SEED)
    observed = average_precision_score(y, s)
    null = np.array([average_precision_score(rng.permutation(y), s) for _ in range(500)])
    p = ((null >= observed).sum() + 1) / (len(null) + 1)  # como em stats.permutation_test_metric
    plot_test_statistic(ax, None, observed, "AP com o gabarito embaralhado", two_sided=False, null_sample=null)
    ax.set_title(f"DBSCAN: AP observada {observed:.3f} × acaso {null.mean():.3f} (p = {p:.3g})",
                 fontsize=9, color=INK, loc="left")
    plot_normality(hist, qq, scores, "escore de risco do DBSCAN")
    return f"3. Modelos: o modelo é melhor que o acaso? ({where})"


def _stage_evaluation(fig, runs_path: Path):
    if not runs_path.exists():
        return None
    runs = pd.read_csv(runs_path)
    scenario = runs["cenario"].iloc[0]
    runs = runs[runs["cenario"] == scenario]
    means = runs.groupby("modelo")["average_precision"].mean().sort_values(ascending=False)
    best, reference = means.index[0], "dbscan" if "dbscan" in means.index else means.index[1]
    wide = runs.pivot_table(index="semente", columns="modelo", values="average_precision")
    diff = (wide[best] - wide[reference]).dropna()
    n = len(diff)
    (ax_t, ax_w, ax_f), hist, qq = _grid(fig, 3)
    t = sps.ttest_rel(wide.loc[diff.index, best], wide.loc[diff.index, reference]).statistic
    plot_test_statistic(ax_t, sps.t(n - 1), t, f"t pareado ({n - 1} gl)")
    ax_t.set_title(f"{model_label(best)} − {model_label(reference)}\nt pareado", fontsize=9, color=INK, loc="left")
    ranks = sps.rankdata(np.abs(diff[diff != 0]))
    w_plus, m = ranks[(diff[diff != 0] > 0).to_numpy()].sum(), len(ranks)
    z = (w_plus - m * (m + 1) / 4) / np.sqrt(m * (m + 1) * (2 * m + 1) / 24) if m else 0.0
    plot_test_statistic(ax_w, sps.norm(), z, "z do Wilcoxon pareado")
    ax_w.set_title(f"Wilcoxon pareado\n(vence em {int((diff > 0).sum())} de {n})", fontsize=9, color=INK, loc="left")
    tests, _ = friedman_models(runs, "average_precision")
    row = tests.iloc[0]
    plot_test_statistic(ax_f, sps.chi2(int(row["k"]) - 1), row["qui-quadrado"],
                        f"χ² do Friedman ({int(row['k']) - 1} gl)", two_sided=False)
    ax_f.set_title(f"Friedman: {int(row['k'])} modelos\n(W de Kendall = {row['W de Kendall']:.2f})", fontsize=9,
                   color=INK, loc="left")
    plot_normality(hist, qq, diff, f"diferença de AP por semente ({n})")
    return f"4. Avaliação: um modelo é melhor que outro? (cenário {scenario}, {n} sementes)"


if __name__ == "__main__":
    main()
