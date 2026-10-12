"""Quem são as contas no topo do risco que não são fraude? (reunião de 01/10)

Na reunião, contas de comércio apareceram com "percentil de risco 100%" no
explorador da rede. Este script responde, para cada detector:

* quais contas ficam no topo do risco e qual é o **papel real** de cada uma
  (vindo do gerador: o modelo não prevê papel nenhum, só dá um escore);
* quantos falsos positivos há entre as k primeiras (k = nº de fraudes), e de
  que papel eles são: comércio, vítima ou conta normal;
* que atributos levam esses falsos positivos ao topo (percentil de cada
  atributo da conta entre todas as contas);
* se isso muda nos cenários em que o comércio também paga (salários,
  fornecedores), como ``negativos_dificeis``, ``calibrado`` e ``aleatorio``.

A primeira semente de cada cenário é a do YAML (42), a do dataset em
``data/synthetic`` e do explorador mostrado na reunião; o script confere se o
dataset gravado é mesmo esse.

Saídas em reports/05_interpretacao/results/:
    falsos_positivos_papeis.csv     uma linha por (cenário, semente, modelo): papéis no top-k
    falsos_positivos_top.csv        as ``--top`` contas de maior risco de cada modelo (semente 42)
    falsos_positivos_atributos.csv  percentil de cada atributo dessas contas
    falsos_positivos_testes.csv     (cenário, modelo): o modelo confunde comércio com fraude? (Fisher
                                    "no top-k" × "é comércio", só nas legítimas) e o escore ordena os
                                    papéis? (Kruskal-Wallis do escore por papel, com ε²)
    falsos_positivos_dunn.csv       que pares de papéis o escore separa (teste de Dunn, semente do YAML)
    falsos_positivos_meta.json      como o resultado foi gerado
e a figura reports/05_interpretacao/figures/falsos_positivos_comercio.png.

Uso:
    python scripts/05_interpretacao/investigar_falsos_positivos.py
    python scripts/05_interpretacao/investigar_falsos_positivos.py --cenarios base --sementes 1 --top 30
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud.anomaly import DETECTORS  # noqa: E402
from pixfraud.experiment import load_experiment_config, load_scenarios, prepare, save_metadata  # noqa: E402
from pixfraud.features import FEATURE_SETS  # noqa: E402
from pixfraud.simulation import generate_dataset, load_config, load_dataset, with_overrides  # noqa: E402
from pixfraud.stats import contingency_test, dunn_posthoc, kruskal_groups  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SEQUENTIAL_CMAP, SURFACE, model_label  # noqa: E402

ROLES = ["laranja", "intermediario", "coletor", "comercio", "vitima", "normal"]
LEGIT = ["comercio", "vitima", "normal"]


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description="Investiga os falsos positivos no topo do risco.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["base", "negativos_dificeis", "calibrado", "aleatorio"])
    parser.add_argument("--sementes", type=int, default=10, help="a do YAML e mais sementes 1, 2, ...")
    parser.add_argument("--conjunto", default="completo", choices=list(FEATURE_SETS))
    parser.add_argument("--top", type=int, default=20, help="contas listadas por modelo na semente do YAML")
    parser.add_argument("--dados", default="data/synthetic", help="dataset gravado, conferido contra a semente do YAML")
    parser.add_argument("--saida", default="reports/05_interpretacao")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    seeds = [base.seed, *[s for s in range(1, args.sementes + 2) if s != base.seed]][: args.sementes]
    _check_saved_dataset(base, args.dados)

    rows, tops, attributes, dunn = [], [], [], []
    for name in args.cenarios:
        for seed in seeds:
            accounts, tx = generate_dataset(replace(with_overrides(base, scenarios[name]), seed=seed))
            prepared = prepare(accounts, tx, config)
            info = accounts.set_index("account_id")
            roles = info["role"].where(~info["is_victim"], "vitima")
            features = prepared.features[FEATURE_SETS[args.conjunto]]
            k = int(info["is_fraud"].sum())
            for model, detect in DETECTORS.items():
                risk = detect(features, **config["modelos"].get(model, {})).scores
                order = risk.sort_values(ascending=False, kind="stable")
                counts = roles[order.index[:k]].value_counts()
                legit = roles[roles.isin(LEGIT)].index
                in_top = pd.Series(legit.isin(order.index[:k]), index=legit)
                merchant = pd.Series(roles[legit] == "comercio", index=legit)
                fisher = contingency_test(in_top, merchant) if in_top.any() and merchant.any() else {}
                by_role = kruskal_groups(risk.rename("risco").to_frame(), roles).iloc[0]
                rows.append({"cenario": name, "semente": seed, "modelo": model, "k": k,
                             **{r: int(counts.get(r, 0)) for r in ROLES},
                             "falsos_positivos": int(counts.reindex(LEGIT).fillna(0).sum()),
                             "razao_chances_comercio": fisher.get("razão de chances", float("nan")),
                             "p_fisher_comercio": fisher.get("p Fisher", float("nan")),
                             "epsilon2_papeis": by_role["ε²"], "p_kruskal_papeis": by_role["p-valor"]})
                if seed == base.seed:
                    dunn.append(dunn_posthoc(risk, roles).assign(cenario=name, modelo=model))
                if seed == base.seed:
                    top = order.index[: args.top]
                    tops.append(pd.DataFrame({
                        "cenario": name, "modelo": model, "posicao": range(1, len(top) + 1), "account_id": top,
                        "papel_real": roles[top].to_numpy(),
                        "percentil": risk.rank(pct=True)[top].round(4).to_numpy(),
                        "grau_entrada": features.get("in_degree", pd.Series(dtype=float)).reindex(top).to_numpy(),
                        "grau_saida": features.get("out_degree", pd.Series(dtype=float)).reindex(top).to_numpy(),
                    }))
                    pct = features.rank(pct=True).loc[top].round(3)
                    attributes.append(pct.assign(cenario=name, modelo=model, papel_real=roles[top]).reset_index())
            print(f"{name}: semente {seed} concluída", flush=True)

    results, figures = Path(args.saida) / "results", Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs = pd.DataFrame(rows)
    runs.to_csv(results / "falsos_positivos_papeis.csv", index=False)
    pd.concat(tops).to_csv(results / "falsos_positivos_top.csv", index=False)
    attributes = pd.concat(attributes).rename(columns={"index": "account_id"})
    attributes.to_csv(results / "falsos_positivos_atributos.csv", index=False)
    tests = _tests_table(runs)
    tests.to_csv(results / "falsos_positivos_testes.csv", index=False)
    pd.concat(dunn, ignore_index=True).to_csv(results / "falsos_positivos_dunn.csv", index=False)
    save_metadata(results / "falsos_positivos_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=seeds, conjunto=args.conjunto, top=args.top, duracao_s=round(time.time() - began))

    share = runs.assign(comercio_no_top=runs["comercio"] / runs["k"]).pivot_table(
        index="modelo", columns="cenario", values="comercio_no_top", aggfunc="mean")[args.cenarios]
    _plot_share(share.reindex(list(DETECTORS)), len(seeds), figures / "falsos_positivos_comercio.png")

    print(f"\nfração do top-k ocupada por comércios (média de {len(seeds)} sementes):")
    print(share.reindex(list(DETECTORS)).round(2).to_string())
    print("\nfalsos positivos no top-k, por papel (soma das sementes):")
    print(runs.groupby(["cenario", "modelo"])[LEGIT].sum().to_string())
    print("\no modelo confunde comércio com fraude? (Fisher nas legítimas; o escore ordena os papéis?)")
    print(tests.round(3).to_string(index=False))
    why = attributes[(attributes["modelo"] == "dbscan") & (attributes["cenario"] == args.cenarios[0])]
    print(f"\npercentil médio dos atributos no top-{args.top} do DBSCAN ({args.cenarios[0]}, semente {base.seed}):")
    columns = [c for c in FEATURE_SETS[args.conjunto] if c in why]
    print(why.groupby("papel_real")[columns].mean().T.round(2).to_string())


def _tests_table(runs: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Por (cenário, modelo): razão de chances mediana do comércio no top-k, em quantas sementes o Fisher
    deu p < alfa, e o ε² médio do Kruskal-Wallis do escore entre os papéis."""
    grouped = runs.groupby(["cenario", "modelo"], sort=False)
    return pd.DataFrame({
        "sementes": grouped.size(),
        "razao_chances_comercio_mediana": grouped["razao_chances_comercio"].median(),
        "sementes_fisher_significativo": grouped["p_fisher_comercio"].apply(lambda p: int((p < alpha).sum())),
        "epsilon2_papeis_medio": grouped["epsilon2_papeis"].mean(),
        "sementes_kruskal_significativo": grouped["p_kruskal_papeis"].apply(lambda p: int((p < alpha).sum())),
    }).reset_index()


