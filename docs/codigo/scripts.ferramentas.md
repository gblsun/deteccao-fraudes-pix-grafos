---
tags: [codigo]
---

# `scripts/ferramentas/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Busca, grafo de notas, ilustrações, documentação do código e relatório. Guia da pasta: [README.md](../../scripts/ferramentas/README.md) · [mapa do código](mapa-do-codigo.md)

## [`buscar.py`](../../scripts/ferramentas/buscar.py)

Busca única no código e nas notas da pesquisa, com saída curta para agentes de IA.

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
    python scripts/ferramentas/buscar.py pagerank
    python scripts/ferramentas/buscar.py "propagate risk"            # código e notas
    python scripts/ferramentas/buscar.py falso positivo --so notas
    python scripts/ferramentas/buscar.py graph_features --so codigo --limite 3

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `termos` | obrigatória | palavras procuradas (todas precisam aparecer) |
| `--so` | — | procura só no código ou só nas notas |
| `--limite` | `8` | resultados por seção (padrão 8) |

**Funções**

- `def normalizar(texto: str) -> str`: Minúsculas, sem acentos, e "_" ou "-" viram espaço.
- `def termos_da_busca(texto: str) -> tuple[list[str], str]`: Os termos (sem palavras de parada, a menos que só haja elas) e a expressão inteira normalizada.
- `def _casa(termos: list[str], texto: str) -> bool`: Todos os termos aparecem no texto?
- `def _carregar_exportador()`: Importa `exportar_grafo_de_notas.py` como módulo (ele não é um pacote).
- `def buscar_notas(termos: list[str], root: Path=ROOT, limite: int=8, linhas: int=2, frase: str='') -> list[dict]`: Notas do cofre que têm todos os termos, das mais citadas para as menos.
- `def buscar_codigo(termos: list[str], grafo: dict, limite: int=8, com_vizinhos: int=3) -> list[dict]`: Nós de código do Graphify cujo nome tem todos os termos, dos mais ligados para os menos.
- `def codigo_citado(caminhos: list[str], arquivo: Path=GRAFO_DE_NOTAS) -> list[tuple[str, int]]`: Arquivos .py para onde as notas dadas apontam, com quantas delas apontam (mais citados primeiro).
- `def grafo_velho(grafo: dict, root: Path=ROOT) -> list[str]`: Arquivos .py mudados desde o commit em que o grafo do código foi gerado (vazio se em dia).
- `def _lista(nomes: list[str]) -> str`: Os primeiros nomes separados por vírgula, com quantos ficaram de fora.
- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py)

Gera a documentação do código em docs/codigo/: uma nota por módulo, por pasta de scripts e por diretório.

Tudo sai das docstrings e da árvore de sintaxe do Python (`ast`), sem importar
nada, então a documentação acompanha o código: depois de mudar uma função, rode
este script de novo. O `tests/test_docs.py` acusa quando as notas ficam velhas.

O que é gerado (notas do Obsidian, com a tag `codigo`):

* `pixfraud.<módulo>.md`: uma por módulo do pacote, com a docstring do
  módulo, cada classe e função pública (assinatura e docstring inteira), as
  funções internas numa lista curta e **quem usa** o módulo (outros módulos,
  scripts, app e testes), o que liga as notas no grafo do Obsidian;
* `scripts.<pasta>.md`: uma por pasta de `scripts/`, com cada script, as
  opções de linha de comando (lidas do `argparse`) e as funções dele;
* `app.md` (o explorador em Streamlit) e `testes.md` (cada arquivo de teste
  e o que ele testa);
* `diretorios.md`: todos os diretórios versionados, com o que guardam;
* `mapa-do-codigo.md`: a nota-mapa, que liga tudo.

