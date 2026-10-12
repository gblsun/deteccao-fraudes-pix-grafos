---
tags: [meta]
---

# Notas da pesquisa no Obsidian

O repositório inteiro funciona como um cofre (*vault*) do [Obsidian](https://obsidian.md):
os arquivos `.md` já são as notas. O Obsidian serve para **escrever e ligar** as notas
(fichamentos, diário, atas, resultados). O código continua no VS Code e no Jupyter, e o
git continua sendo o backup e o histórico.

## Abrir

1. Instale o Obsidian e escolha **Abrir pasta como cofre** (*Open folder as vault*).
2. Selecione a **raiz do repositório** (a pasta `deteccao-fraudes-pix-grafos`), e não
   `docs/`: só assim as figuras de `reports/` aparecem dentro de `docs/resultados.md`.
3. Se o Obsidian perguntar, confie no cofre (a configuração vem do repositório).

A configuração já vem pronta em `.obsidian/`:

| Ajuste | Valor | Por quê |
|--------|-------|---------|
| Formato dos links | Markdown, caminho relativo | os mesmos links funcionam no GitHub |
| Atualizar links ao mover/renomear | sim | reorganizar pastas não quebra nada |
| Pasta de anexos | `docs/anexos/` | imagens coladas nas notas não se espalham |
| Arquivos excluídos | `.venv/`, `data/`, `src/`, `.pytest_cache/`, e qualquer `README.md` (regex) | a busca e o grafo mostram só as notas com nome próprio |
| Modelos | `docs/modelos/` | fichamento, reunião e diário, já com a tag de cada tipo |
| Notas diárias | `docs/diario/AAAA-MM-DD.md` | diário de pesquisa |
| Cores do grafo | `.obsidian/graph.json` | por tipo de nota (ver abaixo) |

Se os comandos de modelos ou de nota diária não aparecerem, ative os plugins principais
**Modelos** (*Templates*) e **Notas diárias** (*Daily notes*) em Configurações →
Plugins principais.

## Por que nenhuma nota se chama "README"

O Obsidian rotula cada nó do grafo pelo **nome do arquivo**. Como quase toda pasta do
repositório tem um `README.md` (é o que o GitHub mostra ao abrir a pasta), um cofre com
vários arquivos chamados "README" vira um grafo com vários nós idênticos e ilegíveis.

A solução: cada pasta documentada tem uma **nota-mapa com nome próprio** — por exemplo,
`scripts/mapa-dos-scripts.md`, `docs/glossario/glossario.md`, `estudos/trilha-de-estudos.md`
— e o `README.md` da pasta vira um ponteiro de três linhas só para o GitHub. A
configuração exclui todo `README.md` do cofre (`userIgnoreFilters` em `.obsidian/app.json`,
com um regex), então só as notas com nome aparecem no grafo. Ao criar uma pasta nova com
documentação própria, siga o padrão: `nome-da-pasta/nome-descritivo.md` + um `README.md`
apontando para ela.

## Cores do grafo, por tipo de nota

Cada nota do cofre de pesquisa tem uma tag no frontmatter, e `.obsidian/graph.json` colore
o grafo por ela:

| Tag | Cor | Notas |
|-----|-----|-------|
| `mapa` | azul | as notas-mapa de cada pasta (a raiz do grafo), incluindo notas-índice como `rede-pix.md` e `revisao-bibliografica.md` |
| `leitura` | verde | os fichamentos de `docs/leituras/` |
| `glossario` | roxo | os termos de `docs/glossario/` |
| `diario` / `ata` | laranja | as notas datadas de `docs/diario/` e `docs/reunioes/` |
| `resultado` / `metodo` | vermelho | `docs/resultados.md` e `docs/modelos.md` |
| `pesquisa` | azul-petróleo | `docs/proposta.md` e `docs/cronograma.md` |
| `meta` | cinza | documentação sobre o próprio cofre (esta nota) |
| `relatorio` | marrom | os capítulos de `relatorio/capitulos/` |
| `ideia` | dourado | as notas de `docs/futuro/` |
| (por caminho) | ciano | tudo em `estudos/` |

Os modelos de `docs/modelos/` já colocam a tag certa em cada nota nova. Se criar uma nota
sem passar pelo modelo, acrescente o frontmatter à mão:

```markdown
---
tags: [leitura]
---
```

Para ver as cores, abra a aba **Grafo** (ícone de rede na barra lateral) — elas já vêm
carregadas do repositório, sem precisar configurar de novo.

Regra geral: **toda nota do cofre tem uma tag**, com duas exceções — os `README.md`
(nem entram no cofre) e as notas de `estudos/`, já coloridas por caminho. O teste
`tests/test_docs.py::test_every_vault_note_has_tags_frontmatter` garante isso.

## Para agentes e ferramentas de IA

O arquivo [`llms.txt`](../llms.txt), na raiz, segue a convenção
[llmstxt.org](https://llmstxt.org): um resumo do projeto e uma lista de pontos de entrada,
para um agente que não consegue abrir o grafo do Obsidian entender a estrutura do
repositório rapidamente. Ele existe **além** do grafo, não em vez dele — continua valendo
o mesmo padrão nota-mapa + README, e o `llms.txt` deve ser atualizado quando um ponto de
entrada novo (uma pasta documentada, uma seção grande) for criado.

Três peças deixam o cofre legível para um agente:

| Arquivo | Para quê |
|---------|----------|
| [`CLAUDE.md`](../CLAUDE.md) | instruções que o Claude Code carrega sozinho ao abrir o repositório (a regra da LGPD, a autoria, por onde começar, como editar notas) |
| [`llms.txt`](../llms.txt) | resumo e pontos de entrada, para qualquer ferramenta de IA |
| [`grafo-de-notas.json`](grafo-de-notas.json) | o grafo do Obsidian em JSON: cada nota (título, tags) e cada link dela, para outra nota ou para um arquivo de código |

O JSON é gerado por `python scripts/ferramentas/exportar_grafo_de_notas.py`, com as mesmas regras de
exclusão do cofre. Rode de novo depois de criar, renomear ou religar notas; o teste
`tests/test_docs.py::test_notes_graph_json_is_up_to_date` avisa se esquecer.

### Grafo de conhecimento do código (Graphify)

O grafo de notas liga documentação. Para o **código**, o repositório usa o
[Graphify](https://github.com/Graphify-Labs/graphify): ele lê os `.py` pela árvore
sintática (sem LLM, sem custo, sempre o mesmo resultado) e monta um grafo de módulos,
funções e classes ligados por `imports`, `calls` e `uses`. A saída fica em
`graphify-out/`, fora do cofre (está nos filtros de `.obsidian/app.json`): só
`graph.json` e `GRAPH_REPORT.md` (resumo, nós centrais, comunidades) são versionados.

```powershell
pip install graphifyy                      # no .venv, fora das dependências do pacote
graphify extract . --code-only             # do zero
graphify cluster-only . --no-label         # refaz o GRAPH_REPORT.md sem chamar LLM
graphify update .                          # depois de mudar o código
graphify affected "graph_features"         # o que chama esta função (e quebra se ela mudar)
graphify path "prepare" "graph_features"  # prepare -> build_features -> graph_features
graphify explain "propagate_risk"
```

### Busca única nos dois grafos

`python scripts/ferramentas/buscar.py termo` procura ao mesmo tempo no grafo do código (nome das
funções, com quem chama e o que chamam) e no **texto** de todas as notas do cofre,
inclusive as que o Graphify deixa de fora (leituras, diário, atas). Ignora acentos,
maiúsculas e `_`/`-`, descarta palavras como "de" e "para" e põe na frente a nota cujo
título tem os termos. No fim lista os `.py` citados nas notas achadas: é a ponte entre o
português das notas e o inglês do código.

```text
> python scripts/ferramentas/buscar.py "propagação de risco" --limite 3
## Código (0)
## Notas (3)
- docs/glossario/propagacao-de-risco.md  "Propagação de risco (culpa por associação)"
...
## Código citado nessas notas
- src/pixfraud/flow.py (3), ...
```

`--so codigo` ou `--so notas` restringe, e `--limite N` muda o número de resultados. Se o
grafo do código estiver mais velho que os `.py`, a busca avisa para rodar `graphify update .`.

`python scripts/reproduzir_tudo.py --etapas notas graphify --extras` atualiza os dois
grafos (notas e código) e abre a página do Graphify no navegador e este cofre no Obsidian
(a URI `obsidian://` só funciona se o cofre já tiver sido aberto uma vez).

O `.graphifyignore` tira do grafo o `docs/proposta-original.pdf` (arquivo de submissão),
`data/`, `reports/`, os notebooks e as notas que não falam do código (leituras, diário,
atas, ideias futuras, modelos de nota e relatório), que já estão no grafo de notas. O `graphify update .` também lê as notas em Markdown,
mas só a estrutura (títulos e links), localmente e sem LLM. A leitura *semântica* dos
docs (conceitos e relações extraídos do texto) exigiria mandar o texto para um LLM, e
fica de fora de propósito: as notas já estão ligadas pelo grafo de notas. Se um dia
quiser, rode `/graphify .` dentro do Claude Code, depois de conferir o `.graphifyignore`.

A figura [`grafo_do_codigo.png`](../reports/ilustracoes/grafo_do_codigo.png) resume esse grafo
por arquivo, e [`grafo_de_notas.png`](../reports/ilustracoes/grafo_de_notas.png) desenha o
grafo de notas com as cores do Obsidian; as duas saem de
`python scripts/ferramentas/ilustrar_grafos_de_conhecimento.py`.

| Papel | Ferramenta |
|-------|-----------|
| escrever e ligar notas, ver o grafo de notas | Obsidian |
| agente achar relações entre notas | `grafo-de-notas.json` |
| agente achar relações no código | Graphify (`graphify-out/`) |

Por que não as alternativas, por enquanto: **Microsoft GraphRAG** foi feito para muitos
documentos sem estrutura e reindexar custa muitas chamadas de LLM; **LangGraph** orquestra
agentes, não guarda conhecimento; **Memgraph** é para grafos em tempo real (caberia na
[detecção em tempo real](futuro/ia-agentica-tempo-real.md), não na documentação);
**Neo4j** exige servidor e só compensa com muito mais dados. Se um dia fizer sentido, o
`graphify export neo4j` leva o mesmo grafo para lá.

Para usar as notas pelo Claude Desktop ou claude.ai (sem acesso aos arquivos), um caminho
opcional é um servidor MCP do Obsidian (plugin da comunidade *Local REST API* + um
servidor MCP que fale com ele); no Claude Code não é necessário, porque ele já lê os
arquivos.

## Rotina

| Quando | O que fazer | Onde |
|--------|-------------|------|
| terminou uma leitura | nova nota com a chave do `.bib` como nome, depois **Modelos: Inserir modelo** → `fichamento`; acrescentar uma linha no índice | `docs/leituras/`, [revisao-bibliografica.md](revisao-bibliografica.md) |
| dia de trabalho na pesquisa | **Notas diárias: Abrir a nota de hoje** (já vem com o modelo): o que rodou, o que deu errado, o que foi decidido e por quê | `docs/diario/` |
| reunião de orientação | nova nota `AAAA-MM-DD`, depois inserir o modelo `reuniao` | `docs/reunioes/` |
| saiu um resultado | ligar o resultado às leituras e decisões que o explicam | [resultados.md](resultados.md) |
| apareceu um termo técnico novo | nota em `docs/glossario/`, a partir do índice; linkar na primeira ocorrência em `resultados.md` ou `modelos.md` | [glossario.md](glossario/glossario.md) |
| surgiu uma ideia de trabalho futuro | nova nota em `docs/futuro/`, tag `ideia`; acrescentar uma linha no índice | [ideias-futuras.md](futuro/ideias-futuras.md) |

O diário é o que mais ajuda no fim: na escrita do relatório (meses 11 e 12), a
justificativa de cada escolha já está registrada, com data.

Para ligar notas, digite `[` e escolha o arquivo, ou arraste o arquivo para dentro da
nota. Com a configuração acima, o link sai como `[texto](../caminho.md)`, que também
funciona no GitHub. Evite `[[wikilinks]]`, que o GitHub não entende.

## Plugins da comunidade (opcionais)

- **Tasks**: junta numa lista só os `- [ ]` espalhados pelas atas e pelo diário. Numa nota
  qualquer, escreva:

  ````markdown
  ```tasks
  not done
  path includes docs/
  ```
  ````

  No GitHub esse bloco aparece como código, o que não atrapalha.
- **Zotero Integration**: cria o fichamento a partir do Zotero, com título, autores,
  resumo e os seus destaques do PDF. Combine com o Better BibTeX para manter o
  `referencias.bib` atualizado.

Plugins e aparência ficam só na sua máquina (o `.gitignore` versiona apenas `app.json`,
`templates.json` e `daily-notes.json`).

## Regras

- **LGPD**: nenhum dado pessoal real de usuário do Pix nas notas, e nenhuma pessoa além
  do autor e do orientador nomeada (ver [CLAUDE.md](../CLAUDE.md)). Anotações pessoais
  ficam num cofre separado, fora desta pasta.
- Commits pelo VS Code ou pelo terminal, como o resto do projeto. Plugins de git
  automático não são necessários.
- Notebooks (`.ipynb`) não abrem no Obsidian: para citá-los, use um link comum para o
  arquivo.
