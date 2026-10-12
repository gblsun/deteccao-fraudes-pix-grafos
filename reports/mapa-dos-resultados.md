---
tags: [mapa]
---

# Resultados gerados

Tudo aqui sai dos scripts de [`scripts/`](../scripts/mapa-dos-scripts.md) e pode ser refeito a
partir da configuração e das sementes. Os arquivos são pequenos e ficam versionados,
para os resultados aparecerem no GitHub e poderem ser citados por commit. A interpretação
está em [`docs/resultados.md`](../docs/resultados.md).

## Por etapa

Cada etapa da pesquisa (ver [fluxo da pesquisa](../docs/fluxo-da-pesquisa.md)) tem a sua pasta, com
`results/` (tabelas) e `figures/` (figuras), gravadas pelos scripts da pasta de mesmo nome em
[`scripts/`](../scripts/mapa-dos-scripts.md). Todo script de avaliação grava também um `*_meta.json`
(commit, configuração, sementes, duração e versões).

### 1. Dados: [`01_dados/`](01_dados/)

| Tabela (`results/`) | Script | Uma linha por... |
|---------|--------|------------------|
| `auditoria_papeis.csv` | `auditar_papeis.py` | conta cujo comportamento não bate com o papel (regra violada) |
| `auditoria_resumo.csv`, `auditoria_perfis.csv` | `auditar_papeis.py` | (cenário, semente): contas por papel e violações; mediana do que cada papel faz |
| `realismo_execucoes.csv` | `validar_realismo.py` | (cenário, semente): fração P2B, tickets médios, golpes a cada 100 mil Pix e valor médio do golpe no gerador |
| `realismo_comparacao.csv` | `validar_realismo.py` | (cenário, estatística): valor do BCB, média do gerador com IC 95%, erro relativo, se o BCB cai no IC e se o erro fica na tolerância |
| `realismo_estrutura.csv` | `validar_realismo.py` | (cenário, estatística): reciprocidade e transitividade observadas × modelo nulo de graus preservados (z e p empírico) |

| Figura (`figures/`) | Script | Mostra |
|---------|--------|--------|
| `testes_01_dados.png` | `ilustrar_testes.py` | o z do modelo nulo da reciprocidade sob H₀, com a zona crítica, e o grau de entrada contra a normal |

### 2. Exploração: [`02_exploracao/`](02_exploracao/)

| Tabela (`results/`) | Script | Uma linha por... |
|---------|--------|------------------|
| `tipo_de_rede_execucoes.csv`, `tipo_de_rede_resumo.csv` | `analisar_tipo_de_rede.py` | (cenário, semente): componentes, lei de potência, passeios e cosseno × Jaccard |
| `tipo_de_rede_modelos.csv` | `analisar_tipo_de_rede.py` | rede × Erdős–Rényi × Barabási–Albert |
| `tipo_de_rede_passeios.csv` | `analisar_tipo_de_rede.py` | (cenário, papel): onde terminam os passeios que saem das vítimas |
| `inferencia_fraude.csv` | `inferencia_atributos.py` | (cenário, atributo): delta de Cliff médio (fraude × legítima), IC 95% e em quantas sementes de validação o p de Holm < 0,05 |
| `inferencia_papeis.csv` | `inferencia_atributos.py` | (cenário, atributo): ε² médio do Kruskal-Wallis entre os 6 papéis, IC 95%, sementes significativas e o papel de maior mediana |
| `inferencia_dunn.csv` | `inferencia_atributos.py` | (cenário, atributo, par de papéis): teste de Dunn com p de Holm, na primeira semente de validação |
| `inferencia_categoricas.csv` | `inferencia_atributos.py` | (cenário, variável): V de Cramér e razão de chances de conta de empresa, conta nova e Pix de madrugada × fraude |
| `inferencia_execucoes.csv` | `inferencia_atributos.py` | (cenário, semente, teste, atributo): tudo o que foi calculado |

| Figura (`figures/`) | Script | Mostra |
|---------|--------|--------|
| `tipo_de_rede_graus.png` | `analisar_tipo_de_rede.py` | distribuição de graus: rede × modelos clássicos; entrada × saída |
| `inferencia_papeis.png` | `inferencia_atributos.py` | ε² médio de cada atributo × cenário: quanto ele separa os 6 papéis |
| `testes_02_exploracao.png` | `ilustrar_testes.py` | o z do Mann-Whitney e o H do Kruskal-Wallis sob H₀, com a zona crítica, e o atributo de maior efeito contra a normal |

### 3. Modelos: [`03_modelos/`](03_modelos/)

