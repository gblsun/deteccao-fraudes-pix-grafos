# 4. Avaliação

Scripts desta etapa da pesquisa: repetir com várias sementes e cenários e comparar os modelos com inferência (IC 95%, Wilcoxon pareado, Holm).

- [`avaliar_robustez.py`](avaliar_robustez.py): repete com várias sementes; IC e testes pareados
- [`avaliar_sementes.py`](avaliar_sementes.py): quantas sementes bastam? AP média e IC 95% com 10, 100, 500 e 1000 sementes
- [`avaliar_cenarios.py`](avaliar_cenarios.py): repete em cada cenário de dificuldade
- [`avaliar_deteccao_online.py`](avaliar_deteccao_online.py): detecção ao longo do tempo: bloqueou a tempo?
- [`avaliar_atributos.py`](avaliar_atributos.py): ablação por atributo e teto supervisionado (Random Forest com os rótulos)
- [`avaliar_propagacao.py`](avaliar_propagacao.py): culpa por associação: com parte das fraudes conhecidas, quanto se acha do resto?
- [`avaliar_fraudar.py`](avaliar_fraudar.py): FRAUDAR: blocos densos (só estrutura) contra o melhor detector e combinados
- [`avaliar_gnn.py`](avaliar_gnn.py): redes neurais para grafos (DOMINANT e GraphSAGE) contra DBSCAN e Random Forest
- [`avaliar_gnn_rotulos.py`](avaliar_gnn_rotulos.py): GraphSAGE e Random Forest treinados com poucas fraudes conhecidas
- [`avaliar_externo.py`](avaliar_externo.py): mesma configuração num dataset externo, por janelas; recall por tipologia

Os resultados vão para [`reports/04_avaliacao/`](../../reports/04_avaliacao/README.md). O que cada script lê e grava está no [mapa dos scripts](../mapa-dos-scripts.md#4-avaliação); a ordem das etapas, no [fluxo da pesquisa](../../docs/fluxo-da-pesquisa.md).
