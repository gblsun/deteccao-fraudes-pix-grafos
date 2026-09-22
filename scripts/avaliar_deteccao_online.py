"""Avalia a detecção ao longo do tempo: a quadrilha é sinalizada a tempo de bloquear o dinheiro?

Para cada cenário e semente, gera o dataset e roda os detectores a cada
--frequencia, vendo só os Pix feitos até cada ponto de corte. A cada corte, um
analista revisa as k contas mais suspeitas (k = nº de contas fraudulentas).
Depois reproduz os Pix da quadrilha, bloqueando cada conta no corte em que ela
foi sinalizada (ver pixfraud.online).

Métricas por (cenário, semente, atributos, modelo):
    detectadas_72h     fração das contas fraudulentas sinalizadas até --horizonte depois
                       do primeiro golpe que receberam
    atraso_mediano_h   atraso mediano (horas) até a sinalização, entre as detectadas
    recuperado_<prazo> fração do dinheiro roubado que ficou retida em contas bloqueadas,
                       supondo que o dinheiro parado numa conta da quadrilha é sacado
                       depois de <prazo>. Há um valor para cada prazo de --saque,
                       porque essa premissa pesa muito no resultado.
A linha "oráculo" sinaliza cada conta fraudulenta no primeiro corte depois da
exposição: é o teto imposto só pela frequência dos cortes.

Saídas: reports/results/online_execucoes.csv, online_resumo.csv e
online_comparacoes.csv, e a figura reports/figures/online_deteccao.png. As
sinalizações de cada cenário e semente ficam em reports/results/online_cortes/
e são reaproveitadas se o script rodar de novo (--refazer recalcula).

Uso:
    python scripts/avaliar_deteccao_online.py --sementes 3
    python scripts/avaliar_deteccao_online.py --cenarios realista --sementes 1 --frequencia 12h
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

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import COMPARISONS, load_experiment_config, load_scenarios  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.online import (  # noqa: E402
    checkpoint_flags,
    exposure_times,
    first_flags,
    recovered_amount,
    relevant_checkpoints,
)
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import compare_runs, summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

ORACLE = "oráculo"


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia se a detecção acontece a tempo de bloquear o dinheiro.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["sem_atalhos", "realista"])
    parser.add_argument("--sementes", type=int, default=3)
    parser.add_argument("--conjuntos", nargs="+", default=["tabular", "grafo", "temporal", "completo"],
                        choices=list(FEATURE_SETS))
    parser.add_argument("--frequencia", default="6h", help="intervalo entre os pontos de corte")
    parser.add_argument("--horizonte", default="72h", help="prazo para a detecção contar (bloqueio cautelar)")
    parser.add_argument("--saque", nargs="+", default=["1h", "6h", "24h"],
                        help="tempos até o dinheiro parado ser sacado (um resultado para cada)")
    parser.add_argument("--saida", default="reports")
    parser.add_argument("--refazer", action="store_true", help="recalcula as sinalizações já salvas")
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    feature_sets = {s: FEATURE_SETS[s] for s in args.conjuntos}
    horizon = pd.Timedelta(args.horizonte)
    metrics = ["detectadas_72h", "atraso_mediano_h"] + [f"recuperado_{c}" for c in args.saque]
    # As sinalizações (a parte cara) de cada cenário e semente são salvas assim que
    # ficam prontas; ao rodar de novo, são reaproveitadas.
    cache = Path(args.saida) / "results" / "online_cortes"
    cache.mkdir(parents=True, exist_ok=True)

    rows = []
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            began = time.time()
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            fraud = accounts.loc[accounts["is_fraud"], "account_id"]
            exposure = exposure_times(tx, fraud)
            checkpoints = relevant_checkpoints(exposure, args.frequencia, args.horizonte)
            flags_file = cache / f"{name}_semente{seed}_{args.frequencia}_{args.horizonte}.csv"
            flags = None
            if flags_file.exists() and not args.refazer:
                flags = pd.read_csv(flags_file, parse_dates=["corte"])
                if not set(feature_sets) <= set(flags["atributos"]):
                    flags = None  # salvo sem algum dos conjuntos pedidos: recalcula
            if flags is None:
                run_config = copy.deepcopy(config)
                run_config["modelos"].setdefault("isolation_forest", {})["seed"] = seed
                flags = checkpoint_flags(accounts, tx, run_config, checkpoints, k=len(fraud),
                                         feature_sets=feature_sets)
                flags.to_csv(flags_file, index=False)
            flags = flags[flags["atributos"].isin(feature_sets)]

            ids = {"cenario": name, "semente": seed}
            for (set_name, model), group in flags.groupby(["atributos", "modelo"], sort=False):
                first = first_flags(group, exposure)
                rows.append({**ids, "atributos": set_name, "modelo": model,
                             **_metrics(first, exposure, tx, fraud, horizon, args.saque)})
            oracle = exposure.map(lambda e: checkpoints[checkpoints >= e].min())
            rows.append({**ids, "atributos": ORACLE, "modelo": ORACLE,
                         **_metrics(oracle, exposure, tx, fraud, horizon, args.saque)})
            print(f"{name}: semente {seed}/{args.sementes}, {len(checkpoints)} cortes, "
                  f"{time.time() - began:.0f} s", flush=True)

    runs = pd.DataFrame(rows)
    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "online_execucoes.csv", index=False)
    summary = pd.concat({m: summarize_runs(runs, m, by=["cenario"]) for m in metrics}, names=["métrica"])
    summary.to_csv(results / "online_resumo.csv")
    pairs = [(a, b) for a, b in COMPARISONS if a in feature_sets and b in feature_sets]
    if pairs and args.sementes > 1:
        paired = [m for m in metrics if m != "atraso_mediano_h"]
        comparisons = compare_runs(runs[runs["atributos"] != ORACLE], pairs, paired, by=["cenario"])
        comparisons.to_csv(results / "online_comparacoes.csv", index=False)
    _plot(summary, args.cenarios, list(feature_sets), figures / "online_deteccao.png", args)

    for metric in metrics:
        print(f"\n{metric} (média):")
        print(summary.loc[metric, "mean"].unstack("cenario")[args.cenarios].round(3).to_string())


def _metrics(first: pd.Series, exposure: pd.Series, tx: pd.DataFrame, fraud, horizon: pd.Timedelta,
             cashouts: list[str]) -> dict:
    delay = first - exposure
    in_time = delay <= horizon
    recovered = {c: recovered_amount(tx, fraud, first, cashout=c) for c in cashouts}
    return {
        "detectadas_72h": float(in_time.mean()),
        "atraso_mediano_h": float(delay[in_time].dt.total_seconds().median() / 3600) if in_time.any() else np.nan,
        **{f"recuperado_{c}": r["fracao_recuperada"] for c, r in recovered.items()},
        "roubado": next(iter(recovered.values()))["roubado"],
        "contas_fraudulentas": len(exposure),
    }


def _plot(summary: pd.DataFrame, names: list, sets: list, path: Path, args) -> None:
    """Painéis modelo × métrica; em cada um, conjunto de atributos (e oráculo) × cenário."""
    models = list(DETECTORS)
    panels = [("detectadas_72h", f"detectadas em {args.horizonte}")]
    panels += [(f"recuperado_{c}", f"recuperado, saque em {c}") for c in dict.fromkeys([args.saque[0], args.saque[-1]])]
    rows = [*sets, ORACLE]
    fig, axes = plt.subplots(len(models), len(panels), figsize=(2.2 + 1.5 * len(names) * len(panels),
                                                                 1.3 + 2.4 * len(models)),
                             sharex=True, sharey=True, layout="constrained", squeeze=False)
    for i, model in enumerate(models):
        for j, (metric, label) in enumerate(panels):
            mean = summary.loc[metric, "mean"]
            matrix = pd.DataFrame(
                {c: [mean.get((c, s, model), mean.get((c, s, ORACLE), np.nan)) for s in rows] for c in names},
                index=rows,
            )
            mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=1, fmt="{:.0%}", ax=axes[i, j])
            if i == 0:
                axes[i, j].set_title(label, color=INK, fontsize=9, loc="left")
        axes[i, 0].set_ylabel(model.replace("_", " "), color=INK, fontsize=10)
    colorbar = fig.colorbar(mesh, ax=axes, shrink=0.6, pad=0.02)
    colorbar.set_label("fração (média das sementes)", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    title = (f"Detecção a tempo: cortes a cada {args.frequencia}, k = nº de contas fraudulentas\n"
             "oráculo = sinaliza toda conta fraudulenta no primeiro corte possível")
    fig.suptitle(title, color=INK, fontsize=10)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
