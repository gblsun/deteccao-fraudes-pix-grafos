"""Testes de fumaça dos scripts de avaliação com várias sementes, num dataset minúsculo."""

import subprocess
import sys
from pathlib import Path

import pandas as pd

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


def _run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args], check=True, capture_output=True)


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
