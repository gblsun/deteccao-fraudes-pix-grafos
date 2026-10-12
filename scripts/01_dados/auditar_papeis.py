"""O papel de cada conta corresponde ao que ela fez? (reunião de 01/10)

Confere, conta por conta, se o papel gravado pelo gerador (comércio, laranja,
intermediário, coletor, vítima, normal) bate com as transações da conta, usando
as regras de ``pixfraud.simulation.audit_roles``: o comércio só paga salário e
fornecedor, a laranja recebe golpe e repassa, a coletora recebe repasses e é a
única que tira o dinheiro, e assim por diante.

Roda no dataset gravado (``--dados``) e em ``--sementes`` sementes de cada
cenário, incluindo o ``aleatorio`` (estrutura sorteada). Também resume o
comportamento típico de cada papel (graus, volume, repasse), para mostrar o que
cada um faz na prática.

Saídas em reports/01_dados/results/:
    auditoria_papeis.csv          uma linha por violação (vazio se tudo confere)
    auditoria_resumo.csv          uma linha por (cenário, semente): contas por papel e violações
    auditoria_perfis.csv          mediana de graus, volumes e repasse por papel e cenário
    auditoria_meta.json           como o resultado foi gerado

Uso:
    python scripts/01_dados/auditar_papeis.py
    python scripts/01_dados/auditar_papeis.py --cenarios base aleatorio --sementes 50
"""

import argparse
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd

from pixfraud.experiment import load_experiment_config, load_scenarios, save_metadata
from pixfraud.simulation import (
    audit_roles,
    generate_dataset,
    load_config,
    load_dataset,
    structure_summary,
    with_overrides,
)

ROLES = ["laranja", "intermediario", "coletor", "comercio", "vitima", "normal"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Confere se o papel de cada conta bate com as transações dela.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=None, help="padrão: todos os de --arquivo-cenarios")
    parser.add_argument("--sementes", type=int, default=20)
    parser.add_argument("--dados", default="data/synthetic")
    parser.add_argument("--saida", default="reports/01_dados")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    names = args.cenarios or list(scenarios)
    unknown = [n for n in names if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")

    datasets = []
    if (Path(args.dados) / "accounts.csv").exists():
        datasets.append((f"gravado ({args.dados})", None, lambda: load_dataset(args.dados), None))
    for name in names:
        for seed in range(1, args.sementes + 1):
            cfg = replace(with_overrides(base, scenarios[name]), seed=seed)
            datasets.append((name, seed, lambda cfg=cfg: generate_dataset(cfg), cfg))

    violations, summary, profiles = [], [], []
    for name, seed, load, cfg in datasets:
        accounts, tx = load()
        found = audit_roles(accounts, tx).assign(cenario=name, semente=seed)
        violations.append(found)
        info = accounts.set_index("account_id")
        roles = info["role"].where(~info["is_victim"], "vitima")
        counts = roles.value_counts()
        row = {"cenario": name, "semente": seed, "contas": len(accounts), **{r: int(counts.get(r, 0)) for r in ROLES},
               "violacoes": len(found), "contas_com_violacao": found["account_id"].nunique()}
        if cfg is not None and cfg.estrutura_aleatoria:
            structure = structure_summary(cfg)
            row["quadrilhas"] = len(structure["quadrilhas"])
            row["coletoras"] = "/".join(q["coletora"] for q in structure["quadrilhas"])
        summary.append(row)
        if seed in (None, 1):
            profiles.append(_profile(tx, roles).assign(cenario=name))
        print(f"{name} {seed or ''}: {len(found)} violações", flush=True)

    results = Path(args.saida) / "results"
    results.mkdir(parents=True, exist_ok=True)
    violations = pd.concat(violations, ignore_index=True)
    summary = pd.DataFrame(summary)
    violations.to_csv(results / "auditoria_papeis.csv", index=False)
    summary.to_csv(results / "auditoria_resumo.csv", index=False)
    pd.concat(profiles).to_csv(results / "auditoria_perfis.csv")
    save_metadata(results / "auditoria_meta.json", config, cenarios={n: scenarios[n] for n in names},
                  sementes=list(range(1, args.sementes + 1)), dados=args.dados,
                  duracao_s=round(time.time() - began))

    print("\nviolações por cenário (soma das sementes):")
    print(summary.groupby("cenario", sort=False)[["violacoes", "contas_com_violacao"]].sum().to_string())
    if len(violations):
        print("\nregras violadas:")
        print(violations.groupby(["cenario", "role", "regra"]).size().to_string())
        with_violation = summary[summary["violacoes"] > 0].groupby("cenario", sort=False).size()
        print("\ndatasets com alguma violação:\n" + with_violation.to_string())
    print("\nperfil mediano de cada papel no primeiro dataset:")
    print(profiles[0].round(2).to_string())


def _profile(tx: pd.DataFrame, roles: pd.Series) -> pd.DataFrame:
    """Mediana, por papel, do que as contas fazem: quem paga, quem recebe e quanto repassam."""
    sent = tx.groupby("sender").agg(pagou_a=("receiver", "nunique"), enviou=("amount", "sum"))
    got = tx.groupby("receiver").agg(recebeu_de=("sender", "nunique"), recebeu=("amount", "sum"))
    pf_payers = tx.assign(pf=tx["sender"].map(roles).isin(["normal", "vitima"])).groupby("receiver")["pf"].mean()
    table = pd.DataFrame(index=roles.index).join(got).join(sent).fillna(0.0)
    table["repasse"] = (table["enviou"] / table["recebeu"].where(table["recebeu"] > 0)).clip(upper=5)
    table["pagadores_pf"] = pf_payers
    table["papel"] = roles
    return table.groupby("papel").median().reindex([r for r in ROLES if r in set(roles)])


if __name__ == "__main__":
    main()