| Tabela (`results/`) | Script | Uma linha por... |
|---------|--------|------------------|
| `metricas.csv` | `rodar_experimento.py` | (conjunto de atributos, modelo), numa semente |
| `modelos_execucoes.csv`, `modelos_resumo.csv`, `modelos_comparacoes.csv` | `avaliar_modelos.py` | (cenário, semente, modelo): AP, precision@k e ROC-AUC de todos os modelos, nas mesmas contas |
| `modelos_friedman.csv`, `modelos_postos.csv` | `avaliar_modelos.py` | (cenário): teste de Friedman, W de Kendall e diferença crítica de Nemenyi; (cenário, modelo): posto médio |
| `modelos_acaso.csv` | `avaliar_modelos.py` | (cenário, modelo): em quantas sementes o modelo foi melhor que o acaso (permutação da AP e hipergeométrico no top-k) |
| `modelos_cenarios_kw.csv` | `avaliar_modelos.py` | modelo: Kruskal-Wallis da AP entre os cenários (a dificuldade muda o resultado?) |

| Figura (`figures/`) | Script | Mostra |
|---------|--------|--------|
| `grafo_de_calor_<modelo>_<atributos>.png` | `rodar_experimento.py` | as contas mais suspeitas e sua vizinhança, coloridas pelo risco |
| `heatmap_risco_<modelo>_<atributos>.png` | `rodar_experimento.py` | os atributos que explicam o risco de cada conta suspeita |
| `modelos_average_precision.png`, `modelos_comparacoes.png` | `avaliar_modelos.py` | AP média e IC 95% de todos os modelos por cenário; diferenças pareadas |
| `modelos_diferenca_critica.png` | `avaliar_modelos.py` | postos médios do Friedman com a diferença crítica: barras que não se tocam = modelos que diferem |
| `testes_03_modelos.png` | `ilustrar_testes.py` | a AP do DBSCAN contra o nulo da permutação do gabarito, e o escore contra a normal |

### 4. Avaliação: [`04_avaliacao/`](04_avaliacao/)

| Tabela (`results/`) | Script | Uma linha por... |
|---------|--------|------------------|
| `robustez_execucoes.csv` | `avaliar_robustez.py` | (semente, atributos, modelo) |
| `robustez_resumo.csv` | `avaliar_robustez.py` | (métrica, atributos, modelo): média e IC 95% |
| `robustez_comparacoes.csv` | `avaliar_robustez.py` | (métrica, modelo, par de conjuntos): teste pareado |
| `cenarios_execucoes.csv` | `avaliar_cenarios.py` | (cenário, semente, atributos, modelo) |
| `cenarios_resumo.csv` | `avaliar_cenarios.py` | (métrica, cenário, atributos, modelo) |
| `cenarios_comparacoes.csv` | `avaliar_cenarios.py` | (cenário, métrica, modelo, par de conjuntos) |
| `cenarios_efeitos.csv` | `avaliar_cenarios.py` | (cenário, atributo): delta de Cliff médio |
| `online_execucoes.csv`, `online_resumo.csv`, `online_comparacoes.csv` | `avaliar_deteccao_online.py` | (cenário, semente, atributos, modelo) e resumos |
| `online_cortes/` | `avaliar_deteccao_online.py` | contas sinalizadas em cada ponto de corte; **não versionado**, serve para retomar a execução |
| `atributos_ablacao.csv`, `atributos_ablacao_resumo.csv` | `avaliar_atributos.py` | (cenário, semente, modelo, atributo removido) e a queda média de AP |
| `atributos_teto.csv`, `atributos_teto_resumo.csv` | `avaliar_atributos.py` | AP dos detectores e do Random Forest supervisionado, por conjunto |
| `propagacao_execucoes.csv`, `propagacao_resumo.csv`, `propagacao_comparacoes.csv` | `avaliar_propagacao.py` | (cenário, semente, fração conhecida, método): AP nas contas ainda desconhecidas |
| `fraudar_execucoes.csv`, `fraudar_resumo.csv`, `fraudar_comparacoes.csv` | `avaliar_fraudar.py` | (cenário, semente, método): AP, precision@k, contas marcadas e cobertura das fraudes pelos blocos |
| `gnn_execucoes.csv`, `gnn_resumo.csv`, `gnn_comparacoes.csv` | `avaliar_gnn.py` | (cenário, semente, método): AP e precision@k das GNN, do DBSCAN e do Random Forest |
| `sementes_execucoes.csv` | `avaliar_sementes.py` | (semente, atributos, modelo), até 1000 sementes; também é o progresso salvo |
| `sementes_convergencia.csv` | `avaliar_sementes.py` | (nº de sementes, atributos, modelo): AP média, desvio e IC 95% usando as sementes 1..n |
| `sementes_sorteios.csv` | `avaliar_sementes.py` | (atributos, modelo): faixa de 95% da média de 10 sementes sorteadas |

