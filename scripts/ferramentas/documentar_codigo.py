"""Gera a documentação do código em docs/codigo/: uma nota por módulo, por pasta de scripts e por diretório.

Tudo sai das docstrings e da árvore de sintaxe do Python (``ast``), sem importar
nada, então a documentação acompanha o código: depois de mudar uma função, rode
este script de novo. O ``tests/test_docs.py`` acusa quando as notas ficam velhas.

O que é gerado (notas do Obsidian, com a tag ``codigo``):

* ``pixfraud.<módulo>.md``: uma por módulo do pacote, com a docstring do
  módulo, cada classe e função pública (assinatura e docstring inteira), as
  funções internas numa lista curta e **quem usa** o módulo (outros módulos,
  scripts, app e testes), o que liga as notas no grafo do Obsidian;
* ``scripts.<pasta>.md``: uma por pasta de ``scripts/``, com cada script, as
  opções de linha de comando (lidas do ``argparse``) e as funções dele;
* ``app.md`` (o explorador em Streamlit) e ``testes.md`` (cada arquivo de teste
  e o que ele testa);
* ``diretorios.md``: todos os diretórios versionados, com o que guardam;
* ``mapa-do-codigo.md``: a nota-mapa, que liga tudo.

Uso:
    python scripts/ferramentas/documentar_codigo.py
    python scripts/ferramentas/documentar_codigo.py --verificar   # só confere, sem gravar
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "codigo"
PACKAGE = ROOT / "src" / "pixfraud"
HEADER = ("> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das "
          "docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.")

# O que cada diretório guarda. Todo diretório versionado precisa estar aqui (tests/test_docs.py confere).
DIRECTORIES = {
    ".claude": "configuração do Claude Code para este repositório (permissões, leituras bloqueadas)",
    ".github": "configuração do GitHub",
    ".github/workflows": "integração contínua: roda o lint e os testes a cada push",
    ".obsidian": "configuração do cofre do Obsidian (cores do grafo, plugins, espaço de trabalho)",
    ".vscode": "configuração do VS Code para o projeto",
    "app": "explorador interativo em Streamlit: gera redes, roda os modelos e mostra resultados",
    "configs": "parâmetros dos experimentos (YAML): simulação, atributos, modelos, cenários e grades de busca",
    "data": "dados (não versionados, só a estrutura): sintéticos, externos, do BCB e processados",
    "data/bcb": "estatísticas agregadas do Pix baixadas da API de dados abertos do Banco Central",
    "data/processed": "tabelas intermediárias, como os atributos de cada conta",
    "data/raw": "arquivos originais baixados (AMLworld, PaySim), antes da conversão",
    "data/synthetic": "o dataset sintético da semente 42 (contas e transações)",
    "docs": "documentação da pesquisa: proposta, cronograma, resultados, glossário, leituras, diário e atas",
    "docs/anexos": "anexos da documentação (figuras e arquivos citados nas notas)",
    "docs/codigo": "esta documentação do código, gerada a partir das docstrings",
    "docs/diario": "diário de pesquisa, uma nota por dia",
    "docs/futuro": "ideias de trabalhos futuros",
    "docs/glossario": "termos técnicos, fórmulas e onde cada um aparece no projeto",
    "docs/leituras": "fichamentos, um por leitura, com a chave do .bib como nome",
    "docs/modelos": "modelos de nota do Obsidian (fichamento, diário, reunião)",
    "docs/reunioes": "atas das reuniões de orientação",
    "estudos": "notebooks de estudo de teoria dos grafos e NetworkX, com gabarito",
    "estudos/dados": "pequenos CSVs de exemplo usados nos estudos",
    "graphify-out": "grafo do código gerado pelo Graphify (graph.json, relatório e página HTML)",
    "notebooks": "análises exploratórias da pesquisa em Jupyter",
    "relatorio": "o relatório final em Markdown, convertido pelo Pandoc",
    "relatorio/capitulos": "os capítulos do relatório",
    "reports": "resultados gerados pelos scripts, uma pasta por etapa da pesquisa",
    "reports/01_dados": "resultados da etapa 1: auditoria do gabarito e realismo do gerador",
    "reports/02_exploracao": "resultados da etapa 2: tipo de rede e inferência sobre os atributos",
    "reports/03_modelos": "resultados da etapa 3: rodada única, otimização e vitrine dos modelos",
    "reports/04_avaliacao": "resultados da etapa 4: robustez, cenários, ablação, propagação, GNN e sementes",
    "reports/05_interpretacao": "resultados da etapa 5: falsos positivos",
    "reports/amlworld": "validação externa no dataset AMLworld",
    "reports/coletor_ativo": "rodada à parte do cenário com a coletora que esvazia o dinheiro",
    "reports/estudos": "grafos gerados nos estudos e a rede inteira em HTML",
    "reports/ilustracoes": "figuras explicativas do README (não são resultados)",
    "reports/otimizado": "a vitrine dos modelos com os hiperparâmetros otimizados",
    "scripts": "pontos de entrada da pesquisa, uma pasta por etapa",
    "scripts/01_dados": "etapa 1: gerar, importar e baixar dados, auditar o gabarito, validar o realismo",
    "scripts/02_exploracao": "etapa 2: forma da rede, inferência sobre os atributos e visualização",
    "scripts/03_modelos": "etapa 3: rodada única, otimização dos hiperparâmetros e vitrine dos modelos",
    "scripts/04_avaliacao": "etapa 4: repetições com sementes e cenários e comparações com inferência",
    "scripts/05_interpretacao": "etapa 5: os erros dos modelos",
    "scripts/ferramentas": "busca, grafo de notas, ilustrações, documentação do código e relatório",
    "src": "código-fonte instalável",
    "src/pixfraud": "o pacote Python da pesquisa",
    "src/pixfraud/models": "os modelos de detecção, organizados por família",
    "src/pixfraud/models/semi_supervised": "modelos que partem de parte das fraudes já conhecida",
    "src/pixfraud/models/supervised": "tetos supervisionados, treinados com os rótulos",
    "src/pixfraud/models/supervised/neural": "redes neurais supervisionadas para grafos (GraphSAGE)",
    "src/pixfraud/models/supervised/trees": "árvores supervisionadas (Random Forest, gradient boosting)",
    "src/pixfraud/models/unsupervised": "detectores não supervisionados de anomalia",
    "src/pixfraud/models/unsupervised/boundary": "detectores de fronteira (One-Class SVM)",
    "src/pixfraud/models/unsupervised/graph": "detectores que usam só a estrutura do grafo (FRAUDAR, node2vec)",
    "src/pixfraud/models/unsupervised/isolation": "detectores por isolamento (Isolation Forest)",
    "src/pixfraud/models/unsupervised/neural": "redes neurais não supervisionadas (autoencoder, DOMINANT)",
    "src/pixfraud/models/unsupervised/proximity": "detectores por proximidade (DBSCAN, LOF, kNN, k-means)",
    "src/pixfraud/models/unsupervised/statistical": "detectores estatísticos (ECOD, PCA)",
    "src/pixfraud/tuning": "otimização de hiperparâmetros: espaço de busca e avaliação dos candidatos",
    "tests": "testes automáticos (pytest) do pacote, dos scripts e da documentação",
}
# nota-mapa ou README de cada diretório, quando houver
DIRECTORY_GUIDE = ("mapa-dos-*.md", "mapa-da-*.md", "mapa-do-*.md", "trilha-de-estudos.md", "glossario.md",
                   "diario-de-pesquisa.md", "atas-de-reuniao.md", "ideias-futuras.md", "README.md")
SCRIPT_FOLDERS = ("01_dados", "02_exploracao", "03_modelos", "04_avaliacao", "05_interpretacao", "ferramentas")


def main() -> None:
    """Gera (ou, com ``--verificar``, só confere) as notas de docs/codigo/."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verificar", action="store_true", help="não grava; sai com erro se alguma nota estiver velha")
    args = parser.parse_args()
    notes = build_notes()
    stale = [name for name, text in notes.items() if _read(OUT / name) != text]
    extra = sorted(p.name for p in OUT.glob("*.md") if p.name not in notes) if OUT.exists() else []
    if args.verificar:
        if stale or extra:
            print("docs/codigo desatualizado: " + ", ".join(stale + extra))
            print("rode: python scripts/ferramentas/documentar_codigo.py")
            sys.exit(1)
        print(f"docs/codigo em dia ({len(notes)} notas)")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name in stale:
        (OUT / name).write_text(notes[name], encoding="utf-8", newline="")
    for name in extra:
        (OUT / name).unlink()
    print(f"{len(notes)} notas em docs/codigo ({len(stale)} atualizadas, {len(extra)} removidas)")


