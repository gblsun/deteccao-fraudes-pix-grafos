"""Culpa por associação: com algumas fraudes já conhecidas, quanto se acha do resto?

No Pix, parte das contas fraudulentas vira conhecida quando as vítimas contestam
(MED). Este script sorteia uma fração das contas fraudulentas como "já
contestadas" e mede, **só nas contas restantes**, a average precision de:

* ``propagacao`` e ``propagacao_relativa``: PageRank personalizado a partir das
  contas conhecidas (``pixfraud.flow.propagate_risk``); a relativa divide pelo
  PageRank comum, para não favorecer as contas muito conectadas;
* ``completo_dbscan`` e ``temporal_if``: os melhores detectores não supervisionados,
  que não usam as contas conhecidas;
* ``combinado``: média dos percentis da propagação relativa e do ``completo_dbscan``;
* ``label_spreading``: propagação de rótulos com as fraudes conhecidas (+1) **e**
  uma fração das contas legítimas também tratadas como conhecidas (-1), a mesma
  fração das fraudes (``pixfraud.flow.label_spreading``);
* ``label_spreading_combinado``: média dos percentis do label spreading e do
  ``completo_dbscan``.

As contas conhecidas (fraudes e legítimas) ficam fora da avaliação de todos os
métodos. Com ``--conhecidas contestacao``, as fraudes conhecidas deixam de ser
sorteadas: são as contas que receberam um golpe contestado até o fim do período
(coluna ``contestado_em``, só nos cenários com ``p_contested`` > 0), como no MED.

Saídas em reports/results/: propagacao_execucoes.csv, propagacao_resumo.csv,
propagacao_comparacoes.csv e propagacao_meta.json, e a figura
reports/figures/propagacao_average_precision.png.

Uso:
    python scripts/avaliar_propagacao.py --sementes 10
    python scripts/avaliar_propagacao.py --cenarios realista --fracoes 0.1 --sementes 3
    python scripts/avaliar_propagacao.py --cenarios calibrado --conhecidas contestacao
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
from pixfraud.flow import label_spreading, propagate_risk  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

METHODS = ["propagacao", "propagacao_relativa", "label_spreading", "completo_dbscan", "temporal_if", "combinado",
           "label_spreading_combinado"]
COMPARISONS = [
    ("combinado", "completo_dbscan"),
    ("propagacao_relativa", "completo_dbscan"),
    ("propagacao_relativa", "propagacao"),
    ("label_spreading", "propagacao_relativa"),
    ("label_spreading_combinado", "combinado"),
]
CONTESTED = "contestacao"


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia a propagação de risco a partir de fraudes conhecidas.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--fracoes", nargs="+", type=float, default=[0.1, 0.25],
                        help="frações das contas fraudulentas tratadas como já conhecidas")
    parser.add_argument("--conhecidas", choices=["fracao", CONTESTED], default="fracao",
                        help="fraudes conhecidas sorteadas (--fracoes) ou vindas das contestações")
    parser.add_argument("--fracao-legitimas", type=float, default=None,
                        help="fração das legítimas conhecidas no modo contestacao (padrão: 0,25)")
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
            legit = prepared.labels.index[~prepared.labels]
            rng = np.random.default_rng(seed)
            legit_rng = np.random.default_rng([seed, 1])  # separado: não muda o sorteio das fraudes
            for fraction, known in _known_frauds(args, rng, fraud, tx):
                legit_fraction = fraction if fraction != CONTESTED else (args.fracao_legitimas or 0.25)
                known_legit = list(legit_rng.choice(legit, size=round(legit_fraction * len(legit)), replace=False))
                scores = {
                    "propagacao": propagate_risk(prepared.graph, known),
                    "propagacao_relativa": propagate_risk(prepared.graph, known, relative=True),
                    "label_spreading": label_spreading(prepared.graph, known, known_legit),
                    **detectors,
                }
                labels = prepared.labels.drop(known + known_legit)  # avalia só nas contas ainda desconhecidas
                scores["combinado"] = _mean_percentile(scores, labels, "propagacao_relativa", "completo_dbscan")
                scores["label_spreading_combinado"] = _mean_percentile(scores, labels, "label_spreading",
                                                                       "completo_dbscan")
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
                  sementes=list(range(1, args.sementes + 1)), conhecidas=args.conhecidas,
                  fracoes=args.fracoes if args.conhecidas == "fracao" else None,
                  duracao_s=round(time.time() - began))
    _plot(summary.loc["average_precision"], args, figures / "propagacao_average_precision.png")

    print("\naverage precision média, só nas contas ainda desconhecidas:")
    print(summary.loc["average_precision", "mean"].droplevel("modelo").unstack(by).round(3).to_string())
    print("\ncomparações pareadas (average precision):")
    columns = ["cenario", "conhecidas", "comparação", "diferença média", "a vence em", "p Wilcoxon (Holm)"]
    print(comparisons[comparisons["métrica"] == "average_precision"][columns].round(4).to_string(index=False))


def _known_frauds(args, rng, fraud, tx):
    """As fraudes tratadas como conhecidas: ``(rótulo, contas)`` para cada nível avaliado."""
    if args.conhecidas == "fracao":
        for fraction in args.fracoes:
            yield fraction, list(rng.choice(fraud, size=max(1, round(fraction * len(fraud))), replace=False))
        return
    if "contestado_em" not in tx:
        raise SystemExit("--conhecidas contestacao precisa de um cenário com p_contested > 0 (coluna contestado_em)")
    contested = tx[tx["contestado_em"].notna() & (tx["contestado_em"] <= tx["timestamp"].max())]
    known = sorted(set(contested["receiver"]) & set(fraud))
    if known:
        yield CONTESTED, known


def _mean_percentile(scores: dict, labels: pd.Series, *methods: str) -> pd.Series:
    """Combinação de métodos: média dos percentis de cada um, nas contas avaliadas."""
    return sum(scores[m].reindex(labels.index).rank(pct=True) for m in methods) / len(methods)


def _known_label(level) -> str:
    return "contestações" if level == CONTESTED else f"{level:.0%} conhecidas"


def _scores(prepared, feature_set: str, model: str, models: dict) -> pd.Series:
    """Escore de um detector não supervisionado (não usa as contas conhecidas)."""
    return DETECTORS[model](prepared.features[FEATURE_SETS[feature_set]], **models.get(model, {})).scores


def _plot(summary: pd.DataFrame, args, path: Path) -> None:
    """Matriz método × (cenário, fração conhecida) da AP média."""
    mean = summary["mean"].droplevel("modelo")
    levels = args.fracoes if args.conhecidas == "fracao" else [CONTESTED]
    columns = [(c, f) for c in args.cenarios for f in levels]
    matrix = pd.DataFrame({f"{c}\n{_known_label(f)}": [mean.get((c, f, m), np.nan) for m in METHODS]
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