Uso:
    python scripts/ferramentas/documentar_codigo.py
    python scripts/ferramentas/documentar_codigo.py --verificar   # só confere, sem gravar

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--verificar` | desligada | não grava; sai com erro se alguma nota estiver velha |

**Funções**

- `def main() -> None`: Gera (ou, com `--verificar`, só confere) as notas de docs/codigo/.
- `def build_notes() -> dict[str, str]`: Todas as notas, como {nome do arquivo: texto}.
- `def module_note(name: str, path: Path, users: set[str]) -> str`: A nota de um módulo: docstring, classes, funções públicas e internas, e quem o usa.
- `def _definitions(tree: ast.Module) -> tuple[list, list]`: Classes e funções do nível do módulo, separadas em públicas e internas.
- `def _definition_block(node, level: int=3) -> list[str]`: Título, assinatura e docstring de uma classe ou função (com os métodos públicos de uma classe).
- `def _signature(node) -> str`: Assinatura legível: `def nome(argumentos) -> retorno` ou `class Nome(bases)`.
- `def _first_line(node) -> str`: O primeiro parágrafo da docstring, numa linha.
- `def _markdown(text: str) -> str`: Docstring em reStructuredText para Markdown: `código` vira `código` e `::` vira `:`.
- `def _module_name(path: Path) -> str`: `src/pixfraud/models/base.py` -> `pixfraud.models.base` (o `__init__` vira o pacote).
- `def _who_imports(modules: dict[str, Path]) -> dict[str, set[str]]`: Para cada módulo, os links das notas que o importam (módulos, pastas de scripts, app, testes).
- `def _imports(path: Path, modules: dict[str, Path]) -> set[str]`: Módulos do pacote importados por `path` (`import pixfraud.x`, `from pixfraud import x`...).
- `def _note_of(path: Path) -> str`: Link Markdown para a nota que documenta `path`.
- `def scripts_note(folder: str) -> str`: A nota de uma pasta de scripts: cada script, suas opções de linha de comando e suas funções.
- `def _script_block(path: Path) -> list[str]`: Um script: docstring, opções do `argparse` e funções.
- `def _cli_options(tree: ast.Module) -> list[tuple[str, str, str]]`: As opções de `parser.add_argument(...)`: nome, valor padrão e ajuda.
- `def _short(text: str, limit: int=40) -> str`: Texto cortado em `limit` caracteres (os padrões longos, como listas de cenários).
- `def app_note() -> str`: A nota do explorador em Streamlit.
- `def tests_note() -> str`: A nota dos testes: cada arquivo e cada teste, com o que ele confere.
- `def tracked_directories() -> list[str]`: Os diretórios com algum arquivo versionado (sem as pastas results/ e figures/ de cada etapa).
- `def directories_note() -> str`: Todos os diretórios versionados, em árvore, com o que guardam e o guia de cada um.
- `def _guide(directory: str) -> str | None`: A nota-mapa ou o README do diretório (a nota-mapa primeiro), se houver.
- `def map_note(modules: dict[str, Path]) -> str`: A nota-mapa da documentação do código.
- `def _front(tag: str) -> list[str]`: Frontmatter do Obsidian com a tag da nota.
- `def _read(path: Path) -> str | None`: Conteúdo de `path`, ou `None` se não existir.

## [`exportar_grafo_de_notas.py`](../../scripts/ferramentas/exportar_grafo_de_notas.py)

Exporta o grafo de notas do cofre do Obsidian para JSON, para agentes de IA consultarem.

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

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--saida` | `SAIDA` | arquivo JSON de saída |
| `--verificar` | desligada | não grava; sai com erro se o arquivo estiver velho |

**Funções**

- `def _filtros_do_cofre(root: Path) -> list[re.Pattern]`: Os userIgnoreFilters do Obsidian como regex: "/.../" já é regex, o resto é prefixo de caminho.
- `def notas_do_cofre(root: Path=ROOT) -> list[Path]`: Os arquivos .md que o Obsidian mostra no grafo, em ordem.
- `def grafo_de_notas(root: Path=ROOT) -> dict`: Nós (notas do cofre) e arestas (links relativos para notas ou arquivos que existem).
- `def como_json(grafo: dict) -> str`: O texto exato que vai para o arquivo (estável, para o teste comparar).
- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`gerar_ilustracoes.py`](../../scripts/ferramentas/gerar_ilustracoes.py)

