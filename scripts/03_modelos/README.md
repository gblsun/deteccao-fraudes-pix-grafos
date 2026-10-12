# 3. Modelos

Scripts desta etapa da pesquisa: ajuste, otimização dos hiperparâmetros e a vitrine de todos os modelos, com o teste de Friedman e os testes contra o acaso.

- [`rodar_experimento.py`](rodar_experimento.py): uma rodada: grafo, atributos, 2 detectores × 6 conjuntos, figuras
- [`avaliar_modelos.py`](avaliar_modelos.py): vitrine de todos os modelos nas mesmas contas, com Friedman e testes contra o acaso
- [`otimizar_hiperparametros.py`](otimizar_hiperparametros.py): busca em grade dos hiperparâmetros de cada modelo, em rodadas

Os resultados vão para [`reports/03_modelos/`](../../reports/03_modelos/README.md). O que cada script lê e grava está no [mapa dos scripts](../mapa-dos-scripts.md#3-modelos); a ordem das etapas, no [fluxo da pesquisa](../../docs/fluxo-da-pesquisa.md).
