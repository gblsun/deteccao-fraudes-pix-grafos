---
tags: [codigo]
---

# Diretórios

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Cada diretório do repositório e o que ele guarda. As pastas `results/` e `figures/` de cada etapa ficam dentro de `reports/<etapa>/`. Ver também o [mapa do código](mapa-do-codigo.md).

| Diretório | O que guarda | Guia |
|---|---|---|
| `.claude/` | configuração do Claude Code para este repositório (permissões, leituras bloqueadas) |  |
| `.github/` | configuração do GitHub |  |
| &nbsp;&nbsp;`workflows/` | integração contínua: roda o lint e os testes a cada push |  |
| `.obsidian/` | configuração do cofre do Obsidian (cores do grafo, plugins, espaço de trabalho) |  |
| `.vscode/` | configuração do VS Code para o projeto |  |
| `app/` | explorador interativo em Streamlit: gera redes, roda os modelos e mostra resultados | [README.md](../../app/README.md) |
| `configs/` | parâmetros dos experimentos (YAML): simulação, atributos, modelos, cenários e grades de busca | [README.md](../../configs/README.md) |
| `data/` | dados (não versionados, só a estrutura): sintéticos, externos, do BCB e processados | [README.md](../../data/README.md) |
| &nbsp;&nbsp;`bcb/` | estatísticas agregadas do Pix baixadas da API de dados abertos do Banco Central |  |
| &nbsp;&nbsp;`processed/` | tabelas intermediárias, como os atributos de cada conta |  |
| &nbsp;&nbsp;`raw/` | arquivos originais baixados (AMLworld, PaySim), antes da conversão |  |
| &nbsp;&nbsp;`synthetic/` | o dataset sintético da semente 42 (contas e transações) |  |
| `docs/` | documentação da pesquisa: proposta, cronograma, resultados, glossário, leituras, diário e atas | [mapa-da-pesquisa.md](../../docs/mapa-da-pesquisa.md) |
| &nbsp;&nbsp;`anexos/` | anexos da documentação (figuras e arquivos citados nas notas) |  |
| &nbsp;&nbsp;`codigo/` | esta documentação do código, gerada a partir das docstrings | [mapa-do-codigo.md](../../docs/codigo/mapa-do-codigo.md) |
| &nbsp;&nbsp;`diario/` | diário de pesquisa, uma nota por dia | [diario-de-pesquisa.md](../../docs/diario/diario-de-pesquisa.md) |
| &nbsp;&nbsp;`futuro/` | ideias de trabalhos futuros | [ideias-futuras.md](../../docs/futuro/ideias-futuras.md) |
| &nbsp;&nbsp;`glossario/` | termos técnicos, fórmulas e onde cada um aparece no projeto | [glossario.md](../../docs/glossario/glossario.md) |
| &nbsp;&nbsp;`leituras/` | fichamentos, um por leitura, com a chave do .bib como nome | [README.md](../../docs/leituras/README.md) |
| &nbsp;&nbsp;`modelos/` | modelos de nota do Obsidian (fichamento, diário, reunião) |  |
| &nbsp;&nbsp;`reunioes/` | atas das reuniões de orientação | [atas-de-reuniao.md](../../docs/reunioes/atas-de-reuniao.md) |
| `estudos/` | notebooks de estudo de teoria dos grafos e NetworkX, com gabarito | [trilha-de-estudos.md](../../estudos/trilha-de-estudos.md) |
| &nbsp;&nbsp;`dados/` | pequenos CSVs de exemplo usados nos estudos |  |
| `graphify-out/` | grafo do código gerado pelo Graphify (graph.json, relatório e página HTML) |  |
| `notebooks/` | análises exploratórias da pesquisa em Jupyter | [mapa-dos-notebooks.md](../../notebooks/mapa-dos-notebooks.md) |
| `relatorio/` | o relatório final em Markdown, convertido pelo Pandoc | [mapa-do-relatorio.md](../../relatorio/mapa-do-relatorio.md) |
| &nbsp;&nbsp;`capitulos/` | os capítulos do relatório |  |
| `reports/` | resultados gerados pelos scripts, uma pasta por etapa da pesquisa | [mapa-dos-resultados.md](../../reports/mapa-dos-resultados.md) |
| &nbsp;&nbsp;`01_dados/` | resultados da etapa 1: auditoria do gabarito e realismo do gerador | [README.md](../../reports/01_dados/README.md) |
| &nbsp;&nbsp;`02_exploracao/` | resultados da etapa 2: tipo de rede e inferência sobre os atributos | [README.md](../../reports/02_exploracao/README.md) |
| &nbsp;&nbsp;`03_modelos/` | resultados da etapa 3: rodada única, otimização e vitrine dos modelos | [README.md](../../reports/03_modelos/README.md) |
| &nbsp;&nbsp;`04_avaliacao/` | resultados da etapa 4: robustez, cenários, ablação, propagação, GNN e sementes | [README.md](../../reports/04_avaliacao/README.md) |
| &nbsp;&nbsp;`05_interpretacao/` | resultados da etapa 5: falsos positivos | [README.md](../../reports/05_interpretacao/README.md) |
| &nbsp;&nbsp;`amlworld/` | validação externa no dataset AMLworld |  |
| &nbsp;&nbsp;`coletor_ativo/` | rodada à parte do cenário com a coletora que esvazia o dinheiro |  |
| &nbsp;&nbsp;`estudos/` | grafos gerados nos estudos e a rede inteira em HTML |  |
| &nbsp;&nbsp;`ilustracoes/` | figuras explicativas do README (não são resultados) | [README.md](../../reports/ilustracoes/README.md) |
| &nbsp;&nbsp;`otimizado/` | a vitrine dos modelos com os hiperparâmetros otimizados |  |
| `scripts/` | pontos de entrada da pesquisa, uma pasta por etapa | [mapa-dos-scripts.md](../../scripts/mapa-dos-scripts.md) |
| &nbsp;&nbsp;`01_dados/` | etapa 1: gerar, importar e baixar dados, auditar o gabarito, validar o realismo | [README.md](../../scripts/01_dados/README.md) |
| &nbsp;&nbsp;`02_exploracao/` | etapa 2: forma da rede, inferência sobre os atributos e visualização | [README.md](../../scripts/02_exploracao/README.md) |
| &nbsp;&nbsp;`03_modelos/` | etapa 3: rodada única, otimização dos hiperparâmetros e vitrine dos modelos | [README.md](../../scripts/03_modelos/README.md) |
| &nbsp;&nbsp;`04_avaliacao/` | etapa 4: repetições com sementes e cenários e comparações com inferência | [README.md](../../scripts/04_avaliacao/README.md) |
| &nbsp;&nbsp;`05_interpretacao/` | etapa 5: os erros dos modelos | [README.md](../../scripts/05_interpretacao/README.md) |
| &nbsp;&nbsp;`ferramentas/` | busca, grafo de notas, ilustrações, documentação do código e relatório | [README.md](../../scripts/ferramentas/README.md) |
| `src/` | código-fonte instalável |  |
| &nbsp;&nbsp;`pixfraud/` | o pacote Python da pesquisa | [README.md](../../src/pixfraud/README.md) |
| &nbsp;&nbsp;&nbsp;&nbsp;`models/` | os modelos de detecção, organizados por família | [mapa-dos-modelos.md](../../src/pixfraud/models/mapa-dos-modelos.md) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`semi_supervised/` | modelos que partem de parte das fraudes já conhecida |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`supervised/` | tetos supervisionados, treinados com os rótulos |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`neural/` | redes neurais supervisionadas para grafos (GraphSAGE) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`trees/` | árvores supervisionadas (Random Forest, gradient boosting) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`unsupervised/` | detectores não supervisionados de anomalia |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`boundary/` | detectores de fronteira (One-Class SVM) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`graph/` | detectores que usam só a estrutura do grafo (FRAUDAR, node2vec) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`isolation/` | detectores por isolamento (Isolation Forest) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`neural/` | redes neurais não supervisionadas (autoencoder, DOMINANT) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`proximity/` | detectores por proximidade (DBSCAN, LOF, kNN, k-means) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`statistical/` | detectores estatísticos (ECOD, PCA) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`tuning/` | otimização de hiperparâmetros: espaço de busca e avaliação dos candidatos |  |
| `tests/` | testes automáticos (pytest) do pacote, dos scripts e da documentação | [mapa-dos-testes.md](../../tests/mapa-dos-testes.md) |
