"""Gera o relatório a partir dos capítulos em Markdown de relatorio/capitulos/.

Junta os capítulos em ordem, resolve as citações ``[@chave]`` com
docs/referencias.bib no estilo ABNT (relatorio/abnt.csl) e grava em
relatorio/saida/ (fora do git). Usa o Pandoc que vem com o pacote
pypandoc_binary, então não é preciso instalar nada no sistema.

Uso:
    pip install -e ".[relatorio]"
    python scripts/gerar_relatorio.py                    # relatorio/saida/relatorio.docx
    python scripts/gerar_relatorio.py --formato html     # página única, com as figuras embutidas
    python scripts/gerar_relatorio.py --formato pdf      # precisa de LaTeX instalado
"""

import argparse
from pathlib import Path

import pypandoc

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "relatorio"


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera o relatório com o Pandoc.")
    parser.add_argument("--formato", choices=["docx", "html", "pdf"], default="docx")
    parser.add_argument("--saida", help="arquivo de saída (padrão: relatorio/saida/relatorio.<formato>)")
    args = parser.parse_args()

    chapters = sorted((REPORT / "capitulos").glob("*.md"))
    out = Path(args.saida) if args.saida else REPORT / "saida" / f"relatorio.{args.formato}"
    out.parent.mkdir(parents=True, exist_ok=True)
    extra = [
        "--citeproc",
        f"--metadata-file={REPORT / 'metadados.yaml'}",
        f"--bibliography={ROOT / 'docs' / 'referencias.bib'}",
        f"--csl={REPORT / 'abnt.csl'}",
        f"--resource-path={REPORT / 'capitulos'}",  # as figuras usam caminhos relativos aos capítulos
        "--toc",
        "--number-sections",
    ]
    if args.formato == "html":
        extra += ["--standalone", "--embed-resources", "--mathml"]
    pypandoc.convert_file([str(c) for c in chapters], to=args.formato, outputfile=str(out), extra_args=extra)
    print(f"{len(chapters)} capítulos -> {out}")


if __name__ == "__main__":
    main()
