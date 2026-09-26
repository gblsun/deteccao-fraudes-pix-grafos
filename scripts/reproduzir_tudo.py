"""Refaz todos os resultados da pesquisa, na ordem certa.

Uso, na raiz do repositório:
    python scripts/reproduzir_tudo.py              # completo, com as sementes do relatório (algumas horas)
    python scripts/reproduzir_tudo.py --rapido     # poucas sementes, em reports_teste/: só confere que tudo roda
    python scripts/reproduzir_tudo.py --refazer    # não reaproveita o progresso salvo das avaliações longas
    python scripts/reproduzir_tudo.py --extras     # + rede, ilustrações, grafos e relatório; abre Graphify e Obsidian
    python scripts/reproduzir_tudo.py --etapas dataset experimento   # só algumas etapas
    python scripts/reproduzir_tudo.py --listar     # mostra as etapas, o tempo médio e os comandos, sem rodar

Com a configuração versionada, o modo completo reproduz os arquivos de reports/
(o dataset usa --seed 42 e as avaliações têm sementes fixas). Cada script grava um
*_meta.json com o commit e a configuração usados. O AMLworld só entra se já tiver sido
importado para data/external/ (ver data/README.md).

Tempo médio: cada execução anota a duração de cada etapa em data/tempos_reproduzir.csv
(fora do git, porque depende da máquina). A média sai desse histórico; sem histórico, vale
a duração gravada no *_meta.json da etapa e, por último, o tempo aproximado de
scripts/mapa-dos-scripts.md (só no modo completo).
"""

import argparse
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parents[1]
RESULTADOS = ("dataset", "experimento", "robustez", "cenarios", "online", "atributos", "propagacao", "fraudar",
              "gnn", "externo")
EXTRAS = ("rede", "ilustracoes", "notas", "graphify", "relatorio")
AMLWORLD = ("amlworld_pix", "amlworld")
HISTORICO = ROOT / "data" / "tempos_reproduzir.csv"
# *_meta.json de cada etapa, relativo à pasta de saída: dá o tempo quando ainda não há histórico
META = {"experimento": "results/metricas_meta.json", "robustez": "results/robustez_meta.json",
        "cenarios": "results/cenarios_meta.json", "online": "results/online_meta.json",
        "atributos": "results/atributos_meta.json", "propagacao": "results/propagacao_meta.json",
        "fraudar": "results/fraudar_meta.json", "gnn": "results/gnn_meta.json"}
# tempo aproximado do modo completo (scripts/mapa-dos-scripts.md), para etapas sem *_meta.json nem histórico
APROXIMADO = {"dataset": 10, "online": 30 * 60, "fraudar": 17 * 60, "gnn": 25 * 60, "rede": 60, "ilustracoes": 60,
              "notas": 5, "graphify": 30, "relatorio": 20}


def graphify() -> str | None:
    """O executável do Graphify (ver docs/obsidian.md), ou ``None`` se não estiver instalado."""
    local = Path(sys.executable).parent / ("graphify.exe" if os.name == "nt" else "graphify")
    return str(local) if local.exists() else shutil.which("graphify")