Gera as ilustrações do README: os padrões de fraude e a animação de uma quadrilha.

São figuras explicativas (não resultados): saem do gerador sintético e dos padrões de
`pixfraud.patterns`, com a mesma semente, então podem ser refeitas a qualquer momento.

Uso:
    python scripts/ferramentas/gerar_ilustracoes.py
    python scripts/ferramentas/gerar_ilustracoes.py --saida reports/ilustracoes

Saídas em reports/ilustracoes/:
    padroes_de_fraude.png   os seis padrões lado a lado
    quadrilha.gif           o dinheiro percorrendo uma quadrilha, hora a hora
    rede_exemplo.png        um recorte da rede sintética, colorido pelo papel de cada conta

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--saida` | `'reports/ilustracoes'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _legenda(papeis) -> list`: Itens de legenda só dos papéis que aparecem no desenho, na ordem de ROLE_COLORS.
- `def _padroes(path: Path) -> None`: Os seis padrões de fraude de `pixfraud.patterns`, lado a lado.
- `def _dataset_pequeno()`: Dataset com uma única quadrilha, pequeno o bastante para desenhar.
- `def _rede_exemplo(path: Path) -> None`: A quadrilha dentro do movimento normal: é isso que o detector precisa achar.
- `def _animacao(path: Path, intervalo_h: int=2) -> None`: O dinheiro percorrendo a quadrilha, hora a hora: golpes, repasses e a coletora.

## [`gerar_relatorio.py`](../../scripts/ferramentas/gerar_relatorio.py)

Gera o relatório a partir dos capítulos em Markdown de relatorio/capitulos/.

Junta os capítulos em ordem, resolve as citações `[@chave]` com
docs/referencias.bib no estilo ABNT (relatorio/abnt.csl) e grava em
relatorio/saida/ (fora do git). Usa o Pandoc que vem com o pacote
pypandoc_binary, então não é preciso instalar nada no sistema.

Uso:
    pip install -e ".[relatorio]"
    python scripts/ferramentas/gerar_relatorio.py                    # relatorio/saida/relatorio.docx
    python scripts/ferramentas/gerar_relatorio.py --formato html     # página única, com as figuras embutidas
    python scripts/ferramentas/gerar_relatorio.py --formato pdf      # precisa de LaTeX instalado

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--formato` | `'docx'` |  |
| `--saida` | — | arquivo de saída (padrão: relatorio/saida/relatorio.<formato>) |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`ilustrar_grafos_de_conhecimento.py`](../../scripts/ferramentas/ilustrar_grafos_de_conhecimento.py)

Desenha os dois grafos de conhecimento do repositório para o README.

São figuras explicativas (não resultados da pesquisa):

- o grafo de notas do Obsidian (docs/grafo-de-notas.json), com as mesmas cores da aba
  Grafo do Obsidian (lidas de .obsidian/graph.json);
- o mapa do código do Graphify (graphify-out/graph.json), resumido por arquivo: cada nó é
  um arquivo .py e cada aresta junta as chamadas e imports de um arquivo para outro.

Rode antes `python scripts/ferramentas/exportar_grafo_de_notas.py` e `graphify update .` para que os
dois JSON estejam atualizados (ver docs/obsidian.md).

Uso:
    python scripts/ferramentas/ilustrar_grafos_de_conhecimento.py
    python scripts/ferramentas/ilustrar_grafos_de_conhecimento.py --saida reports/ilustracoes

