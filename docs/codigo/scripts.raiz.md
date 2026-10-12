---
tags: [codigo]
---

# `scripts/ (raiz)`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Pontos de entrada da pesquisa, uma pasta por etapa. Guia da pasta: [mapa-dos-scripts.md](../../scripts/mapa-dos-scripts.md) · [mapa do código](mapa-do-codigo.md)

## [`reproduzir_tudo.py`](../../scripts/reproduzir_tudo.py)

Refaz todos os resultados da pesquisa, na ordem certa.

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

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--rapido` | desligada | poucas sementes, em reports_teste/, sem AMLworld |
| `--refazer` | desligada | recalcula o progresso salvo das avaliações longas |
| `--extras` | desligada | roda também rede, ilustrações, grafos e relatório, e abre Graphify e Obsidian no fim |
| `--sem-abrir` | desligada | com --extras, não abre nada no fim |
| `--etapas` | `None` | roda só estas etapas (padrão: todas as de resultado, mais as extras com --extras) |
| `--listar` | desligada | mostra as etapas, o tempo médio e os comandos |
| `--saida` | `None` | pasta dos resultados (padrão: reports ou reports_teste) |
| `--dados` | `'data/synthetic'` | pasta do dataset sintético |

**Funções**

- `def gnn_disponivel() -> bool`: O extra "gnn" está instalado e carrega? (o Windows pode bloquear uma DLL do torch)
- `def graphify() -> str | None`: O executável do Graphify (ver docs/obsidian.md), ou `None` se não estiver instalado.
- `def plano(rapido: bool, refazer: bool, saida: str, dados: str) -> list[tuple[str, str, list[str]]]`: Todas as etapas, em ordem, como (nome, descrição, comando).
- `def tempos_medios(modo: str, saida: str) -> dict[str, float]`: Duração média de cada etapa no histórico desta máquina; sem histórico, a do *_meta.json.
- `def formatar(segundos: float | None) -> str`: Duração legível: segundos, minutos ou horas e minutos.
- `def anotar(modo: str, etapa: str, duracao: float) -> None`: Acrescenta a duração de uma etapa ao histórico (data/ não é versionado).
- `def abrir(alvo: str) -> None`: Abre um arquivo ou URI no programa padrão do sistema; se falhar, só avisa.
- `def para_abrir(saida: str) -> list[str]`: O que o --extras abre no fim: a rede, a página do Graphify e o cofre do Obsidian.
- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