| Figura (`figures/`) | Script | Mostra |
|---------|--------|--------|
| `robustez_average_precision.png` | `avaliar_robustez.py` | AP média e IC 95% por conjunto e modelo |
| `cenarios_average_precision.png` | `avaliar_cenarios.py` | AP média por conjunto × cenário |
| `cenarios_efeitos.png` | `avaliar_cenarios.py` | delta de Cliff de cada atributo × cenário |
| `online_deteccao.png` | `avaliar_deteccao_online.py` | detectadas em 72 h e dinheiro recuperado |
| `atributos_ablacao.png` | `avaliar_atributos.py` | queda de AP ao tirar cada atributo |
| `atributos_teto.png` | `avaliar_atributos.py` | detectores não supervisionados × Random Forest com os rótulos |
| `propagacao_average_precision.png` | `avaliar_propagacao.py` | AP da propagação de risco, dos detectores e da combinação |
| `fraudar_average_precision.png` | `avaliar_fraudar.py` | AP do FRAUDAR, do DBSCAN e da combinação por cenário |
| `gnn_average_precision.png` | `avaliar_gnn.py` | AP das GNN e das referências por cenário |
| `sementes_convergencia.png` | `avaliar_sementes.py` | AP média e meia-largura do IC 95% contra o nº de sementes |
| `testes_04_avaliacao.png` | `ilustrar_testes.py` | t pareado, z do Wilcoxon e χ² do Friedman sob H₀, com a zona crítica, e a diferença de AP por semente contra a normal |

### 5. Interpretação: [`05_interpretacao/`](05_interpretacao/)

| Tabela (`results/`) | Script | Uma linha por... |
|---------|--------|------------------|
| `falsos_positivos_papeis.csv` | `investigar_falsos_positivos.py` | (cenário, semente, modelo): papel real das k contas de maior risco (k = nº de fraudes) |
| `falsos_positivos_top.csv`, `falsos_positivos_atributos.csv` | `investigar_falsos_positivos.py` | (cenário, modelo, posição): as contas de maior risco na semente 42, o papel real e o percentil de cada atributo |
| `falsos_positivos_testes.csv` | `investigar_falsos_positivos.py` | (cenário, modelo): razão de chances do comércio no top-k (Fisher, só legítimas) e ε² do escore entre os papéis |
| `falsos_positivos_dunn.csv` | `investigar_falsos_positivos.py` | (cenário, modelo, par de papéis): teste de Dunn do escore de risco |

| Figura (`figures/`) | Script | Mostra |
|---------|--------|--------|
| `falsos_positivos_comercio.png` | `investigar_falsos_positivos.py` | fração das k contas de maior risco que são comércios, por modelo e cenário |

### Ilustrações do README: [`ilustracoes/`](ilustracoes/)

| Figura | Script | Mostra |
|---------|--------|--------|
| `padroes_de_fraude.png`, `quadrilha.gif`, `rede_exemplo.png` | `gerar_ilustracoes.py` | ilustrações do README: os padrões injetados, o dinheiro percorrendo a quadrilha e a fraude dentro do movimento normal |
| `grafo_de_notas.png`, `grafo_do_codigo.png` | `ilustrar_grafos_de_conhecimento.py` | ilustrações do README: o grafo de notas do Obsidian e o mapa do código pelo Graphify (não são resultados da pesquisa) |

## Colunas das tabelas