Saídas:
    grafo_de_notas.png    notas e links, coloridos pelo tipo de nota
    grafo_do_codigo.png   arquivos .py e as dependências entre eles

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--saida` | `ROOT / 'reports' / 'ilustracoes'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _grupos_do_obsidian() -> list[tuple[str, list[str], str]]`: Os grupos de cor de .obsidian/graph.json como (nome, condições, cor em hex).
- `def _rotulo(consulta: str) -> str`: "tag:diario OR tag:ata" -> "diario / ata", para a legenda.
- `def _cor_da_nota(no: dict, grupos) -> str`: Primeiro grupo que casa com a nota, como no Obsidian ("tag:x" ou "path:pasta").
- `def _grafo_de_notas(destino: Path) -> None`: Desenha o grafo de notas do Obsidian, com as cores dos grupos do cofre.
- `def _pasta(arquivo: str) -> str | None`: A pasta de código de um arquivo .py (ou `None` fora delas).
- `def _grafo_do_codigo(destino: Path) -> None`: Desenha o mapa do código: arquivos e as ligações entre pastas, pelo Graphify.

## [`ilustrar_testes.py`](../../scripts/ferramentas/ilustrar_testes.py)

Figuras didáticas dos testes de hipótese: uma por etapa da pesquisa.

Cada figura tem três partes (ver docs/plano-de-testes-estatisticos.md):

1. **a estatística do teste sob a hipótese nula**, com a zona crítica de
   α = 5% sombreada e o valor observado como linha vertical: dá para ver se o
   resultado caiu na zona crítica;
2. **os dados contra a curva normal**: histograma com a normal ajustada, Q-Q
   plot e o teste de Shapiro-Wilk. A cauda pesada é o que justifica os testes
   não paramétricos (Mann-Whitney, Kruskal-Wallis, Wilcoxon) no lugar do t;
3. a ressalva: com milhares de contas, quase tudo cai muito além da zona
   crítica, e por isso o tamanho do efeito importa mais que o p.

As estatísticas de cada etapa:

* 01_dados: o z do modelo nulo (reciprocidade da rede contra grafos aleatórios
  de mesmos graus);
* 02_exploracao: o z do Mann-Whitney (fraude × legítima) e o H do
  Kruskal-Wallis (6 papéis) contra a χ², no atributo de maior efeito;
* 03_modelos: a AP do DBSCAN contra o nulo da permutação do gabarito;
* 04_avaliacao: o t pareado e o z do Wilcoxon entre dois modelos e o χ² do
  Friedman entre todos, a partir de reports/03_modelos/results/modelos_execucoes.csv.

As etapas 01 a 03 usam uma rede de validação (semente 1001), gerada na hora.

Saídas: reports/<etapa>/figures/testes_<etapa>.png

Uso:
    python scripts/ferramentas/ilustrar_testes.py
    python scripts/ferramentas/ilustrar_testes.py --cenario realista --etapas 02_exploracao

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenario` | `'calibrado'` |  |
| `--etapas` | `list(STAGES)` |  |
| `--execucoes` | `'reports/03_modelos/results/modelos_exe…` | AP por (cenário, semente, modelo), para a etapa 04 |
| `--saida` | `'reports'` | pasta com uma subpasta por etapa |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _grid(fig, top: int)`: Linha de cima: `top` painéis da estatística; linha de baixo: histograma e Q-Q plot.
- `def _stage_data(fig, prepared, where)`: Etapa 01: z do modelo nulo da reciprocidade e o grau de entrada contra a normal.
- `def _stage_exploration(fig, prepared, roles, where)`: Etapa 02: z do Mann-Whitney e H do Kruskal-Wallis no atributo de maior efeito.
- `def _stage_models(fig, prepared, config, where)`: Etapa 03: a AP do DBSCAN contra o nulo da permutação do gabarito.
- `def _stage_evaluation(fig, runs_path: Path)`: Etapa 04: t pareado, z do Wilcoxon e χ² do Friedman a partir das execuções gravadas.
