---
tags: [mapa]
---

# Explorador interativo

App em [Streamlit](https://streamlit.io) para gerar redes Pix sintéticas, ver o que cada
modelo acha nelas e explorar contas, trilhas e resultados sem escrever código. Útil para
estudar e para mostrar a pesquisa em reuniões.

```powershell
pip install -e ".[app]"                                          # uma vez
streamlit run app/explorador.py --server.address localhost       # abre no navegador
```

O `--server.address localhost` deixa o app visível **só neste computador**. Sem ele, o
Streamlit também responde pelo IP da rede local e pelo endereço externo da máquina.

## Escolher a rede

Na barra lateral, em **Rede**:

- **Semente**: digite um número, sorteie com o 🎲 ou use um atalho (42 é a dos
  resultados do relatório, 1 a 10 são as sementes de teste dos estudos, 1001 e 1002 são
  as redes de validação da otimização). A mesma semente gera sempre a mesma rede.
- **Cenário**: do `base` (o gerador como está) aos realistas (`realista`,
  `negativos_dificeis`, `quadrilhas_realistas`, `calibrado`); a legenda mostra o que cada
  um muda (ver [`configs/cenarios.yaml`](../configs/cenarios.yaml)).
- **Hiperparâmetros**: `padrão` ou `otimizada`, esta quando existir
  `configs/experimento_otimizado.yaml` (gerado por `scripts/03_modelos/otimizar_hiperparametros.py`).
- **Gerar rede**: gera a rede e roda todos os modelos. A primeira vez de cada rede leva
  cerca de 1 minuto; depois fica guardada enquanto o app estiver aberto.

Em **Modelo**, escolha o modelo que pinta o risco (agrupados em não supervisionados e
supervisionados e ordenados pela AP nesta rede) e o **top-k**: quantas contas um
analista investigaria.

Para explorar um dataset salvo no mesmo formato (por exemplo, o AMLworld importado),
defina a pasta antes de abrir; o app oferece então "dataset salvo" ou "gerar uma rede":

```powershell
$env:PIXFRAUD_DADOS = "data/external/amlworld_pix"; streamlit run app/explorador.py --server.address localhost
```

## As abas

| Aba | O que mostra |
|-----|--------------|
| Resumo | contas, Pix, dias, dinheiro movimentado, quadrilhas, contas fraudulentas, golpes e o dinheiro deles, componente gigante fraca e forte; e o desempenho do modelo escolhido (AP, precisão no top-k, fraudes achadas, alarmes falsos), com o nível do acaso |
| Rede inteira | todas as contas, com busca, filtros, linha do tempo e quatro cores: papel, risco, grupo (Louvain) e **acertos** (fraude achada, alarme falso, fraude perdida); a caixa de desempenho e o seletor de modelo estão na própria página |
| Ranking | as contas mais suspeitas do modelo, com o papel verdadeiro e se é acerto ou alarme falso; selecionar uma linha abre a conta na aba Conta |
| Modelos | a AP de todos os modelos nesta rede, em barras coloridas pelo grupo, com a linha do acaso |
| Conta | ficha da conta escolhida: por que ela chamou atenção e a trilha do dinheiro, comum ou temporal |
| Padrões de fraude | desenha os padrões de `pixfraud.patterns` (fan-in, cadeia, ciclo...) no tamanho escolhido |
| Fluxo e bloqueio | fluxo máximo e corte mínimo até um destino: quanto dinheiro passou e que contas bloquear |
| Resultados | a AP média de todos os modelos nos estudos com 10 sementes por cenário (padrão e otimizada), a robustez dos conjuntos de atributos e os testes estatísticos por atributo |

A interface fica em [`explorador.py`](explorador.py); o que ela calcula (gerar a rede,
pontuar os modelos, o resumo e o top-k) fica em `pixfraud.exploration`, para poder ser
testado sem o Streamlit. Os testes estão em `tests/test_app.py` e
`tests/test_exploration.py`.