def _check_saved_dataset(base, data_dir: str) -> None:
    """Avisa se ``data_dir`` não é o dataset da semente do YAML (o do explorador da reunião)."""
    if not (Path(data_dir) / "accounts.csv").exists():
        return
    saved, _ = load_dataset(data_dir)
    fresh, _ = generate_dataset(base)
    same = saved.set_index("account_id")["role"].sort_index().equals(fresh.set_index("account_id")["role"].sort_index())
    print(f"{data_dir}: {'é' if same else 'NÃO é'} o dataset da semente {base.seed}", flush=True)


def _plot_share(share: pd.DataFrame, n: int, path: Path) -> None:
    """Mapa de calor: fração das k primeiras contas de cada modelo que são comércios."""
    fig, ax = plt.subplots(figsize=(1.8 + 1.5 * share.shape[1], 0.9 + 0.38 * len(share)), layout="constrained")
    ax.imshow(share.to_numpy(dtype=float), cmap=SEQUENTIAL_CMAP, vmin=0, vmax=max(0.5, float(share.max().max())),
              aspect="auto")
    for (i, j), value in pd.DataFrame(share.to_numpy()).stack().items():
        ax.text(j, i, f"{value:.0%}", ha="center", va="center", fontsize=8,
                color=SURFACE if value > 0.3 else INK)
    ax.set_xticks(range(share.shape[1]), share.columns, color=INK_SECONDARY)
    ax.set_yticks(range(len(share)), [model_label(m) for m in share.index], color=INK_SECONDARY)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(f"Comércios entre as k contas de maior risco (k = nº de fraudes; média de {n} sementes)",
                 color=INK, fontsize=10, loc="left")
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
