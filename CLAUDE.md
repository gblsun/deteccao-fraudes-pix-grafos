# Instruções para agentes

Pesquisa de iniciação científica sobre detecção de fraudes no Pix com teoria dos grafos
(pacote Python `pixfraud`). O repositório inteiro é também um cofre do Obsidian.

## Autoria

- Autor: Gabriel Muchon Pavanelli
- Orientador: Prof. Me. Kyung Moo Kim

## Regra principal: LGPD no contexto do Pix

O trabalho segue a LGPD (Lei nº 13.709/2018) e o sigilo bancário (Lei Complementar
nº 105/2001), que protege os dados de transações Pix.

- **Nenhum dado pessoal real de usuário do Pix** entra no repositório: nome de titular,
  CPF, chave Pix (CPF, e-mail, telefone ou aleatória), agência e conta, identificador de
  transação ou qualquer dado que permita reidentificar uma conta. Os dados daqui são
  sintéticos (gerados pelo `pixfraud`) ou estatísticas agregadas e públicas do Banco Central.
- Identificadores sintéticos não imitam formatos reais: nada de CPF válido, telefone ou
  e-mail com cara de verdadeiro em código, exemplos, figuras ou notas.
- Dataset externo com dados de pessoas: fica em `data/` (fora do git), só anonimizado ou
  pseudonimizado, com o mínimo de atributos necessário (princípio da necessidade, art. 6º,
  III) e só para a pesquisa (art. 7º, IV). Resultados publicados são agregados.
- Nomes: os da autoria (acima) podem aparecer, e citar autores externos em referências é
  normal. Outras pessoas (colegas, participantes de reuniões) não são nomeadas nas notas.

## Como se orientar

- Comece por [llms.txt](llms.txt) e [docs/mapa-da-pesquisa.md](docs/mapa-da-pesquisa.md).
- Para achar relações entre notas ("o que fala de PageRank?", "que leituras sustentam
  este resultado?"), consulte [docs/grafo-de-notas.json](docs/grafo-de-notas.json): cada
  nota com título e tags, e cada link dela para outra nota ou para um arquivo de código.
  É o grafo do Obsidian em JSON; leia as notas encontradas depois.
- Para perguntas sobre o **código** (quem chama esta função, o que quebra se eu mudar
  aquilo, como um script chega num módulo), use o grafo do Graphify antes de fazer grep:
  leia `graphify-out/GRAPH_REPORT.md` e consulte com `.venv\Scripts\graphify affected "graph_features"`,
  `graphify path "A" "B"`, `graphify explain "X"` ou `graphify query "..."`. Depois de mudar
  o código, `graphify update .` (local, sem LLM). Detalhes em [docs/obsidian.md](docs/obsidian.md).
- Ao ler a documentação de uma pasta, abra a **nota-mapa** (`scripts/mapa-dos-scripts.md`,
  `docs/glossario/glossario.md`...), não o `README.md`, que é só um ponteiro para o GitHub.

## Ao editar notas

- Links Markdown relativos (`[texto](../caminho.md)`), nunca `[[wikilinks]]`.
- Toda nota nova tem frontmatter `tags: [...]` com uma das tags de
  [docs/obsidian.md](docs/obsidian.md); pasta nova com documentação segue o padrão
  nota-mapa + `README.md`, e entra no `llms.txt`.
- Depois de criar, renomear ou religar notas, rode
  `python scripts/exportar_grafo_de_notas.py` e `pytest tests/test_docs.py`.

## Código

- Python ≥ 3.10; `pip install -e ".[dev]"`; `pytest -m "not lento"` para o ciclo rápido;
  `ruff check .` antes de commitar.
- Scripts rodam da raiz do repositório; ver [scripts/mapa-dos-scripts.md](scripts/mapa-dos-scripts.md).
- `python scripts/reproduzir_tudo.py` refaz o pipeline inteiro (horas); `--rapido` confere
  que tudo roda em `reports_teste/`, `--etapas` roda só uma parte e `--listar` mostra os comandos.