| Coluna | Significado |
|--------|-------------|
| `atributos` | conjunto de atributos (`FEATURE_SETS` em `src/pixfraud/features.py`) |
| `modelo` | `isolation_forest` ou `dbscan` |
| `precision`, `recall`, `f1` | do rótulo binário do modelo (anomalia ou não) |
| `roc_auc`, `average_precision` | da ordenação pelo escore; a AP é a métrica principal (ao acaso, vale a taxa de fraude) |
| `precision_at_k` | fração de fraudes entre as *k* contas mais suspeitas (*k* = nº de fraudes) |
| `n_flagged` | quantas contas o modelo marcou como anômalas |
| `semente`, `cenario`, `fraudes`, `contas` | repetição, cenário de `configs/cenarios.yaml`, nº de contas fraudulentas e total |
| `mean`, `std`, `count`, `ic_inferior`, `ic_superior` | média, desvio, nº de repetições e IC t de 95% |
| `comparação` | `a - b`: diferença positiva quer dizer que `a` foi melhor |
| `diferença média`, `a vence em` | média de `a - b` nas repetições e em quantas `a` foi melhor |
| `p Wilcoxon`, `p t pareado`, `p Wilcoxon (Holm)` | p-valores; o último já corrigido para as várias comparações de cada métrica |
| `delta_medio`, `efeito` | delta de Cliff (fraude × normal; > 0 = maior nas fraudes) e rótulo do tamanho do efeito |
| `detectadas_72h`, `atraso_mediano_h` | fração das contas fraudulentas sinalizadas até 72 h após o 1º golpe e o atraso mediano |
| `recuperado_<prazo>` | fração do dinheiro roubado retida em contas bloqueadas, se o saque acontece após `<prazo>` |
| `atributo`, `ap_sem`, `ap_com_todos`, `queda` | atributo removido, AP sem ele, AP com todos e a diferença (> 0: o atributo ajudava) |
| `metodo`, `conhecidas` | método de pontuação (propagação, detector ou combinação) e fração das fraudes tratadas como já conhecidas |
| `fraudes_conhecidas`, `fraudes_restantes` | contas fraudulentas usadas como ponto de partida e as que ficaram para ser encontradas |

## `amlworld/`: validação externa

Saída de `avaliar_externo.py` sobre o AMLworld (ver [`data/README.md`](../data/README.md)):
`results/<dataset>_execucoes.csv`, `_resumo.csv`, `_comparacoes.csv` e `_tipologias.csv`
(recall@k por tipologia de lavagem), além de `<dataset>_janelas/` (cada janela salva, **não versionada**) e
`figures/<dataset>_tipologias.png`. O `<dataset>` é `amlworld_pix` (só ACH e Wire) ou
`amlworld` (todas as formas de pagamento).

## `coletor_ativo/`: coletora que esvazia o dinheiro

Saída de `avaliar_cenarios.py --cenarios realista coletor_ativo --sementes 10 --saida reports/coletor_ativo`
(pedido da reunião de 24/09): as mesmas tabelas e figuras de `cenarios_*`, só com esses dois
cenários, para não misturar com a rodada completa dos cenários em `04_avaliacao/results/`.

## `estudos/`: grafos dos estudos

Saídas de `criar_grafo.py` e de `visualizar_rede.py` (`rede_completa.html`: a rede
inteira; abra no navegador). São material de estudo, não resultados da pesquisa.

## Lista de figuras

Galeria na ordem em que a pesquisa é contada, no estilo de uma lista de figuras de TCC.
Os arquivos ficam versionados nas pastas `figures/` de cada etapa e em `amlworld/figures/`, e podem ser refeitos a
partir da configuração e das sementes (ver o `*_meta.json` de cada script, na tabela
acima). A interpretação de cada uma está em [`docs/resultados.md`](../docs/resultados.md).

**Figura 1** — Os padrões de fraude injetados pelo simulador (conta laranja,
intermediário, coletora), separados por papel.
*Fonte: `gerar_ilustracoes.py`.*
![Padrões de fraude](ilustracoes/padroes_de_fraude.png)

**Figura 2** — Uma quadrilha dentro do movimento normal: o que a denuncia não é o que
cada conta faz sozinha, e sim o formato que desenha na rede.
*Fonte: `gerar_ilustracoes.py`.*
![Quadrilha dentro do movimento normal](ilustracoes/rede_exemplo.png)

**Figura 3** — Average precision média e intervalo de confiança de 95%, por conjunto de
atributos e modelo, em 10 sementes.
*Fonte: `avaliar_robustez.py`.*
![Robustez: average precision](04_avaliacao/figures/robustez_average_precision.png)

**Figura 4** — Average precision média por conjunto de atributos × cenário (fácil, base,
difícil, realista).
*Fonte: `avaliar_cenarios.py`.*
![Cenários: average precision](04_avaliacao/figures/cenarios_average_precision.png)

**Figura 5** — Delta de Cliff de cada atributo, fraude × normal, em cada cenário: o
tamanho do efeito que separa as duas classes.
*Fonte: `avaliar_cenarios.py`.*
![Cenários: efeitos](04_avaliacao/figures/cenarios_efeitos.png)

**Figura 6** — Queda de average precision ao remover cada atributo, um de cada vez
(ablação).
*Fonte: `avaliar_atributos.py`.*
![Ablação de atributos](04_avaliacao/figures/atributos_ablacao.png)

**Figura 7** — Os detectores não supervisionados contra o teto do Random Forest treinado
com os rótulos: a distância entre os dois é o custo de não ter rótulos.
*Fonte: `avaliar_atributos.py`.*
![Teto supervisionado](04_avaliacao/figures/atributos_teto.png)

