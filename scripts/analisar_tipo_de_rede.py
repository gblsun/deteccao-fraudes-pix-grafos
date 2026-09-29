"""Que tipo de rede é a do Pix sintético? E o que passeios e cosseno dizem sobre as fraudes?

Pedido da reunião de 24/09 (estudar tipo de rede, lei de potência, Barabási–Albert,
componente gigante, passeio aleatório e similaridade de cosseno, depois implementar).
Para cada cenário e semente, gera o dataset e mede (``pixfraud.network``):

* **componentes**: fração das contas na componente gigante fraca e na forte;
* **lei de potência**: expoente ``alpha``, ``k_min`` e distância KS da cauda dos graus
  (total, de entrada e de saída);
* **passeios aleatórios** que seguem o dinheiro a partir das vítimas: em que papel de
  conta eles terminam e que fração passa pelas coletoras;
* **cosseno × Jaccard**: para cada laranja, que fração das 5 contas mais parecidas com
  ela (pelos valores pagos, ``cosine_out``, ou só pelos parceiros, ``jaccard_out``) também
  é fraudulenta.

Na primeira semente do primeiro cenário, compara ainda a rede com um Erdős–Rényi e um
Barabási–Albert do mesmo tamanho (``compare_network_models``).

Saídas em reports/results/:
    tipo_de_rede_execucoes.csv  uma linha por (cenário, semente)
    tipo_de_rede_resumo.csv     média e desvio por cenário
    tipo_de_rede_modelos.csv    rede × Erdős–Rényi × Barabási–Albert
    tipo_de_rede_passeios.csv   onde terminam os passeios que saem das vítimas, por papel
    tipo_de_rede_meta.json      como o resultado foi gerado
e a figura reports/figures/tipo_de_rede_graus.png.

Uso:
    python scripts/analisar_tipo_de_rede.py
    python scripts/analisar_tipo_de_rede.py --cenarios base coletor_ativo --sementes 10
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from pixfraud.algorithms import similar_accounts  # noqa: E402
from pixfraud.experiment import load_scenarios, save_metadata  # noqa: E402
from pixfraud.graph import build_graph  # noqa: E402
from pixfraud.network import (  # noqa: E402
    compare_network_models,
    component_summary,
    degree_sequence,
    fit_power_law,
    random_walk_visits,
)
from pixfraud.simulation import generate_dataset, load_config, with_overrides  # noqa: E402
from pixfraud.visualization import INK, INK_SECONDARY, SURFACE  # noqa: E402

# Cores categóricas em ordem fixa (validadas para daltonismo); rótulo direto em cada curva.
SERIES_COLORS = {"rede analisada": "#2a78d6", "Erdős–Rényi": "#eb6834", "Barabási–Albert": "#1baf7a"}
TOP = 5


def main() -> None:
    parser = argparse.ArgumentParser(description="Tipo de rede, passeios aleatórios e similaridade de cosseno.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["base", "realista", "coletor_ativo"])
    parser.add_argument("--sementes", type=int, default=5)
    parser.add_argument("--passeios", type=int, default=20, help="passeios por vítima")
    parser.add_argument("--saida", default="reports")
    args = parser.parse_args()
    began = time.time()

    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [s for s in args.cenarios if s not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)} (existem: {', '.join(scenarios)})")

    rows, walks, models = [], [], None
    for name in args.cenarios:
        simulation = with_overrides(base, scenarios[name])
        for seed in range(1, args.sementes + 1):
            accounts, tx = generate_dataset(replace(simulation, seed=seed))
            graph = build_graph(tx, accounts["account_id"])
            row, walk = _measure(graph, accounts, args.passeios, seed)
            rows.append({"cenario": name, "semente": seed, **row})
            walks.append(walk.assign(cenario=name, semente=seed))
            if models is None:
                models = compare_network_models(graph, seed=seed)
                degree_graphs = _degree_graphs(graph, seed)
                first, first_graph = name, graph
            print(f"{name}, semente {seed}: gigante fraca {row['gigante_fraca']:.3f}, "
                  f"alpha {row['alpha_total']:.2f}, passeios na coletora {row['passeios_pela_coletora']:.2f}",
                  flush=True)

    runs = pd.DataFrame(rows)
    walks = pd.concat(walks).groupby(["cenario", "papel"], sort=False)["destino"].mean().unstack("papel")
    summary = runs.drop(columns="semente").groupby("cenario", sort=False).agg(["mean", "std"])

    results = Path(args.saida) / "results"
    figures = Path(args.saida) / "figures"
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "tipo_de_rede_execucoes.csv", index=False)
    summary.to_csv(results / "tipo_de_rede_resumo.csv")
    models.to_csv(results / "tipo_de_rede_modelos.csv")
    walks.to_csv(results / "tipo_de_rede_passeios.csv")
    save_metadata(results / "tipo_de_rede_meta.json", None, cenarios=args.cenarios,
                  sementes=list(range(1, args.sementes + 1)), passeios_por_vitima=args.passeios,
                  cenario_da_comparacao=first, duracao_s=round(time.time() - began))
    _plot_degrees(degree_graphs, first_graph, figures / "tipo_de_rede_graus.png", first)

    pd.set_option("display.width", 160)
    print("\nrede × modelos clássicos:")
    print(models.round(3).to_string())
    print("\nmédia por cenário:")
    print(runs.drop(columns="semente").groupby("cenario", sort=False).mean().round(3).T.to_string())
    print("\nonde terminam os passeios que saem das vítimas (fração):")
    print(walks.round(3).to_string())


def _measure(graph: nx.DiGraph, accounts: pd.DataFrame, walks_per_start: int, seed: int):
    """As medidas de uma semente: componentes, lei de potência, passeios e cosseno × Jaccard."""
    row = component_summary(graph).to_dict()
    for kind in ("total", "in", "out"):
        fit = fit_power_law(degree_sequence(graph, kind))
        row |= {f"alpha_{kind}": fit["alpha"], f"k_min_{kind}": fit["k_min"], f"ks_{kind}": fit["ks"]}

    roles = accounts.set_index("account_id")["role"]
    victims = accounts.loc[accounts["is_victim"], "account_id"]
    table = random_walk_visits(graph, victims, walks_per_start=walks_per_start, seed=seed)
    collectors = roles.index[roles == "coletor"].intersection(table.index)
    row["passeios_pela_coletora"] = table.loc[collectors, "visitas"].sum()
    row["passeios_terminam_na_coletora"] = table.loc[collectors, "destino"].sum()
    walk = table.join(roles.rename("papel")).groupby("papel")["destino"].sum().reset_index()

    fraud = set(accounts.loc[accounts["is_fraud"], "account_id"])
    mules = roles.index[roles == "laranja"]
    for method in ("cosine_out", "jaccard_out"):
        hits = [similar_accounts(graph, m, method=method, top=TOP).index.isin(fraud).mean()
                for m in mules if graph.out_degree(m)]
        row[f"vizinhos_fraude_{method}"] = float(np.nanmean(hits)) if hits else np.nan
    return row, walk


def _degree_graphs(graph: nx.DiGraph, seed: int) -> dict[str, nx.Graph]:
    simple = nx.Graph(graph)
    n, m = simple.number_of_nodes(), simple.number_of_edges()
    return {
        "rede analisada": simple,
        "Erdős–Rényi": nx.gnm_random_graph(n, m, seed=seed),
        "Barabási–Albert": nx.barabasi_albert_graph(n, max(1, round(m / n)), seed=seed),
    }


def _ccdf(degrees: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    k = np.sort(degrees[degrees > 0])
    return k, 1.0 - np.arange(k.size) / k.size


def _plot_degrees(graphs: dict[str, nx.Graph], graph: nx.DiGraph, path: Path, scenario: str) -> None:
    """Acumulada complementar dos graus (log-log) em dois painéis.

    Esquerda: grau total da rede × Erdős–Rényi × Barabási–Albert. Direita: graus de
    entrada e de saída da rede, com a lei de potência ajustada à cauda da entrada.
    """
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True, facecolor=SURFACE)
    for name, g in graphs.items():
        k, ccdf = _ccdf(degree_sequence(g))
        left.loglog(k, ccdf, color=SERIES_COLORS[name], lw=2)
        left.annotate(name, (k[-1], ccdf[-1]), xytext=(4, 6), textcoords="offset points",
                      ha="left", fontsize=8, color=INK)
    left.set_title("(a) grau total: rede × modelos clássicos", color=INK, fontsize=10)

    in_color, out_color = SERIES_COLORS["rede analisada"], INK_SECONDARY
    for kind, label, color in (("in", "entrada", in_color), ("out", "saída", out_color)):
        k, ccdf = _ccdf(degree_sequence(graph, kind))
        right.loglog(k, ccdf, color=color, lw=2)
        right.annotate(f"grau de {label}", (k[-1], ccdf[-1]), xytext=(4, 6), textcoords="offset points",
                       fontsize=8, color=INK)
    k, ccdf = _ccdf(degree_sequence(graph, "in"))
    fit = fit_power_law(k)
    share = (k >= fit["k_min"]).mean()
    xs = np.geomspace(fit["k_min"], k.max(), 50)
    ys = share * ((xs - 0.5) / (fit["k_min"] - 0.5)) ** (1 - fit["alpha"])
    right.loglog(xs, ys, color=INK, lw=1, ls="--")
    alpha = f"{fit['alpha']:.2f}".replace(".", ",")
    right.annotate(f"lei de potência na entrada\nα = {alpha} (k ≥ {fit['k_min']})", (xs[5], ys[5]),
                   xytext=(-14, -30), textcoords="offset points", ha="right", fontsize=8, color=INK)
    right.set_title("(b) rede: entrada tem cauda pesada; saída, não", color=INK, fontsize=10)

    left.set_ylabel("P(grau ≥ k)", color=INK)
    for ax in (left, right):
        ax.set_xlabel("grau k (contas distintas)", color=INK)
        ax.set_facecolor(SURFACE)
        ax.grid(alpha=0.25, which="major")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=INK_SECONDARY)
        ax.set_xlim(right=ax.get_xlim()[1] * 3)
    fig.suptitle(f"Distribuição de graus da rede Pix sintética (cenário '{scenario}', semente 1)", color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
