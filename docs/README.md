# Documentação da pesquisa

Ponto de partida para navegar pela documentação (no GitHub ou no Obsidian). A visão geral
do projeto e o passo a passo para rodar estão no [README principal](../README.md).

## A pesquisa

| Documento | Para que serve |
|-----------|----------------|
| [Proposta](proposta.md) ([PDF original](proposta-original.pdf)) | objetivos, justificativa e metodologia planejada |
| [Cronograma](cronograma.md) | etapas de 12 meses e o que cada uma entrega no repositório |
| [Resultados](resultados.md) | o que os experimentos mostraram, com números, figuras e ressalvas |
| [Revisão bibliográfica](revisao-bibliografica.md) | índice das leituras e sugestões; referências em [`referencias.bib`](referencias.bib) |

## Anotações

| Pasta | Conteúdo | Modelo |
|-------|----------|--------|
| [`leituras/`](leituras/) | um fichamento por leitura, com a chave do `.bib` como nome | [fichamento](modelos/fichamento.md) |
| [`diario/`](diario/) | diário de pesquisa, uma nota por dia: o que rodou, o que foi decidido e por quê | [diário](modelos/diario.md) |
| [`reunioes/`](reunioes/) | atas das reuniões de orientação | [reunião](modelos/reuniao.md) |

Como usar tudo isso no Obsidian: [obsidian.md](obsidian.md).

## Documentação do código e dos dados

| Onde | O que explica |
|------|---------------|
| [`src/pixfraud/`](../src/pixfraud/README.md) | os módulos do pacote e como eles se encaixam |
| [`scripts/`](../scripts/README.md) | cada script, o que lê e grava, e a ordem para reproduzir tudo |
| [`configs/`](../configs/README.md) | parâmetros dos experimentos e cenários |
| [`data/`](../data/README.md) | esquema dos dados, limitações do gerador, BCB e datasets externos |
| [`reports/`](../reports/README.md) | cada tabela e figura gerada, com o dicionário das colunas |
| [`notebooks/`](../notebooks/README.md) | análises da pesquisa |
| [`estudos/`](../estudos/README.md) | material de estudo de teoria dos grafos |
| [`app/`](../app/README.md) | o explorador interativo |
| [`relatorio/`](../relatorio/README.md) | esqueleto do relatório final em Markdown, gerado em DOCX/PDF pelo Pandoc |
| [`tests/`](../tests/README.md) | o que cada teste verifica |

Regra para tudo o que fica no repositório: **nenhum nome de pessoa, orientador ou
curso** (a proposta é submetida de forma anônima).
