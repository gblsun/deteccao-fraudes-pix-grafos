# 2. Exploração

Scripts desta etapa da pesquisa: a forma da rede e a inferência sobre os atributos, antes dos modelos.

- [`analisar_tipo_de_rede.py`](analisar_tipo_de_rede.py): tipo de rede: lei de potência, componente gigante, comparação com modelos clássicos
- [`inferencia_atributos.py`](inferencia_atributos.py): testes de hipótese sobre os atributos (Mann-Whitney, Kruskal-Wallis + Dunn, Fisher)
- [`visualizar_rede.py`](visualizar_rede.py): página HTML da rede inteira, com filtros, linha do tempo e um seletor do modelo que pinta o risco
- [`criar_grafo.py`](criar_grafo.py): grafos avulsos: padrões, CSVs quaisquer, trilha do dinheiro, fluxo

Os resultados vão para [`reports/02_exploracao/`](../../reports/02_exploracao/README.md). O que cada script lê e grava está no [mapa dos scripts](../mapa-dos-scripts.md#2-exploração); a ordem das etapas, no [fluxo da pesquisa](../../docs/fluxo-da-pesquisa.md).
