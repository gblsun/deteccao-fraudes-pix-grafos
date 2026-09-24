"""Culpa por associação: com algumas fraudes já conhecidas, quanto se acha do resto?

No Pix, parte das contas fraudulentas vira conhecida quando as vítimas contestam
(MED). Este script sorteia uma fração das contas fraudulentas como "já
contestadas" e mede, **só nas contas restantes**, a average precision de:

* ``propagacao`` e ``propagacao_relativa``: PageRank personalizado a partir das
  contas conhecidas (``pixfraud.flow.propagate_risk``); a relativa divide pelo
  PageRank comum, para não favorecer as contas muito conectadas;
* ``completo_dbscan`` e ``temporal_if``: os melhores detectores não supervisionados,
  que não usam as contas conhecidas;
* ``combinado``: média dos percentis da propagação relativa e do ``completo_dbscan``.

Saídas em reports/results/: propagacao_execucoes.csv, propagacao_resumo.csv,
propagacao_comparacoes.csv e propagacao_meta.json, e a figura
reports/figures/propagacao_average_precision.png.

Uso:
    python scripts/avaliar_propagacao.py --sementes 10
    python scripts/avaliar_propagacao.py --cenarios realista --fracoes 0.1 --sementes 3
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    load_experiment_config,
    load_scenarios,
    prepare,
    save_metadata,
    seeded_models,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.flow import propagate_risk  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

METHODS = ["propagacao", "propagacao_relativa", "completo_dbscan", "temporal_if", "combinado"]
COMPARISONS = [
    ("combinado", "completo_dbscan"),
    ("propagacao_relativa", "completo_dbscan"),
    ("propagacao_relativa", "propagacao"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia a propagação de risco a partir de fraudes conhecidas.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--fracoes", nargs="+", type=float, default=[0.1, 0.25],
                        help="frações das contas fraudulentas tratadas como já conhecidas")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")

    rows = []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            prepared = prepare(accounts, tx, config)
            models = seeded_models(config["modelos"], seed)
            detectors = {
                "completo_dbscan": _scores(prepared, "completo", "dbscan", models),
                "temporal_if": _scores(prepared, "temporal", "isolation_forest", models),
            }
            fraud = prepared.labels.index[prepared.labels]
            rng = np.random.default_rng(seed)
            for fraction in args.fracoes:
                known = list(rng.choice(fraud, size=max(1, round(fraction * len(fraud))), replace=False))
                scores = {
                    "propagacao": propagate_risk(prepared.graph, known),
                    "propagacao_relativa": propagate_risk(prepared.graph, known, relative=True),
                    **detectors,
                }
                labels = prepared.labels.drop(known)  # avalia só nas contas ainda desconhecidas
                percentiles = [scores[m].reindex(labels.index).rank(pct=True)
                               for m in ("propagacao_relativa", "completo_dbscan")]
                scores["combinado"] = sum(percentiles) / 2
                for method in METHODS:
                    score = scores[method].reindex(labels.index).fillna(0.0)
                    k = int(labels.sum())
                    rows.append({
                        "cenario": name, "semente": seed, "conhecidas": fraction, "atributos": method,
                        "modelo": "-", "average_precision": average_precision_score(labels, score),
                        "precision_at_k": float(labels[score.nlargest(k).index].mean()),
                        "fraudes_conhecidas": len(known), "fraudes_restantes": k,
                    })
            print(f"{name}: semente {seed}/{args.sementes} concluída", flush=True)

    runs = pd.DataFrame(rows)
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    by = ["cenario", "conhecidas"]
    summary = pd.concat({m: summarize_runs(runs, m, by=by) for m in ("average_precision", "precision_at_k")},
                        names=["métrica"])
    comparisons = compare_runs(runs, COMPARISONS, ["average_precision", "precision_at_k"], by=by)
    # "atributos" e "modelo" são as colunas que stats espera; aqui a coluna certa é "metodo"
    runs.rename(columns={"atributos": "metodo"}).drop(columns="modelo").to_csv(
        results / "propagacao_execucoes.csv", index=False)
    summary.droplevel("modelo").rename_axis(index={"atributos": "metodo"}).to_csv(results / "propagacao_resumo.csv")
    comparisons.drop(columns="modelo").to_csv(results / "propagacao_comparacoes.csv", index=False)
    save_metadata(results / "propagacao_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), fracoes=args.fracoes,
                  duracao_s=round(time.time() - began))
    _plot(summary.loc["average_precision"], args, figures / "propagacao_average_precision.png")

    print("\naverage precision média, só nas contas ainda desconhecidas:")
    print(summary.loc["average_precision", "mean"].droplevel("modelo").unstack(by).round(3).to_string())
    print("\ncomparações pareadas (average precision):")
    columns = ["cenario", "conhecidas", "comparação", "diferença média", "a vence em", "p Wilcoxon (Holm)"]
    print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))


def _scores(prepared, feature_set: str, model: str, models: dict) -> pd.Series:
    """Escore de um detector não supervisionado (não usa as contas conhecidas)."""
    return DETECTORS[model](prepared.features[FEATURE_SETS[feature_set]], **models.get(model, {})).scores


def _plot(summary: pd.DataFrame, args, path: Path) -> None:
    """Matriz método × (cenário, fração conhecida) da AP média."""
    mean = summary["mean"].droplevel("modelo")
    columns = [(c, f) for c in args.cenarios for f in args.fracoes]
    matrix = pd.DataFrame({f"{c}\n{f:.0%} conhecidas": [mean.get((c, f, m), np.nan) for m in METHODS]
                           for c, f in columns}, index=METHODS)
    fig, ax = plt.subplots(figsize=(2.8 + 1.4 * len(columns), 1.6 + 0.5 * len(METHODS)), layout="constrained")
    mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, ax=ax)
    colorbar = fig.colorbar(mesh, ax=ax, shrink=0.6, pad=0.02)
    colorbar.set_label("average precision", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    ax.set_title(f"Culpa por associação: AP nas contas ainda desconhecidas ({args.sementes} sementes)",
                 color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
