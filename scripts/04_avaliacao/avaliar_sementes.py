"""Quantas sementes bastam? Convergência da average precision média.

Pedido da reunião de 24/09: os estudos de robustez usam 10 sementes por chave
(atributos, modelo); a pergunta é se a média da average precision (AP) muda
com 100, 500 ou 1000 sementes. O script roda o experimento de
``avaliar_robustez.py`` com muitas sementes e mede, para cada chave:

* a média, o desvio e o IC 95% da AP usando só as primeiras ``n`` sementes,
  para cada ``n`` de ``--marcos`` (10, 100, 500, 1000);
* quanto a média de **10 sementes sorteadas** varia em torno da média com
  todas as sementes (faixa de 95% em ``--sorteios`` sorteios sem reposição);
* com que frequência 10 sementes elegem a mesma melhor chave que todas;
* para cada comparação pareada de ``experiment.COMPARISONS`` (ex.: completo -
  tabular), a diferença média, o desvio das diferenças e quantas sementes um
  teste pareado precisa para detectar essa diferença com poder de 80%.

Cada semente é gravada assim que termina, então dá para interromper e rodar
de novo: as sementes que já estão no CSV são puladas.

Saídas em reports/04_avaliacao/results/:
    sementes_execucoes.csv     uma linha por (semente, atributos, modelo)
    sementes_convergencia.csv  média, desvio e IC 95% da AP para cada marco
    sementes_sorteios.csv      variação da média de 10 sementes sorteadas
    sementes_pareadas.csv      sementes necessárias para cada comparação pareada
    sementes_meta.json         como o resultado foi gerado
e a figura reports/04_avaliacao/figures/sementes_convergencia.png.

Uso:
    python scripts/04_avaliacao/avaliar_sementes.py --sementes 1000 --processos 4
    python scripts/04_avaliacao/avaliar_sementes.py --cenario realista --sementes 100
    python scripts/04_avaliacao/avaliar_sementes.py --so-analise    # refaz tabelas e figura a partir do CSV
"""

import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import (  # noqa: E402
    COMPARISONS,
    load_experiment_config,
    load_scenarios,
    run_seeds,
    save_metadata,
)
from pixfraud.simulation import load_config, with_overrides  # noqa: E402
from pixfraud.stats import summarize_runs  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SURFACE  # noqa: E402

