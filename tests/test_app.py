"""Teste de fumaça do explorador Streamlit (pulado se o Streamlit não estiver instalado)."""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

from pixfraud.simulation import SimulationConfig, generate_dataset, save_dataset  # noqa: E402

APP = Path(__file__).parents[1] / "app" / "explorador.py"
pytestmark = pytest.mark.lento
TABS = ["Resumo", "Rede inteira", "Ranking", "Modelos", "Conta", "Padrões de fraude", "Fluxo e bloqueio", "Resultados"]


@pytest.fixture
def app(tmp_path, monkeypatch):
    save_dataset(*generate_dataset(SimulationConfig(n_people=300, n_merchants=15, n_days=7, n_rings=2)), tmp_path)
    monkeypatch.setenv("PIXFRAUD_DADOS", str(tmp_path))  # um dataset pequeno, para o teste ser rápido
    app = AppTest.from_file(str(APP), default_timeout=600)
    app.run()
    return app


def test_app_runs_all_tabs_with_the_saved_dataset(app):
    assert not app.exception
    assert [t.label for t in app.tabs] == TABS
    labels = [m.label for m in app.metric]
    assert "Contas" in labels and "Average precision (AP)" in labels and "Fluxo máximo" in labels


def test_typed_seed_generates_a_new_network(app):
    app.sidebar.radio[0].set_value("gerar uma rede").run()
    app.sidebar.number_input(key="seed").set_value(7).run()
    assert any("Gerar rede" in i.value for i in app.sidebar.info)  # escolha nova, ainda não gerada
    app.sidebar.button[1].click().run()  # [0] é o dado; [1] é "Gerar rede"
    assert not app.exception
    assert "Semente 7" in app.sidebar.caption[-1].value
