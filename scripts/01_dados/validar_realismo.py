"""O dataset sintético parece o Pix real? Validação do gerador contra o Banco Central.

Duas perguntas, antes de qualquer modelo (etapa 1 do fluxo da pesquisa, ver
docs/plano-de-testes-estatisticos.md):

* **Os números batem com o BCB?** Para cada estatística que o BCB publica
  agregada (fração de Pix de pessoa física que vai para empresas, ticket médio
  P2P e P2B, golpes a cada 100 mil Pix, valor médio de um golpe), calcula a
  média do gerador em ``--sementes`` redes de cada cenário, com IC 95% t, e
  compara com o valor do BCB: o BCB cai no IC? o erro relativo fica dentro de
  ``--tolerancia``? Como o BCB só publica agregados, não há distribuição para
  um teste de aderência (KS); o IC entre sementes é o teste possível.
* **A estrutura é diferente do acaso?** Reciprocidade e transitividade da rede
  contra grafos aleatórios com os mesmos graus (``stats.null_model_test``):
  se a rede sintética tem mais ciclos e triângulos que o acaso, os atributos de
  grafo têm o que medir.

A taxa de golpes do gerador é maior que a real de propósito (para haver
exemplos de fraude); a tabela mostra o quanto.

Lê data/bcb/transacoes_*.csv e fraudes_*.csv (baixados por baixar_dados_bcb.py).

Saídas em reports/01_dados/results/:
    realismo_execucoes.csv   uma linha por (cenário, semente): as estatísticas do gerador
    realismo_comparacao.csv  uma linha por (cenário, estatística): BCB, média, IC 95%, erro relativo
    realismo_estrutura.csv   uma linha por (cenário, estatística): observado, nulo, z e p empírico
    realismo_meta.json       como o resultado foi gerado

Uso:
    python scripts/01_dados/validar_realismo.py
    python scripts/01_dados/validar_realismo.py --cenarios calibrado aleatorio --sementes 20
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats as sps

from pixfraud.experiment import load_experiment_config, load_scenarios, save_metadata
from pixfraud.graph import build_graph
from pixfraud.simulation import generate_dataset, load_config, with_overrides
from pixfraud.stats import null_model_test

STATISTICS = {
    "fracao_p2b": "Pix de pessoa física para empresa (fração)",
    "ticket_p2p": "ticket médio P2P (R$)",
    "ticket_p2b": "ticket médio P2B (R$)",
    "golpes_100mil": "golpes a cada 100 mil Pix",
    "valor_golpe": "valor médio de um golpe (R$)",
}
STRUCTURE = {
    "reciprocidade": nx.reciprocity,
    "transitividade": lambda g: nx.transitivity(nx.Graph(g)),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara o dataset sintético com as estatísticas do Pix no BCB.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["calibrado", "aleatorio"])
    parser.add_argument("--sementes", type=int, default=10)
    parser.add_argument("--tolerancia", type=float, default=0.2, help="erro relativo aceito (0,2 = 20%%)")
    parser.add_argument("--amostras-nulas", type=int, default=50, help="grafos aleatórios do modelo nulo")
    parser.add_argument("--bcb", default="data/bcb")
    parser.add_argument("--saida", default="reports/01_dados")
    args = parser.parse_args()
    began = time.time()

    reference = bcb_reference(Path(args.bcb))
    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")

    runs, structure = [], []
    for name in args.cenarios:
        for seed in range(1, args.sementes + 1):
            accounts, tx = generate_dataset(replace(with_overrides(base, scenarios[name]), seed=seed))
            runs.append({"cenario": name, "semente": seed, **synthetic_statistics(accounts, tx)})
            if seed == 1:  # o modelo nulo é caro: uma rede por cenário
                graph = build_graph(tx, accounts["account_id"])
                for stat, func in STRUCTURE.items():
                    result = null_model_test(graph, func, n_samples=args.amostras_nulas, seed=seed)
                    structure.append({"cenario": name, "estatistica": stat, **result})
            print(f"{name}: semente {seed}/{args.sementes}", flush=True)

    runs = pd.DataFrame(runs)
    comparison = compare_with_reference(runs, reference, args.tolerancia)
    results = Path(args.saida) / "results"
    results.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "realismo_execucoes.csv", index=False)
    comparison.to_csv(results / "realismo_comparacao.csv", index=False)
    pd.DataFrame(structure).to_csv(results / "realismo_estrutura.csv", index=False)
    save_metadata(results / "realismo_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes=list(range(1, args.sementes + 1)), tolerancia=args.tolerancia,
                  bcb=reference, duracao_s=round(time.time() - began))

    print("\ngerador × BCB (média entre sementes, IC 95%):")
    print(comparison.round(3).to_string(index=False))
    print("\nestrutura contra o modelo nulo (graus preservados):")
    print(pd.DataFrame(structure).round(3).to_string(index=False))


def bcb_reference(folder: Path) -> dict[str, float]:
    """As mesmas estatísticas, nos dados abertos do Pix (só agregados, sem dado pessoal)."""
    tx = pd.concat([pd.read_csv(f) for f in sorted(folder.glob("transacoes_*.csv"))])
    fraud = pd.concat([pd.read_csv(f) for f in sorted(folder.glob("fraudes_*.csv"))]).drop_duplicates("AnoMes")
    pf = tx[tx["PAG_PFPJ"] == "PF"]
    by_kind = tx.groupby("NATUREZA")[["VALOR", "QUANTIDADE"]].sum()
    return {
        "fracao_p2b": float(pf.loc[pf["NATUREZA"] == "P2B", "QUANTIDADE"].sum() / pf["QUANTIDADE"].sum()),
        "ticket_p2p": float(by_kind.loc["P2P", "VALOR"] / by_kind.loc["P2P", "QUANTIDADE"]),
        "ticket_p2b": float(by_kind.loc["P2B", "VALOR"] / by_kind.loc["P2B", "QUANTIDADE"]),
        "golpes_100mil": float(fraud["Qtdecontestacoesaceitasacada100mil"].mean()),
        "valor_golpe": float(fraud["ValorPixcontestadosaceitos"].sum() / fraud["Qtdecontestacoesaceitas"].sum()),
    }


def synthetic_statistics(accounts: pd.DataFrame, tx: pd.DataFrame) -> dict[str, float]:
    """As estatísticas do BCB calculadas numa rede sintética.

    Golpe é o Pix da vítima (pessoa comum) para a quadrilha; os repasses
    internos da quadrilha não contam, como nas contestações do BCB.
    """
    info = accounts.set_index("account_id")
    payer, payee = tx["sender"].map(info["account_type"]), tx["receiver"].map(info["account_type"])
    sender_role = tx["sender"].map(info["role"])
    legit = ~tx["is_fraud"]
    from_pf = legit & (payer == "PF")
    scams = tx[tx["is_fraud"] & (sender_role == "normal")]
    p2p, p2b = tx[from_pf & (payee == "PF")], tx[from_pf & (payee == "PJ")]
    return {
        "fracao_p2b": len(p2b) / max(1, from_pf.sum()),
        "ticket_p2p": float(p2p["amount"].mean()),
        "ticket_p2b": float(p2b["amount"].mean()),
        "golpes_100mil": 1e5 * len(scams) / len(tx),
        "valor_golpe": float(scams["amount"].mean()) if len(scams) else float("nan"),
    }


def compare_with_reference(runs: pd.DataFrame, reference: dict[str, float], tolerance: float) -> pd.DataFrame:
    """Para cada (cenário, estatística): média do gerador, IC 95% t, valor do BCB e erro relativo."""
    rows = []
    for name, group in runs.groupby("cenario", sort=False):
        for stat, label in STATISTICS.items():
            values = group[stat].dropna().to_numpy()
            n, mean = len(values), float(values.mean())
            half = float(sps.t.ppf(0.975, n - 1) * values.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
            error = (mean - reference[stat]) / reference[stat]
            rows.append({"cenario": name, "estatistica": stat, "descricao": label, "bcb": reference[stat],
                         "gerador_media": mean, "ic_inferior": mean - half, "ic_superior": mean + half,
                         "erro_relativo": error, "bcb_no_ic": mean - half <= reference[stat] <= mean + half,
                         "dentro_da_tolerancia": abs(error) <= tolerance, "sementes": n})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()