def build_notes() -> dict[str, str]:
    """Todas as notas, como {nome do arquivo: texto}."""
    modules = {_module_name(p): p for p in sorted(PACKAGE.rglob("*.py"))}
    users = _who_imports(modules)
    notes = {f"{name}.md": module_note(name, path, users.get(name, set())) for name, path in modules.items()}
    for folder in SCRIPT_FOLDERS:
        notes[f"scripts.{folder}.md"] = scripts_note(folder)
    notes["scripts.raiz.md"] = scripts_note("")
    notes["app.md"] = app_note()
    notes["testes.md"] = tests_note()
    notes["diretorios.md"] = directories_note()
    notes["mapa-do-codigo.md"] = map_note(modules)
    notes["README.md"] = ("# Documentação do código\n\n"
                          "Este arquivo existe para o GitHub mostrar algo ao abrir a pasta. O conteúdo (uma nota "
                          "por módulo, por pasta de scripts e por diretório) está em "
                          "**[Mapa do código](mapa-do-codigo.md)**.\n")
    return notes


# ---- módulos do pacote ----

def module_note(name: str, path: Path, users: set[str]) -> str:
    """A nota de um módulo: docstring, classes, funções públicas e internas, e quem o usa."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT).as_posix()
    lines = _front("codigo") + [f"# `{name}`", "", HEADER, "",
                                f"Arquivo: [`{rel}`](../../{rel}) · [mapa do código](mapa-do-codigo.md)", ""]
    doc = ast.get_docstring(tree)
    lines += [_markdown(doc) if doc else "_Sem docstring de módulo._", ""]
    public, private = _definitions(tree)
    if public:
        lines += ["## Classes e funções", ""]
        for node in public:
            lines += _definition_block(node)
    if private:
        lines += ["## Funções internas", "", "Usadas só dentro do módulo (o nome começa com `_`).", ""]
        lines += [f"- `{_signature(node)}`: {_first_line(node)}" for node in private]
        lines.append("")
    lines += ["## Quem usa este módulo", ""]
    lines += [f"- {link}" for link in sorted(users)] if users else ["Nenhum outro arquivo importa este módulo."]
    return "\n".join(lines).rstrip() + "\n"


def _definitions(tree: ast.Module) -> tuple[list, list]:
    """Classes e funções do nível do módulo, separadas em públicas e internas."""
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    return [n for n in nodes if not n.name.startswith("_")], [n for n in nodes if n.name.startswith("_")]


def _definition_block(node, level: int = 3) -> list[str]:
    """Título, assinatura e docstring de uma classe ou função (com os métodos públicos de uma classe)."""
    kind = "classe" if isinstance(node, ast.ClassDef) else "função"
    lines = [f"{'#' * level} `{node.name}` ({kind})", "", "```python", _signature(node), "```", ""]
    doc = ast.get_docstring(node)
    lines += [_markdown(doc) if doc else "_Sem docstring._", ""]
    if isinstance(node, ast.ClassDef):
        methods = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and (not m.name.startswith("_") or m.name in ("__init__", "__call__"))]
        for method in methods:
            lines += [f"- `{_signature(method)}`: {_first_line(method)}"]
        if methods:
            lines.append("")
    return lines


def _signature(node) -> str:
    """Assinatura legível: ``def nome(argumentos) -> retorno`` ou ``class Nome(bases)``."""
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(b) for b in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"def {node.name}({ast.unparse(node.args)}){returns}"


def _first_line(node) -> str:
    """O primeiro parágrafo da docstring, numa linha."""
    doc = ast.get_docstring(node)
    return _markdown(doc.split("\n\n")[0]).replace("\n", " ") if doc else "_sem docstring_"


def _markdown(text: str) -> str:
    """Docstring em reStructuredText para Markdown: ``código`` vira `código` e ``::`` vira ``:``."""
    text = re.sub(r"``([^`]+)``", r"`\1`", text)
    text = text.replace("::\n", ":\n")
    return text.replace("|", "\\|") if text.lstrip().startswith("|") else text


def _module_name(path: Path) -> str:
    """``src/pixfraud/models/base.py`` -> ``pixfraud.models.base`` (o ``__init__`` vira o pacote)."""
    parts = list(path.relative_to(ROOT / "src").with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _who_imports(modules: dict[str, Path]) -> dict[str, set[str]]:
    """Para cada módulo, os links das notas que o importam (módulos, pastas de scripts, app, testes)."""
    users: dict[str, set[str]] = {}
    files = [*modules.values(), *sorted((ROOT / "scripts").rglob("*.py")), ROOT / "app" / "explorador.py",
             *sorted((ROOT / "tests").glob("*.py"))]
    for path in files:
        source = _note_of(path)
        own = _module_name(path) if path.is_relative_to(PACKAGE) else None
        for imported in _imports(path, modules):
            if imported != own:
                users.setdefault(imported, set()).add(source)
    return users


def _imports(path: Path, modules: dict[str, Path]) -> set[str]:
    """Módulos do pacote importados por ``path`` (``import pixfraud.x``, ``from pixfraud import x``...)."""
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "pixfraud":
            if node.level:
                continue
            found.add(node.module if node.module in modules else node.module.rsplit(".", 1)[0])
            for alias in node.names:
                if f"{node.module}.{alias.name}" in modules:
                    found.add(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.level and path.is_relative_to(PACKAGE):
            base = _module_name(path).split(".")
            base = base[: len(base) - node.level + (1 if path.name == "__init__.py" else 0)]
            target = ".".join(base + ([node.module] if node.module else []))
            if target in modules:
                found.add(target)
            for alias in node.names:
                if f"{target}.{alias.name}" in modules:
                    found.add(f"{target}.{alias.name}")
        elif isinstance(node, ast.Import):
            found |= {a.name for a in node.names if a.name in modules}
    return {m for m in found if m in modules}


def _note_of(path: Path) -> str:
    """Link Markdown para a nota que documenta ``path``."""
    rel = path.relative_to(ROOT)
    if rel.parts[0] == "src":
        name = _module_name(path)
        return f"[`{name}`]({name}.md)"
    if rel.parts[0] == "scripts":
        folder = rel.parts[1] if len(rel.parts) > 2 else "raiz"
        return f"[`{rel.as_posix()}`](scripts.{folder}.md)"
    if rel.parts[0] == "app":
        return f"[`{rel.as_posix()}`](app.md)"
    return f"[`{rel.as_posix()}`](testes.md)"


# ---- scripts, app e testes ----

def scripts_note(folder: str) -> str:
    """A nota de uma pasta de scripts: cada script, suas opções de linha de comando e suas funções."""
    base = ROOT / "scripts" / folder if folder else ROOT / "scripts"
    title = f"scripts/{folder}/" if folder else "scripts/ (raiz)"
    guide = f"../../scripts/{folder}/README.md" if folder else "../../scripts/mapa-dos-scripts.md"
    lines = _front("codigo") + [f"# `{title}`", "", HEADER, "",
                                f"{DIRECTORIES.get(PurePosixPath('scripts', folder).as_posix(), '').capitalize()}. "
                                f"Guia da pasta: [{Path(guide).name}]({guide}) · [mapa do código](mapa-do-codigo.md)",
                                ""]
    for path in sorted(base.glob("*.py")):
        lines += _script_block(path)
    return "\n".join(lines).rstrip() + "\n"


def _script_block(path: Path) -> list[str]:
    """Um script: docstring, opções do ``argparse`` e funções."""
    rel = path.relative_to(ROOT).as_posix()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = [f"## [`{path.name}`](../../{rel})", ""]
    doc = ast.get_docstring(tree)
    lines += [_markdown(doc) if doc else "_Sem docstring._", ""]
    options = _cli_options(tree)
    if options:
        lines += ["**Opções de linha de comando**", "", "| Opção | Padrão | Para quê |", "|---|---|---|"]
        lines += [f"| `{flag}` | {default} | {help_} |" for flag, default, help_ in options]
        lines.append("")
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    if functions:
        lines += ["**Funções**", ""]
        lines += [f"- `{_signature(n)}`: {_first_line(n)}" for n in functions]
        lines.append("")
    return lines


def _cli_options(tree: ast.Module) -> list[tuple[str, str, str]]:
    """As opções de ``parser.add_argument(...)``: nome, valor padrão e ajuda."""
    options = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument" and node.args):
            continue
        names = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if not names:
            continue
        keywords = {k.arg: k.value for k in node.keywords}
        default = keywords.get("default")
        action = keywords.get("action")
        if isinstance(action, ast.Constant) and action.value == "store_true":
            default_text = "desligada"
        elif default is None:
            default_text = "obrigatória" if not names[0].startswith("-") else "—"
        else:
            default_text = f"`{_short(ast.unparse(default))}`"
        help_node = keywords.get("help")
        help_text = help_node.value if isinstance(help_node, ast.Constant) else ""
        options.append((" / ".join(names), default_text, help_text.replace("|", "\\|").replace("%%", "%")))
    return options


def _short(text: str, limit: int = 40) -> str:
    """Texto cortado em ``limit`` caracteres (os padrões longos, como listas de cenários)."""
    text = text.replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def app_note() -> str:
    """A nota do explorador em Streamlit."""
    path = ROOT / "app" / "explorador.py"
    lines = _front("codigo") + ["# `app/explorador.py`", "", HEADER, "",
                                "Guia de uso: [guia do explorador](../../app/guia-do-explorador.md) · "
                                "[mapa do código](mapa-do-codigo.md)", ""]
    lines += _script_block(path)[2:]
    return "\n".join(lines).rstrip() + "\n"


def tests_note() -> str:
    """A nota dos testes: cada arquivo e cada teste, com o que ele confere."""
    lines = _front("codigo") + ["# Testes", "", HEADER, "",
                                "Como rodar e o que cada grupo cobre: [mapa dos testes](../../tests/mapa-dos-testes.md)"
                                " · [mapa do código](mapa-do-codigo.md)", ""]
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree)
        tests = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
        lines += [f"## [`{path.name}`](../../{rel})", "", _markdown(doc) if doc else "", ""]
        for node in tests:
            text = ast.get_docstring(node)
            lines.append(f"- `{node.name}`" + (f": {_markdown(text.split(chr(10) + chr(10))[0])}".replace("\n", " ")
                                               if text else ""))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ---- diretórios e mapa ----

def tracked_directories() -> list[str]:
    """Os diretórios com algum arquivo versionado (sem as pastas results/ e figures/ de cada etapa)."""
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    found = set()
    for line in files.splitlines():
        parent = PurePosixPath(line).parent
        while str(parent) != ".":
            found.add(str(parent))
            parent = parent.parent
    found.add("docs/codigo")
    return sorted(d for d in found if not d.endswith(("/results", "/figures")))


def directories_note() -> str:
    """Todos os diretórios versionados, em árvore, com o que guardam e o guia de cada um."""
    lines = _front("codigo") + ["# Diretórios", "", HEADER, "",
                                "Cada diretório do repositório e o que ele guarda. As pastas `results/` e `figures/` "
                                "de cada etapa ficam dentro de `reports/<etapa>/`. Ver também o "
                                "[mapa do código](mapa-do-codigo.md).", "",
                                "| Diretório | O que guarda | Guia |", "|---|---|---|"]
    for directory in tracked_directories():
        depth = directory.count("/")
        name = ("&nbsp;&nbsp;" * depth) + f"`{PurePosixPath(directory).name}/`"
        guide = _guide(directory)
        guide_link = f"[{Path(guide).name}](../../{guide})" if guide else ""
        lines.append(f"| {name} | {DIRECTORIES.get(directory, '**sem descrição**')} | {guide_link} |")
    return "\n".join(lines).rstrip() + "\n"


def _guide(directory: str) -> str | None:
    """A nota-mapa ou o README do diretório (a nota-mapa primeiro), se houver."""
    folder = ROOT / directory
    for pattern in DIRECTORY_GUIDE:
        match = sorted(folder.glob(pattern))
        if match:
            return match[0].relative_to(ROOT).as_posix()
    return None


def map_note(modules: dict[str, Path]) -> str:
    """A nota-mapa da documentação do código."""
    lines = _front("mapa") + ["# Mapa do código", "", HEADER, "",
                              "Uma nota por módulo do pacote `pixfraud`, por pasta de scripts e por diretório, geradas "
                              "a partir das docstrings. Cada nota de módulo diz quem o usa, e esses links aparecem no "
                              "grafo do Obsidian. Para o desenho de como as peças se encaixam, ver o "
                              "[README do pacote](../../src/pixfraud/README.md); para a ordem da pesquisa, o "
                              "[fluxo da pesquisa](../fluxo-da-pesquisa.md).", "",
                              "- [Diretórios](diretorios.md): todos, com o que guardam", "",
                              "## Pacote `pixfraud`", "", "| Módulo | O que faz |", "|---|---|"]
    for name, path in modules.items():
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
        summary = _markdown(doc.split("\n\n")[0]).replace("\n", " ").replace("|", "\\|")
        lines.append(f"| [`{name}`]({name}.md) | {summary} |")
    lines += ["", "## Scripts", "", "| Pasta | O que guarda |", "|---|---|"]
    for folder in ("", *SCRIPT_FOLDERS):
        key = PurePosixPath("scripts", folder).as_posix()
        label = f"scripts/{folder}/" if folder else "scripts/ (raiz)"
        lines.append(f"| [`{label}`](scripts.{folder or 'raiz'}.md) | {DIRECTORIES[key]} |")
    lines += ["", "## App e testes", "", "- [`app/explorador.py`](app.md): o explorador interativo em Streamlit",
              "- [Testes](testes.md): cada arquivo de teste e o que ele confere"]
    return "\n".join(lines).rstrip() + "\n"


def _front(tag: str) -> list[str]:
    """Frontmatter do Obsidian com a tag da nota."""
    return ["---", f"tags: [{tag}]", "---", ""]


def _read(path: Path) -> str | None:
    """Conteúdo de ``path``, ou ``None`` se não existir."""
    return path.read_text(encoding="utf-8") if path.exists() else None


if __name__ == "__main__":
    main()
