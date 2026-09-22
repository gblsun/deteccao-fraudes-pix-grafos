# Revisão bibliográfica

Índice das leituras. Cada leitura tem o seu fichamento em `docs/leituras/<chave-bibtex>.md`,
com o nome igual à chave do [`referencias.bib`](referencias.bib), o que facilita citar depois
no relatório.

## Como fichar uma leitura

1. Acrescente a referência ao `referencias.bib` (o Zotero com Better BibTeX exporta pronto).
2. Crie `docs/leituras/<chave-bibtex>.md` a partir do modelo
   [`docs/modelos/fichamento.md`](modelos/fichamento.md). No Obsidian: nova nota na pasta
   `leituras` com a chave como nome e depois *Inserir modelo* (ver [obsidian.md](obsidian.md)).
3. Acrescente uma linha na tabela "Fichamentos" abaixo.

## Sugestões de leitura

Não constam na proposta original, mas são próximas do tema. Todas já estão no
`referencias.bib`.

| Chave                  | Por que ler                                                                          |
|------------------------|---------------------------------------------------------------------------------------|
| `akoglu2015graph`      | Survey clássico de detecção de anomalias em grafos: dá o mapa do estado da arte        |
| `lopezrojas2016paysim` | Simulador de transações de dinheiro móvel para fraude: referência para dataset sintético |
| `altman2023realistic`  | Dataset sintético de lavagem de dinheiro (AMLworld) com padrões em grafo (fan-in, fan-out, ciclos, cadeias) |
| `weber2019aml`         | Dataset Elliptic: grafo de transações Bitcoin rotulado, com comparação entre atributos tabulares e de grafo |
| `brandes2001faster`    | Algoritmo usado pelo NetworkX para calcular a intermediação (*betweenness*)            |

## Fichamentos

| Chave | Assunto em uma linha | Entra em |
|-------|----------------------|----------|
<!-- uma linha por leitura, com link para docs/leituras/<chave>.md -->