def plano(rapido: bool, refazer: bool, saida: str, dados: str) -> list[tuple[str, str, list[str]]]:
    """Todas as etapas, em ordem, como (nome, descrição, comando)."""
    py = sys.executable
    sementes = "2" if rapido else "10"
    poucas = "2" if rapido else "5"
    online = ["--cenarios", "realista", "--sementes", "1"] if rapido else ["--sementes", "3"]
    opcao_refazer = ["--refazer"] if refazer else []
    atributos = (Path(dados).parent / "processed" / "features.csv").as_posix()
    etapas = [
        ("dataset", "dataset sintético (semente 42)",
         [py, "scripts/gerar_dataset.py", "--seed", "42", "--saida", dados]),
        ("experimento", "uma rodada completa",
         [py, "scripts/rodar_experimento.py", "--dados", dados, "--atributos", atributos, "--saida", saida]),
        ("robustez", f"robustez ({sementes} sementes)",
         [py, "scripts/avaliar_robustez.py", "--sementes", sementes, "--saida", saida]),
        ("cenarios", "cenários de dificuldade",
         [py, "scripts/avaliar_cenarios.py", "--sementes", sementes, "--saida", saida]),
        ("online", "detecção a tempo",
         [py, "scripts/avaliar_deteccao_online.py", *online, "--saida", saida, *opcao_refazer]),
        ("atributos", "ablação e teto supervisionado",
         [py, "scripts/avaliar_atributos.py", "--sementes", poucas, "--saida", saida]),
        ("propagacao", "culpa por associação",
         [py, "scripts/avaliar_propagacao.py", "--sementes", sementes, "--saida", saida]),
        ("fraudar", "FRAUDAR (blocos densos)",
         [py, "scripts/avaliar_fraudar.py", "--sementes", sementes, "--saida", saida]),
    ]
    if importlib.util.find_spec("torch"):  # dependência opcional: pip install -e ".[gnn]"
        etapas.append(("gnn", "redes neurais para grafos (DOMINANT e GraphSAGE)",
                       [py, "scripts/avaliar_gnn.py", "--sementes", poucas, "--saida", saida]))
    if not rapido:  # cada janela do AMLworld leva minutos
        for nome in AMLWORLD:
            if (ROOT / "data" / "external" / nome).exists():
                etapas.append(("externo", f"AMLworld ({nome})",
                               [py, "scripts/avaliar_externo.py", "--dados", f"data/external/{nome}",
                                "--saida", f"{saida}/amlworld", *opcao_refazer]))
    etapas += [
        ("rede", "página HTML da rede inteira",
         [py, "scripts/visualizar_rede.py", "--dados", dados, "--saida", f"{saida}/estudos/rede_completa.html"]),
        ("ilustracoes", "ilustrações do README",
         [py, "scripts/gerar_ilustracoes.py", "--saida", f"{saida}/figures"]),
        ("notas", "grafo de notas do Obsidian", [py, "scripts/exportar_grafo_de_notas.py"]),
    ]
    exe = graphify()
    if exe:
        etapas.append(("graphify", "grafo do código (Graphify)", [exe, "update", "."]))
    etapas.append(("relatorio", "relatório (docx em relatorio/saida/)", [py, "scripts/gerar_relatorio.py"]))
    return etapas


def tempos_medios(modo: str, saida: str) -> dict[str, float]:
    """Duração média de cada etapa no histórico desta máquina; sem histórico, a do *_meta.json."""
    medias = dict(APROXIMADO) if modo == "completo" else {}
    for etapa, meta in META.items():
        path = ROOT / saida / meta
        if path.exists():
            duracao = json.loads(path.read_text(encoding="utf-8")).get("duracao_s")
            if duracao is not None:
                medias[etapa] = float(duracao)
    if HISTORICO.exists():
        vistas: dict[str, list[float]] = {}
        with HISTORICO.open(encoding="utf-8", newline="") as f:
            for linha in csv.DictReader(f):
                if linha["modo"] == modo:
                    vistas.setdefault(linha["etapa"], []).append(float(linha["duracao_s"]))
        medias.update({etapa: sum(v) / len(v) for etapa, v in vistas.items()})
    return medias


def formatar(segundos: float | None) -> str:
    if segundos is None:
        return "?"
    if segundos < 60:
        return f"{segundos:.0f} s"
    if segundos < 3600:
        return f"{segundos / 60:.0f} min"
    return f"{segundos // 3600:.0f} h {segundos % 3600 / 60:02.0f} min"


def anotar(modo: str, etapa: str, duracao: float) -> None:
    """Acrescenta a duração de uma etapa ao histórico (data/ não é versionado)."""
    novo = not HISTORICO.exists()
    HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    with HISTORICO.open("a", encoding="utf-8", newline="") as f:
        escrita = csv.writer(f)
        if novo:
            escrita.writerow(["data", "modo", "etapa", "duracao_s"])
        escrita.writerow([datetime.now().isoformat(timespec="seconds"), modo, etapa, round(duracao)])


def abrir(alvo: str) -> None:
    """Abre um arquivo ou URI no programa padrão do sistema; se falhar, só avisa."""
    try:
        if sys.platform == "win32":
            os.startfile(alvo)
        else:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", alvo], check=True)
    except (OSError, subprocess.CalledProcessError) as erro:
        print(f"não consegui abrir {alvo}: {erro}")


