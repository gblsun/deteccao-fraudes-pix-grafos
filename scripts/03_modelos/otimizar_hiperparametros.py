"""Otimiza os hiperparâmetros de cada modelo em redes de validação, até achar o melhor, e grava a configuração.

Para cada cenário de ``--cenarios`` e cada semente de validação (1001, 1002...,
nunca usadas pelos estudos de avaliação), gera a rede, calcula os atributos e
dá nota (average precision) a cada candidato. A busca roda em rodadas:

1. a grade de ``configs/busca_hiperparametros.yaml``, mais a configuração atual;
2. para cada modelo cujo vencedor caiu numa ponta da lista (o maior ou o menor
   valor testado), acrescenta um valor além da ponta e testa só as combinações
   novas;
3. repete até nenhum vencedor estar numa ponta que possa crescer, ou até
   ``--rodadas``.

O vencedor de cada modelo vai para ``--config-saida``, uma cópia de
``--config`` com a seção ``modelos`` trocada. Para medir o ganho sem trapaça,
avalie depois nas sementes de teste (1, 2, 3...):

    python scripts/03_modelos/avaliar_modelos.py --config configs/experimento_otimizado.yaml --saida reports/otimizado

As redes neurais para grafos (DOMINANT e GraphSAGE) ficam de fora: precisam
do extra ``gnn`` e custam minutos por treino.

Saídas:
    reports/03_modelos/results/otimizacao_execucoes.csv  uma linha por (rodada, cenário, semente, modelo, candidato)
    reports/03_modelos/results/otimizacao_resumo.csv     AP média de cada candidato e qual foi escolhido
    reports/03_modelos/results/otimizacao_meta.json      como o resultado foi gerado, com as grades finais
    configs/experimento_otimizado.yaml        a configuração com os hiperparâmetros escolhidos

Uso:
    python scripts/03_modelos/otimizar_hiperparametros.py --processos 4
    python scripts/03_modelos/otimizar_hiperparametros.py --modelos knn kmeans pca --sementes 1 --rodadas 2
"""

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import pandas as pd
import yaml

from pixfraud.experiment import load_experiment_config, load_scenarios, prepare, save_metadata
from pixfraud.features import FEATURE_SETS
from pixfraud.simulation import generate_dataset, load_config, with_overrides
from pixfraud.tuning import (
    DEFAULT_PATH,
    VALIDATION_SEED,
    candidates,
    choose,
    chosen_params,
    expand,
    full_params,
    load_search_spaces,
    params_key,
    score_candidates,
)
from pixfraud.visualization import model_label

