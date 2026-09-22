"""Testes de fumaça dos scripts de avaliação, num dataset minúsculo."""

import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from pixfraud.simulation import SimulationConfig, generate_dataset, save_dataset

ROOT = Path(__file__).parents[1]
CONFIG = """
simulacao: {n_people: 150, n_merchants: 8, n_days: 4, n_rings: 2, victims_per_ring: 5}
atributos: {betweenness_k: 50}
modelos:
  isolation_forest: {n_estimators: 50}
  dbscan: {min_samples: 5}
"""
SCENARIOS = """
base: {}
dificil: {fraud_hours: comercial, p_new_fraud_account: 0.0, quiet_fraction: 0.3}
"""


def _run(script: str, *args: str) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True, capture_output=True,
                          env=env)
    return done.stdout.decode("utf-8")


def test_avaliar_cenarios(tmp_path):
    (tmp_path / "config.yaml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "cenarios.yaml").write_text(SCENARIOS, encoding="utf-8")
    _run("avaliar_cenarios.py", "--config", str(tmp_path / "config.yaml"),
         "--arquivo-cenarios", str(tmp_path / "cenarios.yaml"), "--sementes", "2", "--saida", str(tmp_path))

    runs = pd.read_csv(tmp_path / "results" / "cenarios_execucoes.csv")
    assert set(runs["cenario"]) == {"base", "dificil"} and set(runs["semente"]) == {1, 2}
    comparisons = pd.read_csv(tmp_path / "results" / "cenarios_comparacoes.csv")
    assert {"cenario", "comparação", "p Wilcoxon (Holm)"} <= set(comparisons.columns)
    effects = pd.read_csv(tmp_path / "results" / "cenarios_efeitos.csv")
    assert effects["delta_medio"].between(-1, 1).all()
    for figure in ("cenarios_average_precision.png", "cenarios_efeitos.png"):
        assert (tmp_path / "figures" / figure).stat().st_size > 0


def test_avaliar_robustez(tmp_path):
    (tmp_path / "config.yaml").write_text(CONFIG, encoding="utf-8")
    _run("avaliar_robustez.py", "--config", str(tmp_path / "config.yaml"), "--sementes", "2", "--saida", str(tmp_path))
    summary = pd.read_csv(tmp_path / "results" / "robustez_resumo.csv")
    assert set(summary["métrica"]) >= {"average_precision", "roc_auc"}
    assert (tmp_path / "figures" / "robustez_average_precision.png").exists()


def test_avaliar_externo(tmp_path):
    # um dataset sintético pequeno fazendo o papel de dataset externo, com o papel como "tipologia"
    accounts, transactions = generate_dataset(SimulationConfig(n_people=200, n_merchants=10, n_days=6, n_rings=3,
                                                               victims_per_ring=5))
    data = tmp_path / "externo"
    save_dataset(accounts, transactions, data)
    fraud = accounts[accounts["is_fraud"]]
    fraud[["account_id", "role"]].rename(columns={"role": "typology"}).to_csv(data / "patterns.csv", index=False)
    (tmp_path / "config.yaml").write_text(CONFIG, encoding="utf-8")
    args = ["--config", str(tmp_path / "config.yaml"), "--dados", str(data), "--dias-janela", "2",
            "--min-fraudes", "1", "--saida", str(tmp_path / "saida")]
    first = _run("avaliar_externo.py", *args)
    assert "reaproveitada" not in first
    assert "reaproveitada" in _run("avaliar_externo.py", *args)  # as janelas prontas ficam salvas

    runs = pd.read_csv(tmp_path / "saida" / "results" / "externo_execucoes.csv")
    assert runs["janela"].nunique() >= 1 and set(runs["modelo"]) == {"isolation_forest", "dbscan"}
    typologies = pd.read_csv(tmp_path / "saida" / "results" / "externo_tipologias.csv")
    assert set(typologies["typology"]) <= {"laranja", "intermediario", "coletor"}
    assert typologies["recall_at_k"].between(0, 1).all()
    assert (tmp_path / "saida" / "figures" / "externo_tipologias.png").exists()


def test_avaliar_deteccao_online(tmp_path):
    (tmp_path / "config.yaml").write_text(CONFIG, encoding="utf-8")
    (tmp_path / "cenarios.yaml").write_text(SCENARIOS, encoding="utf-8")
    args = ["--config", str(tmp_path / "config.yaml"), "--arquivo-cenarios", str(tmp_path / "cenarios.yaml"),
            "--cenarios", "dificil", "--sementes", "2", "--frequencia", "12h", "--conjuntos", "tabular", "grafo",
            "--saida", str(tmp_path)]
    _run("avaliar_deteccao_online.py", *args)
    runs = pd.read_csv(tmp_path / "results" / "online_execucoes.csv")
    assert set(runs["atributos"]) == {"tabular", "grafo", "oráculo"}
    recovered = runs[["recuperado_1h", "recuperado_6h", "recuperado_24h"]]
    assert recovered.stack().between(0, 1 + 1e-9).all()  # soma de pedaços: arredondamento
    assert (runs["recuperado_1h"] <= runs["recuperado_24h"] + 1e-9).all()  # mais prazo, mais dinheiro retido
    assert len(list((tmp_path / "results" / "online_cortes").glob("*.csv"))) == 2
    assert (tmp_path / "figures" / "online_deteccao.png").exists()
