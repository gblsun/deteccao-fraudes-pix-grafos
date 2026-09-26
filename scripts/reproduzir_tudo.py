"""Refaz todos os resultados da pesquisa, na ordem certa.

Uso, na raiz do repositório:
    python scripts/reproduzir_tudo.py              # completo, com as sementes do relatório (algumas horas)
    python scripts/reproduzir_tudo.py --rapido     # poucas sementes, em reports_teste/: só confere que tudo roda
    python scripts/reproduzir_tudo.py --refazer    # não reaproveita o progresso salvo das avaliações longas
    python scripts/reproduzir_tudo.py --etapas dataset experimento   # só algumas etapas
    python scripts/reproduzir_tudo.py --listar     # mostra as etapas e os comandos, sem rodar

Com a configuração versionada, o modo completo reproduz os arquivos de reports/
(o dataset usa --seed 42 e as avaliações têm sementes fixas). Cada script grava um
*_meta.json com o commit e a configuração usados. O AMLworld só entra se já tiver sido
importado para data/external/ (ver data/README.md).
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parents[1]
ETAPAS = ("dataset", "experimento", "robustez", "cenarios", "online", "atributos", "propagacao", "externo")
AMLWORLD = ("amlworld_pix", "amlworld")


def plano(rapido: bool, refazer: bool, saida: str, dados: str) -> list[tuple[str, str, list[str]]]:
    """As etapas, em ordem, como (nome, descrição, argumentos do python)."""
    sementes = "2" if rapido else "10"
    poucas = "2" if rapido else "5"
    online = ["--cenarios", "realista", "--sementes", "1"] if rapido else ["--sementes", "3"]
    opcao_refazer = ["--refazer"] if refazer else []
    atributos = (Path(dados).parent / "processed" / "features.csv").as_posix()
    etapas = [
        ("dataset", "dataset sintético (semente 42)", ["scripts/gerar_dataset.py", "--seed", "42", "--saida", dados]),
        ("experimento", "uma rodada completa",
         ["scripts/rodar_experimento.py", "--dados", dados, "--atributos", atributos, "--saida", saida]),
        ("robustez", f"robustez ({sementes} sementes)",
         ["scripts/avaliar_robustez.py", "--sementes", sementes, "--saida", saida]),
        ("cenarios", "cenários de dificuldade",
         ["scripts/avaliar_cenarios.py", "--sementes", sementes, "--saida", saida]),
        ("online", "detecção a tempo",
         ["scripts/avaliar_deteccao_online.py", *online, "--saida", saida, *opcao_refazer]),
        ("atributos", "ablação e teto supervisionado",
         ["scripts/avaliar_atributos.py", "--sementes", poucas, "--saida", saida]),
        ("propagacao", "culpa por associação",
         ["scripts/avaliar_propagacao.py", "--sementes", sementes, "--saida", saida]),
    ]
    if not rapido:  # cada janela do AMLworld leva minutos
        for nome in AMLWORLD:
            if (ROOT / "data" / "external" / nome).exists():
                etapas.append(("externo", f"AMLworld ({nome})",
                               ["scripts/avaliar_externo.py", "--dados", f"data/external/{nome}",
                                "--saida", f"{saida}/amlworld", *opcao_refazer]))
    return etapas


def main() -> None:
    parser = argparse.ArgumentParser(description="Refaz todos os resultados da pesquisa, na ordem certa.")
    parser.add_argument("--rapido", action="store_true", help="poucas sementes, em reports_teste/, sem AMLworld")
    parser.add_argument("--refazer", action="store_true", help="recalcula o progresso salvo das avaliações longas")
    parser.add_argument("--etapas", nargs="+", choices=ETAPAS, default=list(ETAPAS), help="roda só estas etapas")
    parser.add_argument("--listar", action="store_true", help="mostra as etapas e os comandos, sem rodar")
    parser.add_argument("--saida", default=None, help="pasta dos resultados (padrão: reports ou reports_teste)")
    parser.add_argument("--dados", default="data/synthetic", help="pasta do dataset sintético")
    args = parser.parse_args()

    saida = args.saida or ("reports_teste" if args.rapido else "reports")
    etapas = [e for e in plano(args.rapido, args.refazer, saida, args.dados) if e[0] in args.etapas]
    if "externo" in args.etapas and not args.rapido and not any(e[0] == "externo" for e in etapas):
        print("AMLworld não importado: pulado (ver data/README.md).")
    if args.rapido and "externo" in args.etapas:
        print("AMLworld pulado no modo rápido (cada janela leva minutos).")

    if args.listar:
        for nome, descricao, argumentos in etapas:
            print(f"{nome:<12} {descricao:<35} python {' '.join(argumentos)}")
        return

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for nome, descricao, argumentos in etapas:
        print(f"\n== {descricao}", flush=True)
        inicio = time.time()
        # o que decide é o código de saída: avisos no stderr (do SciPy, por exemplo) não são erro
        if subprocess.run([sys.executable, *argumentos], cwd=ROOT, env=env).returncode != 0:
            sys.exit(f"falhou: {descricao} (etapa {nome})")
        print(f"   pronto em {time.time() - inicio:,.0f} s", flush=True)

    print(f"\nTudo pronto. Resultados em {saida}/.")


if __name__ == "__main__":
    main()
