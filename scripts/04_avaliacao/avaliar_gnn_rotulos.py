"""GraphSAGE com poucos rótulos: a vantagem da GNN sobrevive quando só parte das fraudes é conhecida?

Em ``avaliar_gnn.py`` a GraphSAGE treina com os rótulos de 80% das contas. No Pix,
só uma fração das contas fraudulentas vira conhecida (quando as vítimas contestam pelo
MED) e todas as outras aparecem como "não fraude". Como em ``avaliar_propagacao.py``,
este script sorteia uma fração das fraudes como "já contestadas" e mede, **só nas contas
restantes**, a average precision de:

* ``sage_tabular`` e ``sage_completo``: GraphSAGE treinada com as fraudes conhecidas
  (``pixfraud.gnn.sage_known_fraud_scores``), com os atributos tabulares ou com todos;
* ``rf_tabular`` e ``rf_completo``: Random Forest com os mesmos rótulos e atributos
  (``pixfraud.experiment.known_fraud_scores``);
* ``completo_dbscan``: o melhor detector não supervisionado, que não usa rótulo nenhum;
* ``propagacao_combinado``: o melhor método da culpa por associação (média dos
  percentis da propagação relativa e do ``completo_dbscan``).

Precisa do torch: ``pip install -e ".[gnn]"``.

Saídas em reports/04_avaliacao/results/: gnn_rotulos_execucoes.csv, gnn_rotulos_resumo.csv,
gnn_rotulos_comparacoes.csv e gnn_rotulos_meta.json, e a figura
reports/04_avaliacao/figures/gnn_rotulos_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_gnn_rotulos.py --sementes 10
    python scripts/04_avaliacao/avaliar_gnn_rotulos.py --cenarios realista --fracoes 0.1 --sementes 3
"""

import argparse
import copy
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
    known_fraud_scores,
    load_experiment_config,
    load_scenarios,
    prepare,
    save_metadata,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.flow import propagate_risk  # noqa: E402
from pixfraud.gnn import sage_known_fraud_scores  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

METHODS = ["completo_dbscan", "propagacao_combinado", "rf_tabular", "sage_tabular", "rf_completo", "sage_completo"]
COMPARISONS = [
    ("sage_tabular", "rf_tabular"),
    ("sage_completo", "rf_completo"),
    ("sage_completo", "propagacao_combinado"),
    ("sage_completo", "completo_dbscan"),
]
METRICS = ["average_precision", "precision_at_k"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia a GraphSAGE com só parte das fraudes conhecida.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--fracoes", nargs="+", type=float, default=[0.1, 0.25],
                        help="frações das contas fraudulentas tratadas como já conhecidas")
    parser.add_argument("--epocas", type=int, default=None, help="épocas de treino (padrão: as de pixfraud.gnn)")
    parser.add_argument("--saida", default="reports/04_avaliacao")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    epochs = {"epochs": args.epocas} if args.epocas else {}

    rows = []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            seed_began = time.time()
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            prepared = prepare(accounts, tx, config)
            models = copy.deepcopy(config["modelos"])
            graph = prepared.graph
            tabular = prepared.features[FEATURE_SETS["tabular"]]
            completo = prepared.features[FEATURE_SETS["completo"]]
            dbscan = DETECTORS["dbscan"](completo, **models.get("dbscan", {})).scores
            fraud = prepared.labels.index[prepared.labels]
            rng = np.random.default_rng(seed)  # mesmo sorteio de avaliar_propagacao.py
            for fraction in args.fracoes:
                known = list(rng.choice(fraud, size=max(1, round(fraction * len(fraud))), replace=False))
                labels = prepared.labels.drop(known)  # avalia só nas contas ainda desconhecidas
                propagation = propagate_risk(graph, known, relative=True)
                scores = {
                    "completo_dbscan": dbscan,
                    "propagacao_combinado": sum(s.reindex(labels.index).rank(pct=True) for s in (propagation, dbscan))
                    / 2,
                    "rf_tabular": known_fraud_scores(tabular, known, seed=seed),
                    "sage_tabular": sage_known_fraud_scores(graph, tabular, known, seed=seed, **epochs),
                    "rf_completo": known_fraud_scores(completo, known, seed=seed),
                    "sage_completo": sage_known_fraud_scores(graph, completo, known, seed=seed, **epochs),
                }
                k = int(labels.sum())
                for method in METHODS:
                    score = scores[method].reindex(labels.index).fillna(0.0)
                    rows.append({
                        "cenario": name, "semente": seed, "conhecidas": fraction, "atributos": method,
                        "modelo": "-", "average_precision": average_precision_score(labels, score),
                        "precision_at_k": float(labels[score.nlargest(k).index].mean()),
                        "fraudes_conhecidas": len(known), "fraudes_restantes": k,
                    })
            print(f"{name}: semente {seed}/{args.sementes}, {time.time() - seed_began:.0f} s", flush=True)

    runs = pd.DataFrame(rows)
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    by = ["cenario", "conhecidas"]
    summary = pd.concat({m: summarize_runs(runs, m, by=by) for m in METRICS}, names=["métrica"])
    comparisons = compare_runs(runs, COMPARISONS, METRICS, by=by)
    # "atributos" e "modelo" são as colunas que stats espera; aqui a coluna certa é "metodo"
    runs.rename(columns={"atributos": "metodo"}).drop(columns="modelo").to_csv(
        results / "gnn_rotulos_execucoes.csv", index=False)
    summary.droplevel("modelo").rename_axis(index={"atributos": "metodo"}).to_csv(
        results / "gnn_rotulos_resumo.csv")
    comparisons.drop(columns="modelo").to_csv(results / "gnn_rotulos_comparacoes.csv", index=False)
    save_metadata(results / "gnn_rotulos_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), fracoes=args.fracoes, epocas=args.epocas,
                  duracao_s=round(time.time() - began))
    _plot(summary.loc["average_precision"], args, figures / "gnn_rotulos_average_precision.png")

    print("\naverage precision média, só nas contas ainda desconhecidas:")
    print(summary.loc["average_precision", "mean"].droplevel("modelo").unstack(by).reindex(METHODS)
          .round(3).to_string())
    print("\ncomparações pareadas (average precision):")
    columns = ["cenario", "conhecidas", "comparação", "diferença média", "a vence em", "p Wilcoxon (Holm)"]
    print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))


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
    ax.set_title(f"GraphSAGE com poucos rótulos: AP nas contas ainda desconhecidas ({args.sementes} sementes)",
                 color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