**Figura 8** — Average precision da propagação de risco (PageRank personalizado a partir
de fraudes já conhecidas), dos detectores sozinhos e da combinação dos dois.
*Fonte: `avaliar_propagacao.py`.*
![Propagação de risco](04_avaliacao/figures/propagacao_average_precision.png)

**Figura 9** — Fração das contas fraudulentas detectadas até 72 h após o primeiro golpe e
fração do dinheiro roubado retida, simulando o bloqueio cautelar (MED).
*Fonte: `avaliar_deteccao_online.py`.*
![Detecção em tempo](04_avaliacao/figures/online_deteccao.png)

**Figura 10** — Grafo de calor: as contas mais suspeitas e sua vizinhança, coloridas pelo
risco (DBSCAN, conjunto de atributos completo). As demais combinações de modelo ×
conjunto de atributos seguem o mesmo padrão e ficam em `grafo_de_calor_<modelo>_<atributos>.png`.
*Fonte: `rodar_experimento.py`.*
![Grafo de calor](03_modelos/figures/grafo_de_calor_dbscan_completo.png)

**Figura 11** — Heatmap de risco: os atributos que explicam o risco de cada conta
suspeita (DBSCAN, conjunto completo). As demais combinações ficam em
`heatmap_risco_<modelo>_<atributos>.png`.
*Fonte: `rodar_experimento.py`.*
![Heatmap de risco](03_modelos/figures/heatmap_risco_dbscan_completo.png)

**Figura 12** — Recall@k por tipologia de lavagem de dinheiro, na validação externa com o
AMLworld (versão só com ACH e Wire, mais próxima do Pix).
*Fonte: `avaliar_externo.py`.*
![Validação externa: tipologias do AMLworld](amlworld/figures/amlworld_pix_tipologias.png)

**Figura 13** — Average precision do FRAUDAR (blocos densos, só estrutura), do melhor
detector de atributos e da combinação dos dois, do cenário mais fácil ao mais realista.
*Fonte: `avaliar_fraudar.py`.*
![FRAUDAR](04_avaliacao/figures/fraudar_average_precision.png)

**Figura 14** — Average precision das redes neurais para grafos (DOMINANT, sem rótulos;
GraphSAGE, com rótulos) ao lado do DBSCAN e do Random Forest.
*Fonte: `avaliar_gnn.py`.*
![Redes neurais para grafos](04_avaliacao/figures/gnn_average_precision.png)

**Figura 15** — Quantas sementes bastam: average precision média (com IC 95%) e
meia-largura do IC com 10, 100, 500 e 1000 sementes (conjunto completo).
*Fonte: `avaliar_sementes.py`.*
![Convergência da AP média](04_avaliacao/figures/sementes_convergencia.png)

**Figura 16** — Distribuição de graus da rede Pix sintética: (a) ao lado de um
Erdős–Rényi e de um Barabási–Albert do mesmo tamanho; (b) grau de entrada, com cauda
de lei de potência, e grau de saída, sem ela.
*Fonte: `analisar_tipo_de_rede.py`.*
![Tipo de rede](02_exploracao/figures/tipo_de_rede_graus.png)

**Figura 17** — Todos os modelos nas mesmas contas (não supervisionados, incluindo KNN,
K-Means e PCA; estrutura do grafo; semi-supervisionados; tetos supervisionados): average
precision média e IC 95% por cenário.
*Fonte: `avaliar_modelos.py`.*
![Todos os modelos](03_modelos/figures/modelos_average_precision.png)

**Figura 18** — Fração das k contas de maior risco (k = nº de fraudes) que são comércios,
por modelo e cenário: os falsos positivos da reunião de 01/10.
*Fonte: `investigar_falsos_positivos.py`.*
![Comércios no topo do risco](05_interpretacao/figures/falsos_positivos_comercio.png)

## Material interativo

Não são figuras estáticas, então ficam fora da lista numerada acima:

- [`quadrilha.gif`](ilustracoes/quadrilha.gif): o dinheiro percorrendo a quadrilha, do golpe
  ao saque.
- [`estudos/rede_completa.html`](estudos/rede_completa.html): toda a rede sintética, com
  busca, filtro por papel, cor por papel/risco/comunidade, setas no sentido do dinheiro
  (entradas e saídas destacadas ao clicar numa conta) e linha do tempo dia a dia
  (embutida em [`docs/rede-pix.md`](../docs/rede-pix.md)).
- [`estudos/trilha_coletor.png`](estudos/trilha_coletor.png): a trilha do dinheiro em
  volta de uma conta coletora (`criar_grafo.py`), usada também em `docs/rede-pix.md`.
