# 1. Dados

Scripts desta etapa da pesquisa: gerar a rede sintética, importar dados externos, conferir o gabarito e comparar o gerador com o Pix real (BCB).

- [`gerar_dataset.py`](gerar_dataset.py): gera um dataset sintético (semente sorteada ou fixa com --seed)
- [`auditar_papeis.py`](auditar_papeis.py): confere se o papel de cada conta bate com as transações dela (`simulation.audit_roles`), em todos os cenários
- [`validar_realismo.py`](validar_realismo.py): o gerador parece o Pix real? médias do gerador × agregados do BCB e a estrutura contra o acaso
- [`importar_dataset.py`](importar_dataset.py): converte AMLworld ou PaySim para o formato do projeto
- [`baixar_dados_bcb.py`](baixar_dados_bcb.py): baixa estatísticas do Pix do Banco Central

Os resultados vão para [`reports/01_dados/`](../../reports/01_dados/README.md). O que cada script lê e grava está no [mapa dos scripts](../mapa-dos-scripts.md#1-dados); a ordem das etapas, no [fluxo da pesquisa](../../docs/fluxo-da-pesquisa.md).