METRIC = "average_precision"
KEY = ["atributos", "modelo"]
# Cores categóricas em ordem fixa (validadas para daltonismo); rótulo direto no fim de cada linha.
MODEL_COLORS = {"dbscan": "#2a78d6", "isolation_forest": "#eb6834", "local_outlier_factor": "#1baf7a"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convergência da AP média com o número de sementes.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenario", default="base", help="cenário de configs/cenarios.yaml")
    parser.add_argument("--sementes", type=int, default=1000, help="sementes 1, 2, ..., N")
    parser.add_argument("--processos", type=int, default=1, help="sementes rodando ao mesmo tempo")
    parser.add_argument("--modelos", nargs="+", default=list(MODEL_COLORS), choices=sorted(DETECTORS),
                        help="detectores (padrão: os 3 das 1000 sementes salvas, para a retomada continuar comparável)")
    parser.add_argument("--marcos", nargs="+", type=int, default=[10, 100, 500, 1000])
    parser.add_argument("--sorteios", type=int, default=2000, help="nº de sorteios de --tamanho-sorteio sementes")
    parser.add_argument("--tamanho-sorteio", type=int, default=10, help="sementes por sorteio (hoje, 10)")
    parser.add_argument("--atributos-figura", default="completo", help="conjunto de atributos da figura")
    parser.add_argument("--saida", default="reports/04_avaliacao")
    parser.add_argument("--so-analise", action="store_true", help="não roda sementes novas")
    args = parser.parse_args()
    began = time.time()

    results = Path(args.saida) / "results"
    figures = Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs_path = results / f"sementes_execucoes{_suffix(args.cenario)}.csv"

    config = load_experiment_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    if args.cenario not in scenarios:
        parser.error(f"cenário desconhecido: {args.cenario} (existem: {', '.join(scenarios)})")
    simulation = with_overrides(load_config(args.config), scenarios[args.cenario])

    if not args.so_analise:
        done = set(pd.read_csv(runs_path)["semente"]) if runs_path.exists() else set()
        todo = [s for s in range(1, args.sementes + 1) if s not in done]
        print(f"{len(done)} sementes já no CSV; faltam {len(todo)}", flush=True)
        _run(simulation, config, todo, args.processos, args.modelos, runs_path)

    runs = pd.read_csv(runs_path)
    runs = runs[runs["semente"] <= args.sementes]
    n_total = runs["semente"].nunique()
    marks = sorted({m for m in args.marcos if m < n_total} | {n_total})

    convergence = _convergence(runs, marks)
    size = min(args.tamanho_sorteio, n_total - 1)
    draws, same_best = _draws(runs, args.sorteios, size)
    suffix = _suffix(args.cenario)
    convergence.to_csv(results / f"sementes_convergencia{suffix}.csv", index=False)
    draws.to_csv(results / f"sementes_sorteios{suffix}.csv", index=False)
    paired = _paired_needs(runs)
    paired.to_csv(results / f"sementes_pareadas{suffix}.csv", index=False)
    save_metadata(results / f"sementes_meta{suffix}.json", config, cenario=args.cenario,
                  sementes=n_total, marcos=marks, sorteios=args.sorteios,
                  tamanho_sorteio=size, mesma_melhor_chave=same_best,
                  processos=args.processos, duracao_s=round(time.time() - began))
    _plot(convergence, args.atributos_figura, figures / f"sementes_convergencia{suffix}.png", args.cenario)

    print(f"\n{n_total} sementes, cenário {args.cenario}")
    print("\nAP média e meia-largura do IC 95% em cada marco:")
    table = convergence.pivot_table(index=KEY, columns="n", values=["mean", "meia_largura"])
    print(table.round(4).to_string())
    print(f"\nmédia de {size} sementes sorteadas × média com todas:")
    print(draws.round(4).to_string(index=False))
    print(f"\n{size} sementes elegem a mesma melhor chave que todas em {same_best:.0%} dos sorteios")
    print("\ncomparações pareadas: sementes para detectar a diferença (poder de 80%, alfa 5%):")
    print(paired.round(4).to_string(index=False))


def _paired_needs(runs: pd.DataFrame, power: float = 0.8, alpha: float = 0.05) -> pd.DataFrame:
    """Diferença pareada média de cada comparação e o nº de sementes para detectá-la.

    Menor $n$ com $\\sqrt n \\, |\\bar d| / s \\geq t_{1-\\alpha/2,\\,n-1} + t_{poder,\\,n-1}$
    (poder do teste t pareado), em que $\\bar d$ e $s$ são a média e o desvio das
    diferenças por semente, estimados com todas as sementes. O mínimo é 6: com
    menos, o Wilcoxon exato bilateral (usado em ``stats.compare_runs``) não
    chega a p < 0,05. ``a_vence_em`` é a fração das sementes em que o primeiro
    conjunto tem AP maior.
    """
    wide = runs.pivot_table(index="semente", columns=KEY, values=METRIC)
    rows = []
    for a, b in COMPARISONS:
        for model in sorted(runs["modelo"].unique()):
            diff = wide[(a, model)] - wide[(b, model)]
            mean, sd = diff.mean(), diff.std()
            rows.append({
                "comparacao": f"{a} - {b}", "modelo": model,
                "diferenca_media": mean, "desvio_das_diferencas": sd,
                "a_vence_em": float((diff > 0).mean()),
                "sementes_necessarias": _seeds_for_power(abs(mean) / sd, power, alpha),
            })
    return pd.DataFrame(rows)


def _seeds_for_power(effect: float, power: float, alpha: float, minimum: int = 6, maximum: int = 100_000):
    """Menor nº de sementes para um teste t pareado detectar o efeito padronizado ``effect``."""
    if not np.isfinite(effect) or effect == 0:
        return np.nan
    for n in range(minimum, maximum + 1):
        if np.sqrt(n) * effect >= stats.t.ppf(1 - alpha / 2, n - 1) + stats.t.ppf(power, n - 1):
            return n
    return np.nan


def _suffix(scenario: str) -> str:
    return "" if scenario == "base" else f"_{scenario}"


def _one_seed(simulation, config, seed: int, models: list[str]) -> pd.DataFrame:
    """Roda uma semente (em outro processo, com ``--processos`` > 1)."""
    (_, _, metrics), = run_seeds(simulation, config, [seed], models=models)
    return metrics


def _run(simulation, config, seeds: list[int], processes: int, models: list[str], path: Path) -> None:
    """Roda ``seeds`` e acrescenta cada resultado ao CSV assim que fica pronto."""
    began = time.time()

    def save(metrics: pd.DataFrame, i: int) -> None:
        metrics.to_csv(path, mode="a", header=not path.exists(), index=False)
        per_seed = (time.time() - began) / i
        eta = per_seed * (len(seeds) - i) / 60
        print(f"semente {int(metrics['semente'].iloc[0])} ok ({i}/{len(seeds)}, "
              f"{per_seed:.1f} s/semente, faltam ~{eta:.0f} min)", flush=True)

    if processes <= 1:
        for i, seed in enumerate(seeds, 1):
            save(_one_seed(simulation, config, seed, models), i)
        return
    with ProcessPoolExecutor(max_workers=processes) as pool:
        futures = [pool.submit(_one_seed, simulation, config, s, models) for s in seeds]
        for i, future in enumerate(as_completed(futures), 1):
            save(future.result(), i)


def _convergence(runs: pd.DataFrame, marks: list[int]) -> pd.DataFrame:
    """Média, desvio e IC 95% da AP usando só as sementes 1..n, para cada marco n."""
    tables = []
    for n in marks:
        summary = summarize_runs(runs[runs["semente"] <= n], METRIC).reset_index()
        summary["meia_largura"] = (summary["ic_superior"] - summary["ic_inferior"]) / 2
        tables.append(summary.assign(n=n))
    return pd.concat(tables, ignore_index=True)


def _draws(runs: pd.DataFrame, n_draws: int, size: int = 10, seed: int = 0) -> tuple[pd.DataFrame, float]:
    """Quanto a média de ``size`` sementes sorteadas se afasta da média com todas as sementes.

    Devolve a tabela por chave e a fração dos sorteios em que a melhor chave
    (maior AP média) é a mesma que com todas as sementes.
    """
    wide = runs.pivot_table(index="semente", columns=KEY, values=METRIC)
    rng = np.random.default_rng(seed)
    idx = np.array([rng.choice(len(wide), size=size, replace=False) for _ in range(n_draws)])
    values = wide.to_numpy()
    means = values[idx].mean(axis=1)  # sorteios × chaves
    full = values.mean(axis=0)
    best_full = int(np.argmax(full))
    rows = []
    for j, key in enumerate(wide.columns):
        deviation = means[:, j] - full[j]
        rows.append({
            "atributos": key[0], "modelo": key[1],
            f"media_{len(wide)}_sementes": full[j],
            "faixa95_inferior": full[j] + np.quantile(deviation, 0.025),
            "faixa95_superior": full[j] + np.quantile(deviation, 0.975),
            "desvio_absoluto_mediano": float(np.median(np.abs(deviation))),
        })
    table = pd.DataFrame(rows).sort_values(f"media_{len(wide)}_sementes", ascending=False)
    return table, float((means.argmax(axis=1) == best_full).mean())


def _plot(convergence: pd.DataFrame, feature_set: str, path: Path, scenario: str) -> None:
    """Dois painéis: AP média com IC 95% e meia-largura do IC, ambos contra o nº de sementes."""
    data = convergence[convergence["atributos"] == feature_set]
    fig, (left, right) = plt.subplots(1, 2, figsize=(10, 4.2), facecolor=SURFACE)
    for model, group in data.groupby("modelo"):
        color = MODEL_COLORS.get(model, INK_SECONDARY)
        group = group.sort_values("n")
        left.fill_between(group["n"], group["ic_inferior"], group["ic_superior"], color=color, alpha=0.18, lw=0)
        left.plot(group["n"], group["mean"], color=color, lw=2, marker="o", ms=5)
        right.plot(group["n"], group["meia_largura"], color=color, lw=2, marker="o", ms=5,
                   label=model.replace("_", " "))
        left.annotate(model.replace("_", " "), (group["n"].iloc[-1], group["mean"].iloc[-1]), xytext=(6, 0),
                      textcoords="offset points", va="center", fontsize=8, color=INK)
    first = data.sort_values("n").groupby("modelo").first()
    n0 = data["n"].min()
    ns = np.array(sorted(data["n"].unique()))
    reference = first["meia_largura"].max() * 1.3 * np.sqrt(n0 / ns)
    right.plot(ns, reference, color=INK_SECONDARY, lw=1, ls="--", label="referência ∝ 1/√n")
    right.set_yscale("log")  # em log-log, 1/√n é uma reta de inclinação -1/2
    right.legend(frameon=False, fontsize=8, labelcolor=INK)
    left.set_ylabel("average precision média (IC 95%)", color=INK)
    right.set_ylabel("meia-largura do IC 95% (escala log)", color=INK)
    for ax in (left, right):
        ax.set_xscale("log")
        ax.set_xlabel("nº de sementes", color=INK)
        ax.set_facecolor(SURFACE)
        ax.grid(alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=INK_SECONDARY)
        ax.set_xlim(right=ns[-1] * 2.2)
    fig.suptitle(f"Convergência da AP média — atributos '{feature_set}', cenário '{scenario}'", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
