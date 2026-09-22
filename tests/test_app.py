"""Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver instalado)."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

from pixfraud.simulation import SimulationConfig, generate_dataset, save_dataset  # noqa: E402

APP = Path(__file__).parents[1] / "app" / "explorador.py"
pytestmark = pytest.mark.lento


def test_app_runs_all_tabs(tmp_path, monkeypatch):
    save_dataset(*generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=7, n_rings=2)), tmp_path)
    monkeypatch.setenv("PIXFRAUD_DADOS", str(tmp_path))
    app = AppTest.from_file(str(APP), default_timeout=300)
    app.run()
    assert not app.exception
    tabs = ["Rede inteira", "Conta", "Padrões de fraude", "Fluxo e bloqueio", "Resultados"]
    assert [t.label for t in app.tabs] == tabs
    assert app.metric[0].label == "Fluxo máximo"
