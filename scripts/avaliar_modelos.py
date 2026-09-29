"""Vitrine de todos os modelos: qual abordagem funciona, e em qual cenário?

Para cada cenário e semente, gera o dataset e avalia quatro famílias de modelos
**nas mesmas contas**, para os números serem comparáveis entre elas:

* **não supervisionados** (``pixfraud.anomaly.DETECTORS``), no conjunto de
  atributos ``--conjunto`` (padrão: ``completo``);
* **estrutura do grafo** (``pixfraud.graph_models.GRAPH_DETECTORS``): FRAUDAR e
  node2vec, que não usam a tabela de atributos;
* **semi-supervisionados**: parte das fraudes já é conhecida e 25% das contas
  legítimas também. No cenário com a coluna ``contestado_em``, as fraudes
  conhecidas são as contestadas até o fim do período, como no MED; nos demais,
  são 25% sorteadas. Os métodos são o PageRank relativo, o label spreading e a
  combinação de cada um com o DBSCAN;
* **tetos supervisionados**, treinados com os rótulos em validação cruzada:
  Random Forest, gradient boosting e, com o extra ``gnn``, a GraphSAGE.

As contas conhecidas, fraudes ou legítimas, ficam fora da avaliação de
**todos** os modelos. As comparações pareadas (``stats.compare_runs`` com
``between="modelo"``) usam o DBSCAN como referência e confrontam as variantes
de cada família.

Saídas em reports/results/:
    modelos_execucoes.csv    uma linha por (cenário, semente, modelo)
    modelos_resumo.csv       média, desvio e IC 95% de cada métrica
    modelos_comparacoes.csv  diferenças pareadas entre modelos
    modelos_meta.json        como o resultado foi gerado
e as figuras reports/figures/modelos_average_precision.png e modelos_comparacoes.png.

Uso:
    python scripts/avaliar_modelos.py --sementes 20 --processos 3
    python scripts/avaliar_modelos.py --cenarios realista --sementes 2 --sem-gnn
    python scripts/avaliar_modelos.py --so-figuras    # redesenha as figuras a partir dos CSVs
"""

import argparse
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud import gnn  # noqa: E402
from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.evaluation import ranking_metrics  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    SUPERVISED_MODELS,
    load_experiment_config,
    load_scenarios,
    prepare,
    save_metadata,
    seeded_models,
    supervised_scores,
)
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.flow import label_spreading, propagate_risk  # noqa: E402
from pixfraud.graph_models import GRAPH_DETECTORS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, SURFACE, plot_differences, plot_model_intervals  # noqa: E402

