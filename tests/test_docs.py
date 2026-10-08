"""Testes da documentação: links que funcionam, docstrings, README e mapa em cada pasta."""

import ast
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
# pasta -> nome da nota-mapa (o README da pasta é só um ponteiro para ela; ver docs/obsidian.md)
FOLDER_MAPS = {
    "app": "guia-do-explorador.md",
    "configs": "parametros-dos-experimentos.md",
    "data": None,  # data/README.md é a própria documentação, sem nota-mapa separada
    "docs": "mapa-da-pesquisa.md",
    "docs/diario": "diario-de-pesquisa.md",
    "docs/futuro": "ideias-futuras.md",
    "docs/glossario": "glossario.md",
    "docs/leituras": "mapa-das-leituras.md",
    "docs/reunioes": "atas-de-reuniao.md",
    "estudos": "trilha-de-estudos.md",
    "notebooks": "mapa-dos-notebooks.md",
    "relatorio": "mapa-do-relatorio.md",
    "reports": "mapa-dos-resultados.md",
    "scripts": "mapa-dos-scripts.md",
    "src/pixfraud": None,  # README técnico do pacote, não faz parte do cofre de pesquisa
    "src/pixfraud/models": "mapa-dos-modelos.md",
    "tests": "mapa-dos-testes.md",
}
FOLDERS_WITH_README = sorted(FOLDER_MAPS)
MARKDOWN = sorted({ROOT / "README.md", *(p for f in FOLDERS_WITH_README for p in (ROOT / f).rglob("*.md"))})
CODE = re.compile(r"(`{3,}).*?\1|`[^`\n]*`", re.DOTALL)  # blocos e trechos de código: exemplos, não links
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")


@pytest.mark.parametrize("folder", FOLDERS_WITH_README)
def test_every_folder_has_a_readme(folder):
    assert (ROOT / folder / "README.md").exists()


@pytest.mark.parametrize("folder", sorted(f for f, mapa in FOLDER_MAPS.items() if mapa))
def test_every_docs_folder_has_a_named_map_note(folder):
    """As pastas do cofre de pesquisa têm uma nota-mapa com nome próprio (não "README"),
    porque o Obsidian rotula cada nó do grafo pelo nome do arquivo."""
    assert (ROOT / folder / FOLDER_MAPS[folder]).exists()


NOTES_WITHOUT_TAG = {p for p in MARKDOWN if p.name == "README.md" or "estudos" in p.relative_to(ROOT).parts}


@pytest.mark.parametrize("path", sorted(set(MARKDOWN) - NOTES_WITHOUT_TAG), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_vault_note_has_tags_frontmatter(path):
    """Toda nota do cofre tem uma tag (para colorir o grafo); README e estudos/ ficam de
    fora de propósito (ver docs/obsidian.md)."""
    text = path.read_text(encoding="utf-8")
    assert re.match(r"^---\ntags: \[.+\]\n---", text), f"{path.relative_to(ROOT)}: sem frontmatter de tags"


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_point_to_existing_files(path):
    text = CODE.sub("", path.read_text(encoding="utf-8"))
    targets = [t for t in LINK.findall(text) if not t.startswith(("http://", "https://", "mailto:")) and "{{" not in t]
    missing = [t for t in targets if not (path.parent / t).exists()]
    assert not missing, f"links quebrados em {path.relative_to(ROOT)}: {missing}"


@pytest.mark.parametrize("path", sorted((ROOT / "src" / "pixfraud").rglob("*.py")),
                         ids=lambda p: str(p.relative_to(ROOT / "src" / "pixfraud")))
def test_public_code_has_docstrings(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assert ast.get_docstring(tree), f"{path.name} sem docstring de módulo"
    public = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_")]
    missing = [n.name for n in public if not ast.get_docstring(n)]
    assert not missing, f"{path.name}: sem docstring em {missing}"


def test_notes_graph_json_is_up_to_date():
    """docs/grafo-de-notas.json (o grafo do Obsidian para agentes de IA) acompanha as notas."""
    spec = importlib.util.spec_from_file_location("exportar", ROOT / "scripts" / "exportar_grafo_de_notas.py")
    exportar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exportar)
    saved = (ROOT / "docs" / "grafo-de-notas.json").read_text(encoding="utf-8")
    assert saved == exportar.como_json(exportar.grafo_de_notas(ROOT)), (
        "grafo de notas desatualizado: rode python scripts/exportar_grafo_de_notas.py"
    )


def test_code_graph_leaves_out_private_and_generated_files():
    """O grafo do Graphify (graphify-out/, ver docs/obsidian.md) não lê o PDF original da
    proposta (arquivo de submissão) nem dados e resultados gerados."""
    graph = ROOT / "graphify-out" / "graph.json"
    if not graph.exists():
        pytest.skip("grafo do Graphify ainda não gerado")
    text = graph.read_text(encoding="utf-8")
    for forbidden in ("proposta-original.pdf", "data/synthetic", "data/raw", "reports/results"):
        assert forbidden not in text, f"graphify-out/graph.json menciona {forbidden}: confira o .graphifyignore"
