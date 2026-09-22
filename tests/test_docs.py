"""Testes da documentação: links que funcionam, docstrings e um README em cada pasta."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
FOLDERS_WITH_README = ["app", "configs", "data", "docs", "estudos", "notebooks", "relatorio", "reports", "scripts",
                       "src/pixfraud", "tests"]
MARKDOWN = sorted({ROOT / "README.md", *(p for f in FOLDERS_WITH_README for p in (ROOT / f).rglob("*.md"))})
CODE = re.compile(r"(`{3,}).*?\1|`[^`\n]*`", re.DOTALL)  # blocos e trechos de código: exemplos, não links
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")


@pytest.mark.parametrize("folder", FOLDERS_WITH_README)
def test_every_folder_has_a_readme(folder):
    assert (ROOT / folder / "README.md").exists()


@pytest.mark.parametrize("path", MARKDOWN, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_point_to_existing_files(path):
    text = CODE.sub("", path.read_text(encoding="utf-8"))
    targets = [t for t in LINK.findall(text) if not t.startswith(("http://", "https://", "mailto:")) and "{{" not in t]
    missing = [t for t in targets if not (path.parent / t).exists()]
    assert not missing, f"links quebrados em {path.relative_to(ROOT)}: {missing}"


@pytest.mark.parametrize("path", sorted((ROOT / "src" / "pixfraud").glob("*.py")), ids=lambda p: p.name)
def test_public_code_has_docstrings(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assert ast.get_docstring(tree), f"{path.name} sem docstring de módulo"
    public = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_")]
    missing = [n.name for n in public if not ast.get_docstring(n)]
    assert not missing, f"{path.name}: sem docstring em {missing}"
