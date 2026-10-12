"""Exporta o grafo de notas do cofre do Obsidian para JSON, para agentes de IA consultarem.

O Obsidian mostra as notas e os links entre elas como um grafo, mas só na tela. Este
script grava o mesmo grafo em docs/grafo-de-notas.json: cada nota (caminho, título e
tags do frontmatter) e cada link relativo que sai dela, seja para outra nota ou para um
arquivo do repositório (código, figura, notebook). Um agente responde "o que está ligado
a X?" lendo um arquivo só, sem abrir dezenas de notas.

Segue as mesmas regras do cofre (ver docs/obsidian.md): pastas ocultas e os filtros de
.obsidian/app.json (README.md, src/, data/...) ficam de fora como notas, mas links para
arquivos dessas pastas continuam registrados.

Exemplos:
    python scripts/ferramentas/exportar_grafo_de_notas.py             # grava docs/grafo-de-notas.json
    python scripts/ferramentas/exportar_grafo_de_notas.py --verificar # só confere se o arquivo está atualizado
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
SAIDA = ROOT / "docs" / "grafo-de-notas.json"
CODE = re.compile(r"(`{3,}).*?\1|`[^`\n]*`", re.DOTALL)  # blocos e trechos de código: exemplos, não links
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
TAGS = re.compile(r"^---\ntags: \[(.+)\]\n---")
TITULO = re.compile(r"^# (.+)$", re.MULTILINE)


def _filtros_do_cofre(root: Path) -> list[re.Pattern]:
    """Os userIgnoreFilters do Obsidian como regex: "/.../" já é regex, o resto é prefixo de caminho."""
    filtros = json.loads((root / ".obsidian" / "app.json").read_text(encoding="utf-8")).get("userIgnoreFilters", [])
    return [re.compile(f[1:-1]) if f.startswith("/") and f.endswith("/") else re.compile("^" + re.escape(f))
            for f in filtros]


def notas_do_cofre(root: Path = ROOT) -> list[Path]:
    """Os arquivos .md que o Obsidian mostra no grafo, em ordem."""
    filtros = _filtros_do_cofre(root)
    notas = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if any(parte.startswith(".") for parte in path.relative_to(root).parts):
            continue
        if not any(f.search(rel) for f in filtros):
            notas.append(path)
    return sorted(notas, key=lambda p: p.relative_to(root).as_posix())


def grafo_de_notas(root: Path = ROOT) -> dict:
    """Nós (notas do cofre) e arestas (links relativos para notas ou arquivos que existem)."""
    notas = notas_do_cofre(root)
    caminhos_das_notas = {p.relative_to(root).as_posix() for p in notas}
    nos, arestas = [], []
    for path in notas:
        texto = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        tags = TAGS.match(texto)
        titulo = TITULO.search(texto)
        nos.append({
            "caminho": rel,
            "titulo": titulo.group(1).strip() if titulo else path.stem,
            "tags": [t.strip() for t in tags.group(1).split(",")] if tags else [],
        })
        destinos = set()
        for alvo in LINK.findall(CODE.sub("", texto)):
            if alvo.startswith(("http://", "https://", "mailto:")) or "{{" in alvo:
                continue
            destino = (path.parent / alvo).resolve()
            if not destino.exists() or not destino.is_relative_to(root.resolve()):
                continue
            destino_rel = destino.relative_to(root.resolve()).as_posix()
            if destino_rel != rel:
                destinos.add(destino_rel)
        for destino_rel in sorted(destinos):
            tipo = "nota" if destino_rel in caminhos_das_notas else "arquivo"
            arestas.append({"de": rel, "para": destino_rel, "tipo": tipo})
    return {
        "descricao": "Grafo de notas do cofre do Obsidian (gerado por scripts/ferramentas/exportar_grafo_de_notas.py; "
                     "não edite à mão).",
        "nos": nos,
        "arestas": arestas,
    }


def como_json(grafo: dict) -> str:
    """O texto exato que vai para o arquivo (estável, para o teste comparar)."""
    return json.dumps(grafo, ensure_ascii=False, indent=1) + "\n"


def main() -> None:
    """Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--saida", type=Path, default=SAIDA, help="arquivo JSON de saída")
    parser.add_argument("--verificar", action="store_true", help="não grava; sai com erro se o arquivo estiver velho")
    args = parser.parse_args()

    grafo = grafo_de_notas()
    texto = como_json(grafo)
    if args.verificar:
        atual = args.saida.read_text(encoding="utf-8") if args.saida.exists() else ""
        if atual != texto:
            sys.exit(f"{args.saida} desatualizado: rode python scripts/ferramentas/exportar_grafo_de_notas.py")
        print(f"{args.saida} está atualizado")
        return
    args.saida.write_text(texto, encoding="utf-8", newline="\n")
    notas = sum(a["tipo"] == "nota" for a in grafo["arestas"])
    print(f"{len(grafo['nos'])} notas, {notas} links entre notas, "
          f"{len(grafo['arestas']) - notas} links para arquivos -> {args.saida}")


if __name__ == "__main__":
    main()
