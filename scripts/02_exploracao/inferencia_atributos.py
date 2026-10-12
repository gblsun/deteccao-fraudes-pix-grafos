"""Inferência sobre os atributos, antes dos modelos: o que distingue as contas fraudulentas?

Etapa 2 do fluxo da pesquisa (ver docs/plano-de-testes-estatisticos.md). Roda
nas **sementes de validação** (1001, 1002...), as mesmas da otimização dos
hiperparâmetros, para não tocar nas redes de teste (sementes 1 a 10).

Para cada cenário e semente:

* **fraude × legítima** (2 grupos): Mann-Whitney com delta de Cliff e Holm
  (``stats.compare_groups``);
* **entre os 6 papéis** (normal, comércio, vítima, laranja, intermediário,
  coletor): Kruskal-Wallis com ε² e Holm (``stats.kruskal_groups``) e, nos
  atributos com efeito pelo menos médio na primeira semente, o teste de Dunn
  para saber que pares de papéis diferem (``stats.dunn_posthoc``);
* **variáveis categóricas × fraude** (conta de empresa, conta nova, recebeu Pix
  de madrugada): qui-quadrado, Fisher exato e razão de chances
  (``stats.contingency_test``).

O resumo diz, para cada atributo, o efeito médio entre as sementes e em quantas
delas o teste deu significativo depois do Holm: um efeito que só aparece numa
semente não é um efeito.

Saídas em reports/02_exploracao/results/:
    inferencia_fraude.csv        (cenário, atributo): delta de Cliff médio, IC 95% e sementes significativas
    inferencia_papeis.csv        (cenário, atributo): ε² médio, IC 95%, sementes significativas e papel de maior mediana
    inferencia_dunn.csv          (cenário, atributo, par de papéis): z, p de Holm, na primeira semente
    inferencia_categoricas.csv   (cenário, variável): V de Cramér, razão de chances e sementes significativas
    inferencia_execucoes.csv     uma linha por (cenário, semente, teste, atributo): tudo o que foi calculado
    inferencia_meta.json         como o resultado foi gerado
e a figura reports/02_exploracao/figures/inferencia_papeis.png (ε² atributo × cenário).

Uso:
    python scripts/02_exploracao/inferencia_atributos.py
    python scripts/02_exploracao/inferencia_atributos.py --cenarios calibrado --sementes 5
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
from scipy import stats as sps  # noqa: E402

from pixfraud.experiment import load_experiment_config, load_scenarios, prepare, save_metadata  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.stats import (  # noqa: E402
    compare_groups,
    contingency_test,
    dunn_posthoc,
    effect_size_label,
    epsilon_squared_label,
    holm_correction,
    kruskal_groups,
)
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, plot_value_matrix  # noqa: E402

FIRST_VALIDATION_SEED = 1001  # as mesmas redes de validação de otimizar_hiperparametros.py
ALPHA = 0.05
NEW_ACCOUNT_DAYS = 30
NIGHT_HOURS = range(0, 6)


def main() -> None:
    parser = argparse.ArgumentParser(description="Testes de hipótese sobre os atributos, nas sementes de validação.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["realista", "negativos_dificeis", "calibrado", "aleatorio"])
    parser.add_argument("--sementes", type=int, default=5, help="sementes de validação: 1001, 1002, ...")
    parser.add_argument("--saida", default="reports/02_exploracao")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    seeds = list(range(FIRST_VALIDATION_SEED, FIRST_VALIDATION_SEED + args.sementes))

    rows, dunn = [], []
    for name in args.cenarios:
        for seed in seeds:
            accounts, tx = generate_dataset(replace(with_overrides(base, scenarios[name]), seed=seed))
            prepared = prepare(accounts, tx, config)
            features, labels = prepared.features, prepared.labels
            info = accounts.set_index("account_id")
            roles = info["role"].where(~info["is_victim"], "vitima").reindex(features.index)
            common = {"cenario": name, "semente": seed}

            fraud = compare_groups(features, labels)
            rows += [{**common, "teste": "fraude", "atributo": a, "efeito": r["delta de Cliff"],
                      "p_holm": r["p ajustado (Holm)"]} for a, r in fraud.iterrows()]
            by_role = kruskal_groups(features, roles)
            rows += [{**common, "teste": "papeis", "atributo": a, "efeito": r["ε²"], "p_holm": r["p ajustado (Holm)"],
                      "maior_mediana": r["maior mediana"]} for a, r in by_role.iterrows()]
            for variable, flag in categorical_variables(accounts, tx).items():
                result = contingency_test(labels, flag.reindex(labels.index).fillna(False))
                rows.append({**common, "teste": "categorica", "atributo": variable, "efeito": result["V de Cramér"],
                             "p_holm": result.get("p Fisher", result["p-valor"]),
                             "razao_de_chances": result.get("razão de chances", np.nan)})
            if seed == seeds[0]:
                for attribute in by_role.index[by_role["ε²"] >= 0.06]:
                    pairs = dunn_posthoc(features[attribute], roles)
                    dunn.append(pairs.assign(cenario=name, atributo=attribute))
            print(f"{name}: semente {seed}", flush=True)

    runs = pd.DataFrame(rows)
    # Holm entre as variáveis categóricas de cada (cenário, semente): uma família de testes
    categorical = runs["teste"] == "categorica"
    runs.loc[categorical, "p_holm"] = runs[categorical].groupby(["cenario", "semente"])["p_holm"].transform(
        lambda p: holm_correction(p.to_numpy()))
    summaries = {test: summarize(runs[runs["teste"] == test]) for test in ("fraude", "papeis", "categorica")}
    summaries["fraude"]["rotulo"] = summaries["fraude"]["efeito_medio"].map(effect_size_label)
    summaries["papeis"]["rotulo"] = summaries["papeis"]["efeito_medio"].map(epsilon_squared_label)
    roles_mode = (runs[runs["teste"] == "papeis"].groupby(["cenario", "atributo"])["maior_mediana"]
                  .agg(lambda s: s.mode().iloc[0]))
    summaries["papeis"] = summaries["papeis"].join(roles_mode, on=["cenario", "atributo"])

    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "inferencia_execucoes.csv", index=False)
    summaries["fraude"].to_csv(results / "inferencia_fraude.csv", index=False)
    summaries["papeis"].to_csv(results / "inferencia_papeis.csv", index=False)
    summaries["categorica"].to_csv(results / "inferencia_categoricas.csv", index=False)
    dunn = pd.concat(dunn, ignore_index=True) if dunn else pd.DataFrame()
    dunn.to_csv(results / "inferencia_dunn.csv", index=False)
    save_metadata(results / "inferencia_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=seeds, alfa=ALPHA, duracao_s=round(time.time() - began))
    _plot_roles(summaries["papeis"], args.cenarios, len(seeds), figures / "inferencia_papeis.png")

    print("\natributos que mais separam os papéis (épsilon² médio do Kruskal-Wallis):")
    top = summaries["papeis"].sort_values("efeito_medio", ascending=False).groupby("cenario", sort=False).head(5)
    print(top[["cenario", "atributo", "efeito_medio", "rotulo", "sementes_significativas", "maior_mediana"]]
          .round(3).to_string(index=False))
    print("\nvariáveis categóricas × fraude:")
    print(summaries["categorica"].round(3).to_string(index=False))


def categorical_variables(accounts: pd.DataFrame, tx: pd.DataFrame) -> dict[str, pd.Series]:
    """Variáveis sim/não de cada conta, para cruzar com o gabarito."""
    info = accounts.set_index("account_id")
    night = tx[pd.to_datetime(tx["timestamp"]).dt.hour.isin(NIGHT_HOURS)]
    return {
        "conta_de_empresa": info["account_type"] == "PJ",
        "conta_nova": info["account_age_days"] <= NEW_ACCOUNT_DAYS,
        "recebeu_de_madrugada": info.index.to_series().isin(set(night["receiver"])),
    }


def summarize(runs: pd.DataFrame) -> pd.DataFrame:
    """Por (cenário, atributo): efeito médio, IC 95% t entre as sementes e em quantas o p de Holm < alfa."""
    grouped = runs.groupby(["cenario", "atributo"], sort=False)
    table = grouped["efeito"].agg(efeito_medio="mean", desvio="std", sementes="count")
    half = sps.t.ppf(0.975, (table["sementes"] - 1).clip(lower=1)) * table["desvio"] / np.sqrt(table["sementes"])
    table["ic_inferior"], table["ic_superior"] = table["efeito_medio"] - half, table["efeito_medio"] + half
    table["sementes_significativas"] = grouped["p_holm"].apply(lambda p: int((p < ALPHA).sum()))
    if "razao_de_chances" in runs:
        table["razao_de_chances_mediana"] = grouped["razao_de_chances"].median()
    return table.reset_index().sort_values(["cenario", "efeito_medio"], ascending=[True, False])


def _plot_roles(summary: pd.DataFrame, names: list, n: int, path: Path) -> None:
    """Matriz atributo × cenário do ε² médio do Kruskal-Wallis entre os papéis."""
    matrix = summary.pivot(index="atributo", columns="cenario", values="efeito_medio")[names]
    order = [c for s in FEATURE_SETS.values() for c in s]
    matrix = matrix.reindex([c for c in dict.fromkeys(order) if c in matrix.index])
    fig, ax = plt.subplots(figsize=(2.6 + 1.05 * len(names), 0.34 * len(matrix) + 1.6), layout="constrained")
    vmax = max(0.3, float(np.nanmax(matrix.to_numpy())))
    mesh = plot_value_matrix(matrix, SEQUENTIAL_CMAP, vmin=0, vmax=vmax, fmt="{:.2f}", ax=ax)
    colorbar = fig.colorbar(mesh, ax=ax, shrink=0.6, pad=0.02)
    colorbar.set_label("ε² do Kruskal-Wallis entre os papéis", color=INK_SECONDARY)
    colorbar.outline.set_visible(False)
    ax.set_title(f"Quanto cada atributo separa os 6 papéis ({n} sementes de validação)\n"
                 "ε² ≥ 0,14: efeito grande · ≥ 0,06: médio", color=INK, fontsize=9, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
