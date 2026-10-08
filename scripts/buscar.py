"""Busca única no código e nas notas da pesquisa, com saída curta para agentes de IA.

Junta os dois grafos (ver docs/obsidian.md) numa consulta só:

- **código**: funções, classes e arquivos do grafo do Graphify (graphify-out/graph.json),
  com onde ficam e, para os primeiros resultados, quem chama e o que chamam;
- **notas**: o texto de todas as notas do cofre do Obsidian (glossário, leituras, diário,
  atas, ideias, relatório...), com as linhas que casam e o número da linha;
- **código citado nas notas**: os .py para onde as notas achadas apontam. É a ponte entre
  o português das notas e o inglês do código ("propagação de risco" leva a flow.py).

A busca ignora maiúsculas, acentos e a diferença entre "_", "-" e espaço: "propagacao",
"Propagação" e "propagate risk" acham o que se espera. Com vários termos, o resultado
precisa ter todos; palavras curtas como "de" e "para" não contam como termo, mas a
expressão inteira sobe no ranking. Lê os arquivos direto, sem chamar o Graphify nem um LLM, e avisa se o
grafo do código estiver velho.

Exemplos:
    python scripts/buscar.py pagerank
    python scripts/buscar.py "propagate risk"            # código e notas
    python scripts/buscar.py falso positivo --so notas
    python scripts/buscar.py graph_features --so codigo --limite 3
"""

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
GRAFO_DO_CODIGO = ROOT / "graphify-out" / "graph.json"
LIGACOES = {"calls", "indirect_call", "uses"}  # arestas que contam como "chama"
VIZINHOS = 5  # nomes mostrados por lista de chamadores/chamados
LARGURA = 110  # corte das linhas de nota
GRAFO_DE_NOTAS = ROOT / "docs" / "grafo-de-notas.json"
PARADAS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "para",
           "por", "com", "um", "uma", "que", "se", "the", "of", "and", "to", "in", "for"}


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, e "_" ou "-" viram espaço."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[_\-]+", " ", sem_acento.lower())


def termos_da_busca(texto: str) -> tuple[list[str], str]:
    """Os termos (sem palavras de parada, a menos que só haja elas) e a expressão inteira normalizada."""
    palavras = normalizar(texto).split()
    termos = [p for p in palavras if p not in PARADAS] or palavras
    return list(dict.fromkeys(termos)), " ".join(palavras)


def _casa(termos: list[str], texto: str) -> bool:
    return all(t in texto for t in termos)


def _carregar_exportador():
    spec = importlib.util.spec_from_file_location("exportar", ROOT / "scripts" / "exportar_grafo_de_notas.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def buscar_notas(termos: list[str], root: Path = ROOT, limite: int = 8, linhas: int = 2,
                 frase: str = "") -> list[dict]:
    """Notas do cofre que têm todos os termos, das mais citadas para as menos.

    Cada resultado traz caminho, título, pontos e as melhores linhas (as que têm a
    expressão inteira, depois as com mais termos), com o número da linha. A expressão
    inteira vale 5 pontos por ocorrência, e todos os termos no título valem 50: a nota que
    define o assunto vem primeiro.
    """
    resultados = []
    for path in _carregar_exportador().notas_do_cofre(root):
        texto = path.read_text(encoding="utf-8")
        norm = normalizar(texto)
        if not _casa(termos, norm):
            continue
        titulo = next((linha[2:].strip() for linha in texto.splitlines() if linha.startswith("# ")), path.stem)
        candidatas = []
        for numero, linha in enumerate(texto.splitlines(), start=1):
            n = normalizar(linha)
            acertos = sum(t in n for t in termos) + (len(termos) if frase and frase in n else 0)
            if acertos:
                candidatas.append((-acertos, numero, linha.strip()))
        melhores = sorted(candidatas)[:linhas]
        no_titulo = _casa(termos, normalizar(titulo))
        resultados.append({
            "caminho": path.relative_to(root).as_posix(),
            "titulo": titulo,
            "pontos": sum(norm.count(t) for t in termos) + (5 * norm.count(frase) if frase else 0)
                      + (50 if no_titulo else 0),
            "linhas": [(numero, linha) for _, numero, linha in sorted(melhores, key=lambda c: c[1])],
        })
    resultados.sort(key=lambda r: (-r["pontos"], r["caminho"]))
    return resultados[:limite]


