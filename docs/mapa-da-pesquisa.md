---
tags: [mapa]
---

# Documentação da pesquisa

Ponto de partida para navegar pela documentação (no GitHub ou no Obsidian). A visão geral
do projeto e o passo a passo para rodar estão no [README principal](../README.md).

## A pesquisa

| Documento | Para que serve |
|-----------|----------------|
| [Proposta](proposta.md) ([PDF original](proposta-original.pdf)) | objetivos, justificativa e metodologia planejada |
| [Cronograma](cronograma.md) | etapas de 12 meses e o que cada uma entrega no repositório |
| [Próximos passos](proximos-passos.md) | o que ficou em aberto, para retomar na próxima sessão |
| [Resultados](resultados.md) | o que os experimentos mostraram, com números, figuras e ressalvas |
| [Modelos](modelos.md) | o que cada modelo faz, como está configurado e que outros caberiam |
| [Revisão bibliográfica](revisao-bibliografica.md) | índice das leituras e sugestões; referências em [`referencias.bib`](referencias.bib) |
| [Glossário](glossario/glossario.md) | termos técnicos, fórmulas e onde cada um aparece no projeto |
| [Ideias futuras](futuro/ideias-futuras.md) | direções de pesquisa ainda não exploradas, para a seção de trabalhos futuros |

## Anotações

| Pasta                                        | Conteúdo                                                                                                                         | Modelo                              |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| [`leituras/`](leituras/mapa-das-leituras.md) | um fichamento por leitura, com a chave do `.bib` como nome; o [mapa das leituras](leituras/mapa-das-leituras.md) agrupa por tema | [fichamento](modelos/fichamento.md) |
| [`diario/`](diario/diario-de-pesquisa.md)    | diário de pesquisa, uma nota por dia: o que rodou, o que foi decidido e por quê                                                  | [diário](modelos/diario.md)         |
| [`reunioes/`](reunioes/atas-de-reuniao.md)   | atas das reuniões de orientação                                                                                                  | [reunião](modelos/reuniao.md)       |

Como usar tudo isso no Obsidian: [obsidian.md](obsidian.md). Para ver a **rede Pix** (e
não o grafo das notas) sem sair do cofre: [rede-pix.md](rede-pix.md).

## Documentação do código e dos dados

| Onde | O que explica |
|------|---------------|
| [`src/pixfraud/`](../src/pixfraud/README.md) | os módulos do pacote e como eles se encaixam |
| [`scripts/`](../scripts/mapa-dos-scripts.md) | cada script, o que lê e grava, e a ordem para reproduzir tudo |
| [`configs/`](../configs/parametros-dos-experimentos.md) | parâmetros dos experimentos e cenários |
| [`data/`](../data/README.md) | esquema dos dados, limitações do gerador, BCB e datasets externos |
| [`reports/`](../reports/mapa-dos-resultados.md) | cada tabela e figura gerada, com o dicionário das colunas |
| [`notebooks/`](../notebooks/mapa-dos-notebooks.md) | análises da pesquisa |
| [`estudos/`](../estudos/trilha-de-estudos.md) | material de estudo de teoria dos grafos |
| [`app/`](../app/guia-do-explorador.md) | o explorador interativo |
| [`relatorio/`](../relatorio/mapa-do-relatorio.md) | esqueleto do relatório final em Markdown, gerado em DOCX/PDF pelo Pandoc |
| [`tests/`](../tests/mapa-dos-testes.md) | o que cada teste verifica |

Regra para tudo o que fica no repositório: seguir a **LGPD** no contexto do Pix, sem
nenhum dado pessoal real de usuário do Pix (ver [CLAUDE.md](../CLAUDE.md)).