FAMILIES = {
    "não supervisionado": list(DETECTORS),
    "estrutura do grafo": list(GRAPH_DETECTORS),
    "semi-supervisionado": ["propagacao_relativa", "label_spreading", "combinado", "label_spreading_combinado"],
    "teto supervisionado": [*SUPERVISED_MODELS, "graphsage"],
}
FAMILY_OF = {model: family for family, models in FAMILIES.items() for model in models}
ORDER = [model for models in FAMILIES.values() for model in models]
REFERENCE = "dbscan"
COMPARISONS = [
    *[(m, REFERENCE) for m in [*DETECTORS, *GRAPH_DETECTORS] if m != REFERENCE],
    ("label_spreading", "propagacao_relativa"),
    ("combinado", REFERENCE),
    ("label_spreading_combinado", "combinado"),
    ("random_forest", REFERENCE),
    ("gradient_boosting", "random_forest"),
    ("graphsage", "random_forest"),
]
METRICS = ["average_precision", "precision_at_k", "roc_auc"]
KNOWN_FRACTION = 0.25


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara todos os modelos nas mesmas contas.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["base", "realista", "calibrado"])
    parser.add_argument("--sementes", type=int, default=20)
    parser.add_argument("--conjunto", default="completo", choices=list(FEATURE_SETS),
                        help="atributos dos modelos que usam a tabela de atributos")
    parser.add_argument("--processos", type=int, default=1, help="sementes rodando ao mesmo tempo (memória!)")
    parser.add_argument("--sem-gnn", action="store_true", help="não roda a GraphSAGE mesmo se estiver instalada")
    parser.add_argument("--saida", default="reports")
    parser.add_argument("--so-figuras", action="store_true", help="só redesenha as figuras a partir dos CSVs")
    args = parser.parse_args()
    began = time.time()
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"

    if args.so_figuras:
        runs = pd.read_csv(results / "modelos_execucoes.csv")
        summary = pd.read_csv(results / "modelos_resumo.csv", index_col=[0, 1, 2, 3])
        comparisons = pd.read_csv(results / "modelos_comparacoes.csv")
        names = list(dict.fromkeys(runs["cenario"]))
    else:
        config = load_experiment_config(args.config)
        base = load_config(args.config)
        scenarios = load_scenarios(args.arquivo_cenarios)
        names = args.cenarios
        unknown = [n for n in names if n not in scenarios]
        if unknown:
            parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
        use_gnn = gnn.available() and not args.sem_gnn
        if not use_gnn and not args.sem_gnn:
            print("aviso: sem o extra 'gnn' (PyTorch Geometric), a GraphSAGE fica de fora", flush=True)
        jobs = [(with_overrides(base, scenarios[n]), n, seed, config, args.conjunto, use_gnn)
                for n in names for seed in range(1, args.sementes + 1)]
        rows = []
        if args.processos > 1:
            with ProcessPoolExecutor(max_workers=args.processos) as pool:
                for job, done in zip(jobs, pool.map(_evaluate_star, jobs)):
                    rows += done
                    print(f"{job[1]}: semente {job[2]}/{args.sementes} concluída", flush=True)
        else:
            for job in jobs:
                rows += _evaluate(*job)
                print(f"{job[1]}: semente {job[2]}/{args.sementes} concluída", flush=True)
        runs = pd.DataFrame(rows)
        summary = pd.concat({m: summarize_runs(runs, m, by=["cenario"]) for m in METRICS}, names=["métrica"])
        comparisons = compare_runs(runs, COMPARISONS, METRICS, by=["cenario"], between="modelo")
        results.mkdir(parents=True, exist_ok=True)
        runs.to_csv(results / "modelos_execucoes.csv", index=False)
        summary.to_csv(results / "modelos_resumo.csv")
        comparisons.to_csv(results / "modelos_comparacoes.csv", index=False)
        save_metadata(results / "modelos_meta.json", config, cenarios={n: scenarios[n] for n in names},
                      sementes=list(range(1, args.sementes + 1)), conjunto=args.conjunto,
                      modelos=sorted(set(runs["modelo"])), processos=args.processos,
                      duracao_s=round(time.time() - began))

    figures.mkdir(parents=True, exist_ok=True)
    rate = runs.groupby("cenario")["taxa_fraude"].mean()
    n_seeds = runs["semente"].nunique()
    _plot_models(summary, names, rate, n_seeds, figures / "modelos_average_precision.png")
    _plot_comparisons(comparisons, names, n_seeds, figures / "modelos_comparacoes.png")

    table = summary.loc["average_precision", "mean"].droplevel("atributos").unstack("cenario")[names]
    print("\naverage precision média (mesmas contas para todos os modelos):")
    print(table.reindex([m for m in ORDER if m in table.index]).round(3).to_string())


def _evaluate_star(job):
    return _evaluate(*job)


