"""Testes da busca única (scripts/buscar.py) num cofre e num grafo de código minúsculos."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("buscar", ROOT / "scripts" / "buscar.py")
buscar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(buscar)


def _cofre(tmp_path: Path) -> Path:
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "app.json").write_text(json.dumps({"userIgnoreFilters": ["src/"]}), encoding="utf-8")
    (tmp_path / "glossario").mkdir()
    (tmp_path / "glossario" / "propagacao.md").write_text(
        "# Propagação de risco\n\nCulpa por associação, em [flow.py](../src/flow.py).\n", encoding="utf-8")
    (tmp_path / "resultados.md").write_text(
        "# Resultados\n\nA propagacao de risco ganhou.\nO risco caiu.\nOutra propagação.\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "flow.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "notas.md").write_text("# Fora do cofre\n\npropagação de risco\n", encoding="utf-8")
    return tmp_path


def test_normalizar_ignora_acentos_maiusculas_e_separadores():
    assert buscar.normalizar("Propagação_de-Risco") == "propagacao de risco"


def test_termos_tiram_palavras_de_parada_mas_guardam_a_expressao():
    assert buscar.termos_da_busca("Propagação de risco") == (["propagacao", "risco"], "propagacao de risco")
    assert buscar.termos_da_busca("de") == (["de"], "de")


def test_notas_exigem_todos_os_termos_e_poem_o_titulo_na_frente(tmp_path):
    root = _cofre(tmp_path)
    achados = buscar.buscar_notas(["propagacao", "risco"], root, frase="propagacao de risco")
    assert [r["caminho"] for r in achados] == ["glossario/propagacao.md", "resultados.md"]  # src/ fica fora
    assert achados[1]["linhas"][0] == (3, "A propagacao de risco ganhou.")  # a expressão inteira vem antes
    assert buscar.buscar_notas(["propagacao", "inexistente"], root) == []


def test_codigo_acha_pelo_nome_e_mostra_so_vizinhos_do_repositorio():
    grafo = {
        "nodes": [
            {"id": "a", "label": "propagate_risk()", "file_type": "code", "source_file": "src/flow.py",
             "source_location": "L10", "_callable": True},
            {"id": "b", "label": "main()", "file_type": "code", "source_file": "scripts/x.py", "_callable": True},
            {"id": "c", "label": "networkx", "file_type": "code", "source_file": ""},
        ],
        "links": [{"source": "b", "target": "a", "relation": "calls"},
                  {"source": "a", "target": "c", "relation": "calls"}],
    }
    [achado] = buscar.buscar_codigo(["propagate", "risk"], grafo)
    assert achado["onde"] == "src/flow.py:L10"
    assert achado["chamado_por"] == ["main()"]
    assert achado["chama"] == []  # networkx é biblioteca, não código do repositório


def test_codigo_citado_conta_as_notas_que_apontam_para_cada_py(tmp_path):
    arquivo = tmp_path / "grafo.json"
    arquivo.write_text(json.dumps({"arestas": [
        {"de": "a.md", "para": "src/flow.py", "tipo": "arquivo"},
        {"de": "b.md", "para": "src/flow.py", "tipo": "arquivo"},
        {"de": "b.md", "para": "reports/x.png", "tipo": "arquivo"},
        {"de": "c.md", "para": "src/outro.py", "tipo": "arquivo"},
    ]}), encoding="utf-8")
    assert buscar.codigo_citado(["a.md", "b.md"], arquivo) == [("src/flow.py", 2)]
