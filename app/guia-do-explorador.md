---
tags: [mapa]
---

# Explorador interativo

App em [Streamlit](https://streamlit.io) para explorar a rede, as contas suspeitas e os
resultados sem escrever código. Útil para estudar e para mostrar a pesquisa em reuniões.

```powershell
pip install -e ".[app]"          # uma vez
streamlit run app/explorador.py  # abre no navegador
```

Na primeira execução, se `data/synthetic/` não existir, o dataset sintético é gerado
automaticamente. Para explorar outro dataset no mesmo formato (por exemplo, o AMLworld
importado), defina a pasta antes de abrir:

```powershell
$env:PIXFRAUD_DADOS = "data/external/amlworld_pix"; streamlit run app/explorador.py
```

## O que tem

Na barra lateral, escolha o **detector** e o **conjunto de atributos** que definem o
risco de cada conta. As abas:

| Aba | O que mostra |
|-----|--------------|
| Rede inteira | todas as contas, com busca, filtros por papel, cor por papel, risco ou comunidade, e linha do tempo |
| Conta | ficha de uma das 50 contas mais suspeitas (ou de qualquer conta digitada): por que ela chamou atenção e a trilha do dinheiro, comum ou temporal |
| Padrões de fraude | desenha os padrões de `pixfraud.patterns` (fan-in, cadeia, ciclo...) no tamanho escolhido |
| Fluxo e bloqueio | fluxo máximo e corte mínimo até um destino: quanto dinheiro passou e que contas bloquear |
| Resultados | métricas dos detectores e testes estatísticos por atributo |

O código fica todo em [`explorador.py`](explorador.py) e reaproveita o pacote
[`pixfraud`](../src/pixfraud/README.md). O teste de fumaça está em
`tests/test_app.py`.