def para_abrir(saida: str) -> list[str]:
    """O que o --extras abre no fim: a rede, a página do Graphify e o cofre do Obsidian."""
    alvos = [ROOT / saida / "estudos" / "rede_completa.html", ROOT / "graphify-out" / "graph.html"]
    return [str(a) for a in alvos if a.exists()] + [f"obsidian://open?path={ROOT}"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Refaz todos os resultados da pesquisa, na ordem certa.")
    parser.add_argument("--rapido", action="store_true", help="poucas sementes, em reports_teste/, sem AMLworld")
    parser.add_argument("--refazer", action="store_true", help="recalcula o progresso salvo das avaliações longas")
    parser.add_argument("--extras", action="store_true",
                        help="roda também rede, ilustrações, grafos e relatório, e abre Graphify e Obsidian no fim")
    parser.add_argument("--sem-abrir", action="store_true", help="com --extras, não abre nada no fim")
    parser.add_argument("--etapas", nargs="+", choices=RESULTADOS + EXTRAS, default=None,
                        help="roda só estas etapas (padrão: todas as de resultado, mais as extras com --extras)")
    parser.add_argument("--listar", action="store_true", help="mostra as etapas, o tempo médio e os comandos")
    parser.add_argument("--saida", default=None, help="pasta dos resultados (padrão: reports ou reports_teste)")
    parser.add_argument("--dados", default="data/synthetic", help="pasta do dataset sintético")
    args = parser.parse_args()

    saida = args.saida or ("reports_teste" if args.rapido else "reports")
    modo = "rapido" if args.rapido else "completo"
    escolhidas = args.etapas or list(RESULTADOS + (EXTRAS if args.extras else ()))
    etapas = [e for e in plano(args.rapido, args.refazer, saida, args.dados) if e[0] in escolhidas]
    nomes = [e[0] for e in etapas]
    if "externo" in escolhidas and "externo" not in nomes:
        print("AMLworld pulado: " + ("modo rápido (cada janela leva minutos)." if args.rapido
                                      else "não importado (ver data/README.md)."))
    if "gnn" in escolhidas and "gnn" not in nomes:
        print('GNN pulada: torch não instalado (pip install -e ".[gnn]").')
    if "graphify" in escolhidas and "graphify" not in nomes:
        print("Graphify não instalado: pulado (pip install graphifyy, ver docs/obsidian.md).")
    medias = tempos_medios(modo, saida)
    abre = args.extras and not args.sem_abrir

    if args.listar:
        for nome, descricao, comando in etapas:
            programa = "python" if comando[0] == sys.executable else Path(comando[0]).stem
            print(f"{nome:<12} {descricao:<38} ~{formatar(medias.get(nome)):<9} {programa} {' '.join(comando[1:])}")
        sem = [n for n in nomes if n not in medias]
        conhecido = sum(medias[n] for n in nomes if n in medias) if len(sem) < len(nomes) else None
        print(f"\ntotal estimado: ~{formatar(conhecido)}"
              + (f" (sem estimativa para: {', '.join(sem)})" if sem else ""))
        if abre:
            print("no fim, abre: " + ", ".join(para_abrir(saida)))
        return

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    feitas = []
    for nome, descricao, comando in etapas:
        print(f"\n== {descricao} (média ~{formatar(medias.get(nome))})", flush=True)
        inicio = time.time()
        # o que decide é o código de saída: avisos no stderr (do SciPy, por exemplo) não são erro
        if subprocess.run(comando, cwd=ROOT, env=env).returncode != 0:
            sys.exit(f"falhou: {descricao} (etapa {nome})")
        duracao = time.time() - inicio
        anotar(modo, nome, duracao)
        feitas.append((nome, duracao))
        print(f"   pronto em {formatar(duracao)}", flush=True)

    medias = tempos_medios(modo, saida)
    print("\nTempo de cada etapa (desta vez / média nesta máquina):")
    for nome, duracao in feitas:
        print(f"   {nome:<12} {formatar(duracao):>9} / {formatar(medias.get(nome))}")
    print(f"   {'total':<12} {formatar(sum(d for _, d in feitas)):>9}")
    print(f"\nTudo pronto. Resultados em {saida}/.")
    if abre:
        for alvo in para_abrir(saida):
            abrir(alvo)


if __name__ == "__main__":
    main()