def buscar_codigo(termos: list[str], grafo: dict, limite: int = 8, com_vizinhos: int = 3) -> list[dict]:
    """Nós de código do Graphify cujo nome tem todos os termos, dos mais ligados para os menos.

    Os ``com_vizinhos`` primeiros trazem quem chama e o que chamam.
    """
    nos = {n["id"]: n for n in grafo["nodes"]}
    chamadores, chamados, grau = defaultdict(set), defaultdict(set), defaultdict(int)
    for aresta in grafo["links"]:
        grau[aresta["source"]] += 1
        grau[aresta["target"]] += 1
        if aresta["relation"] in LIGACOES:
            chamadores[aresta["target"]].add(aresta["source"])
            chamados[aresta["source"]].add(aresta["target"])

    achados = [n for n in nos.values()
               if n.get("file_type") == "code" and n.get("source_file") and _casa(termos, normalizar(n["label"]))]
    achados.sort(key=lambda n: (not n.get("_callable"), -grau[n["id"]], n["label"]))

    def nomes(ids: set) -> list[str]:  # só o que é do repositório: bibliotecas não têm source_file
        return sorted({nos[i]["label"] for i in ids if i in nos and nos[i].get("source_file")})

    resultados = []
    for posicao, no in enumerate(achados[:limite]):
        resultado = {"nome": no["label"], "onde": f"{no['source_file']}:{no.get('source_location', '')}".rstrip(":"),
                     "ligacoes": grau[no["id"]]}
        if posicao < com_vizinhos:
            resultado["chamado_por"] = nomes(chamadores[no["id"]])
            resultado["chama"] = nomes(chamados[no["id"]])
        resultados.append(resultado)
    return resultados


def codigo_citado(caminhos: list[str], arquivo: Path = GRAFO_DE_NOTAS) -> list[tuple[str, int]]:
    """Arquivos .py para onde as notas dadas apontam, com quantas delas apontam (mais citados primeiro)."""
    if not arquivo.exists():
        return []
    notas = set(caminhos)
    contagem = defaultdict(int)
    for aresta in json.loads(arquivo.read_text(encoding="utf-8"))["arestas"]:
        if aresta["de"] in notas and aresta["para"].endswith(".py"):
            contagem[aresta["para"]] += 1
    return sorted(contagem.items(), key=lambda c: (-c[1], c[0]))


def grafo_velho(grafo: dict, root: Path = ROOT) -> list[str]:
    """Arquivos .py mudados desde o commit em que o grafo do código foi gerado (vazio se em dia)."""
    commit = grafo.get("built_at_commit")
    if not commit:
        return []
    try:
        feito = subprocess.run(["git", "diff", "--name-only", commit, "--", "*.py"], cwd=root,
                               capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    return feito.stdout.split()


def _lista(nomes: list[str]) -> str:
    resto = len(nomes) - VIZINHOS
    return ", ".join(nomes[:VIZINHOS]) + (f" (+{resto})" if resto > 0 else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("termos", nargs="+", help="palavras procuradas (todas precisam aparecer)")
    parser.add_argument("--so", choices=["codigo", "notas"], help="procura só no código ou só nas notas")
    parser.add_argument("--limite", type=int, default=8, help="resultados por seção (padrão 8)")
    args = parser.parse_args()
    termos, frase = termos_da_busca(" ".join(args.termos))
    frase = frase if len(frase.split()) > 1 else ""

    if args.so != "notas":
        if not GRAFO_DO_CODIGO.exists():
            print("código: graphify-out/graph.json não existe (rode graphify update .)")
        else:
            grafo = json.loads(GRAFO_DO_CODIGO.read_text(encoding="utf-8"))
            velhos = grafo_velho(grafo)
            if velhos:
                print(f"[aviso] grafo do código velho ({len(velhos)} .py mudaram): rode graphify update .")
            achados = buscar_codigo(termos, grafo, args.limite)
            print(f"## Código ({len(achados)})")
            for r in achados:
                print(f"- {r['nome']}  {r['onde']}  [{r['ligacoes']} ligações]")
                if r.get("chamado_por"):
                    print(f"    chamado por: {_lista(r['chamado_por'])}")
                if r.get("chama"):
                    print(f"    chama: {_lista(r['chama'])}")

    if args.so != "codigo":
        achados = buscar_notas(termos, limite=args.limite, frase=frase)
        print(f"## Notas ({len(achados)})")
        for r in achados:
            print(f"- {r['caminho']}  \"{r['titulo']}\"")
            for numero, linha in r["linhas"]:
                corte = linha if len(linha) <= LARGURA else linha[:LARGURA - 1] + "…"
                print(f"    L{numero}: {corte}")
        citados = codigo_citado([r["caminho"] for r in achados])
        if citados:
            print("## Código citado nessas notas")
            print("- " + ", ".join(f"{caminho} ({n})" for caminho, n in citados[:args.limite]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