HEADER = """\
# Gerado por scripts/03_modelos/otimizar_hiperparametros.py: cópia de {origem} com a seção
# `modelos` trocada pelos hiperparâmetros de maior average precision nas redes de
# validação (cenários {cenarios}; sementes {sementes}; {rodadas} rodadas de busca).
# Não edite à mão: rode o script de novo. Cada candidato testado está em
# reports/03_modelos/results/otimizacao_resumo.csv.

"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Otimiza os hiperparâmetros de cada modelo em redes de validação.")
    parser.add_argument("--config", default="configs/experimento.yaml")
    parser.add_argument("--grades", default=str(DEFAULT_PATH), help="valores testados de cada hiperparâmetro")
    parser.add_argument("--arquivo-cenarios", default="configs/cenarios.yaml")
    parser.add_argument("--cenarios", nargs="+", default=["realista", "negativos_dificeis", "quadrilhas_realistas"],
                        help="cenários das redes de validação (padrão: os mais realistas)")
    parser.add_argument("--sementes", type=int, default=2, help="redes de validação por cenário")
    parser.add_argument("--rodadas", type=int, default=6, help="máximo de rodadas de ampliação da grade")
    parser.add_argument("--conjunto", default="completo", choices=list(FEATURE_SETS))
    parser.add_argument("--modelos", nargs="+", help="padrão: todos os que têm grade")
    parser.add_argument("--processos", type=int, default=1, help="redes avaliadas ao mesmo tempo")
    parser.add_argument("--saida", default="reports/03_modelos")
    parser.add_argument("--config-saida", default="configs/experimento_otimizado.yaml")
    args = parser.parse_args()
    began = time.time()

    config = load_experiment_config(args.config)
    base = load_config(args.config)
    scenarios = load_scenarios(args.arquivo_cenarios)
    unknown = [n for n in args.cenarios if n not in scenarios]
    if unknown:
        parser.error(f"cenários desconhecidos: {', '.join(unknown)}")
    spaces = load_search_spaces(args.grades)
    models = args.modelos or list(spaces)
    missing = [m for m in models if m not in spaces]
    if missing:
        parser.error(f"modelos sem grade em {args.grades}: {', '.join(missing)}")
    configured = {m: config["modelos"].get(m, {}) for m in models}
    current = {m: full_params(m, configured[m], spaces[m]) for m in models}
    seeds = list(range(VALIDATION_SEED, VALIDATION_SEED + args.sementes))
    networks = [(with_overrides(base, scenarios[name]), name, seed) for name in args.cenarios for seed in seeds]

    todo = {m: candidates(m, configured[m], spaces[m]) for m in models}
    tested = {m: {params_key(p) for p in todo[m]} for m in models}
    rows, rounds, history = [], 0, []
    with ProcessPoolExecutor(max_workers=max(1, args.processos)) as pool:
        while todo and rounds < args.rodadas:
            rounds += 1
            total = sum(len(v) for v in todo.values())
            print(f"\nrodada {rounds}: {total} candidatos em {len(todo)} modelos × {len(networks)} redes", flush=True)
            jobs = [(simulation, name, seed, config, args.conjunto, todo, current)
                    for simulation, name, seed in networks]
            for job, done in zip(jobs, pool.map(_score_star, jobs)):
                rows += [{"rodada": rounds, **row} for row in done]
                print(f"  {job[1]}: semente {job[2]} concluída ({time.time() - began:.0f} s)", flush=True)
            best = chosen_params(choose(pd.DataFrame(rows)))
            todo = {}
            for model in models:
                spaces[model], changes = expand(spaces[model], best[model])
                new = [p for p in candidates(model, configured[model], spaces[model])
                       if params_key(p) not in tested[model]]
                if new:
                    todo[model] = new
                    tested[model] |= {params_key(p) for p in new}
                    history.append({"rodada": rounds, "modelo": model, "ampliou": changes})
                    print(f"  {model_label(model)}: vencedor na ponta da grade; {'; '.join(changes)}", flush=True)

    runs = pd.DataFrame(rows)
    summary = choose(runs)
    best = chosen_params(summary)
    unfinished = sorted(todo)  # ainda queriam crescer quando as rodadas acabaram

    results = Path(args.saida) / "results"
    results.mkdir(parents=True, exist_ok=True)
    runs.to_csv(results / "otimizacao_execucoes.csv", index=False)
    summary.to_csv(results / "otimizacao_resumo.csv", index=False)
    final_spaces = {m: {k: list(p.values) for k, p in spaces[m].items()} for m in models}
    save_metadata(results / "otimizacao_meta.json", config, cenarios={n: scenarios[n] for n in args.cenarios},
                  sementes_validacao=seeds, conjunto=args.conjunto, modelos=models, rodadas=rounds,
                  ampliacoes=history, grades_finais=final_spaces, sem_convergir=unfinished, escolhidos=best,
                  duracao_s=round(time.time() - began))
    _write_config(args.config, args.config_saida, best, args.cenarios, seeds, rounds)

    print("\naverage precision média nas redes de validação:")
    table = []
    for model in models:
        group = summary[summary["modelo"] == model]
        default = group[group["padrao"]].iloc[0]
        chosen = group[group["escolhido"]].iloc[0]
        before = json.loads(default["parametros"])
        change = {k: v for k, v in best[model].items() if before.get(k) != v}
        table.append({"modelo": model_label(model), "padrão": round(default["media"], 3),
                      "otimizado": round(chosen["media"], 3), "candidatos": len(group),
                      "mudou": ", ".join(f"{k}={v}" for k, v in change.items()) or "(manteve)"})
    print(pd.DataFrame(table).sort_values("otimizado", ascending=False).to_string(index=False))
    if unfinished:
        print(f"\naviso: ainda na ponta da grade depois de {rounds} rodadas: {', '.join(unfinished)} "
              "(aumente --rodadas ou os limites em --grades)")
    print(f"\nconfiguração salva em {args.config_saida}")


def _score_star(job):
    simulation, name, seed, config, conjunto, todo, current = job
    accounts, tx = generate_dataset(replace(simulation, seed=seed))
    prepared = prepare(accounts, tx, config)
    rows = score_candidates(prepared, FEATURE_SETS[conjunto], todo, current, seed)
    return [{"cenario": name, "semente": seed, **row} for row in rows]


def _write_config(source: str, target: str, best: dict, scenarios: list, seeds: list, rounds: int) -> None:
    with open(source, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for model, params in best.items():
        config["modelos"][model] = params
    text = HEADER.format(origem=source, cenarios=", ".join(scenarios), sementes=", ".join(map(str, seeds)),
                         rodadas=rounds)
    text += yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
    Path(target).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