def _evaluate(simulation, name, seed, config, conjunto, use_gnn) -> list[dict]:
    """Todas as famílias numa semente, avaliadas nas mesmas contas (as que ninguém conhece)."""
    accounts, tx = generate_dataset(replace(simulation, seed=seed))
    prepared = prepare(accounts, tx, config)
    models = seeded_models(config["modelos"], seed)
    labels = prepared.labels
    fraud, legit = labels.index[labels], labels.index[~labels]
    rng = np.random.default_rng([seed, 2])
    known, how = [], f"{KNOWN_FRACTION:.0%} sorteadas"
    if "contestado_em" in tx:
        contested = tx[tx["contestado_em"].notna() & (tx["contestado_em"] <= tx["timestamp"].max())]
        known, how = sorted(set(contested["receiver"]) & set(fraud)), "contestações"
    if not known:
        known = list(rng.choice(fraud, size=max(1, round(KNOWN_FRACTION * len(fraud))), replace=False))
    known_legit = list(rng.choice(legit, size=round(KNOWN_FRACTION * len(legit)), replace=False))
    evaluated = labels.drop(known + known_legit)

    columns = FEATURE_SETS[conjunto]
    scores = {m: detect(prepared.features[columns], **models.get(m, {})).scores for m, detect in DETECTORS.items()}
    scores |= {m: detect(prepared.graph, **models.get(m, {})).scores for m, detect in GRAPH_DETECTORS.items()}
    scores["propagacao_relativa"] = propagate_risk(prepared.graph, known, relative=True)
    scores["label_spreading"] = label_spreading(prepared.graph, known, known_legit)

    def percentile(model):
        return scores[model].reindex(evaluated.index).rank(pct=True)

    scores["combinado"] = (percentile("propagacao_relativa") + percentile(REFERENCE)) / 2
    scores["label_spreading_combinado"] = (percentile("label_spreading") + percentile(REFERENCE)) / 2
    for model in SUPERVISED_MODELS:
        scores[model] = supervised_scores(prepared.features[columns], labels, seed=seed, model=model)
    if use_gnn:
        scores["graphsage"] = gnn.graphsage_scores(prepared.graph, prepared.features[columns], labels, seed=seed)

    common = {"cenario": name, "semente": seed, "atributos": "vitrine", "taxa_fraude": float(evaluated.mean()),
              "fraudes_avaliadas": int(evaluated.sum()), "contas_avaliadas": len(evaluated),
              "fraudes_conhecidas": len(known), "conhecidas": how}
    return [{**common, "modelo": model, "familia": FAMILY_OF[model],
             "conjunto": "-" if FAMILY_OF[model] == "estrutura do grafo" else conjunto,
             **ranking_metrics(evaluated, score)}
            for model, score in scores.items()]


def _plot_models(summary: pd.DataFrame, names: list, rate: pd.Series, n: int, path: Path) -> None:
    """Um painel por cenário: cada modelo com a AP média e o IC 95%, agrupados por família."""
    ap = summary.loc["average_precision"].droplevel("atributos")
    present = set(ap.index.get_level_values("modelo"))
    order = [m for m in ORDER if m in present]
    fig, axes = plt.subplots(1, len(names), figsize=(1.8 + 3.6 * len(names), 1.2 + 0.32 * len(order)),
                             sharey=True, squeeze=False, layout="constrained")
    for i, (ax, scenario) in enumerate(zip(axes[0], names)):
        plot_model_intervals(ap.loc[scenario].reindex(order), ax, baseline=rate[scenario], groups=FAMILY_OF,
                             group_labels=i == len(names) - 1)
        ax.set_title(scenario, color=INK, fontsize=10, loc="left")
    fig.suptitle(f"Todos os modelos nas mesmas contas: average precision média e IC 95% ({n} sementes)",
                 color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def _plot_comparisons(comparisons: pd.DataFrame, names: list, n: int, path: Path) -> None:
    """Um painel por cenário: as diferenças pareadas de AP entre modelos."""
    ap = comparisons[comparisons["métrica"] == "average_precision"]
    height = 0.3 * ap.groupby("cenario").size().max() + 1.0
    fig, axes = plt.subplots(len(names), 1, figsize=(9.5, 0.6 + height * len(names)), squeeze=False,
                             layout="constrained")
    for ax, scenario in zip(axes[:, 0], names):
        plot_differences(ap[ap["cenario"] == scenario], ax)
        ax.set_title(scenario, color=INK, fontsize=10, loc="left")
    fig.suptitle(f"Comparações pareadas entre modelos ({n} sementes)\n"
                 "verde: A melhor · vermelho: B melhor · cinza: sem diferença (p de Holm ≥ 0,05)",
                 color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
