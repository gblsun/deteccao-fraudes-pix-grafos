---
tags: [mapa]
---

# Scripts

Pontos de entrada da pesquisa. Rode sempre da **raiz do repositório**, com o ambiente
ativado (`.venv\Scripts\Activate.ps1`). Cada script tem `--help` e uma docstring no topo
com exemplos de uso.

## Mapa

As pastas seguem as etapas da pesquisa (ver [fluxo da pesquisa](../docs/fluxo-da-pesquisa.md));
os resultados de cada etapa vão para a pasta de mesmo nome em `reports/`.

### 1. Dados

[`01_dados/`](01_dados/): gerar a rede sintética, importar dados externos e conferir o gabarito.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`gerar_dataset.py`](01_dados/gerar_dataset.py) | gera um dataset sintético novo a cada execução (semente sorteada, gravada em `dataset_meta.json`; `--seed N` reproduz; `--aleatorio` sorteia também o nº de quadrilhas, laranjas, vítimas e comércios) | `configs/experimento.yaml` | `data/synthetic/` + `dataset_meta.json` | segundos |
| [`auditar_papeis.py`](01_dados/auditar_papeis.py) | confere se o papel de cada conta bate com as transações dela (`simulation.audit_roles`), em todos os cenários | `configs/cenarios.yaml`, `data/synthetic/` | `reports/01_dados/results/auditoria_*` | ~1 min (14 cenários × 20 sementes) |
| [`importar_dataset.py`](01_dados/importar_dataset.py) | converte AMLworld ou PaySim para o formato do projeto | `data/raw/` | `data/external/<nome>/` | ~1 min |
| [`baixar_dados_bcb.py`](01_dados/baixar_dados_bcb.py) | baixa estatísticas do Pix do Banco Central | API do BCB | `data/bcb/` | segundos |

### 2. Exploração

[`02_exploracao/`](02_exploracao/): a forma da rede e os atributos, antes dos modelos.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`analisar_tipo_de_rede.py`](02_exploracao/analisar_tipo_de_rede.py) | tipo de rede: lei de potência, componente gigante, comparação com Erdős–Rényi e Barabási–Albert, passeios aleatórios a partir das vítimas, cosseno × Jaccard | `configs/cenarios.yaml` | `reports/02_exploracao/results/tipo_de_rede_*.csv`, `tipo_de_rede_graus.png` | ~2 min (3 cenários × 5 sementes) |
| [`visualizar_rede.py`](02_exploracao/visualizar_rede.py) | página HTML da rede inteira, com filtros, linha do tempo e um seletor do modelo que pinta o risco (todos os modelos, separados em não supervisionados e supervisionados e ordenados pela AP) | `data/synthetic/` | `reports/estudos/rede_completa.html` | ~1 min |
| [`criar_grafo.py`](02_exploracao/criar_grafo.py) | grafos avulsos: padrões, CSVs quaisquer, trilha do dinheiro, fluxo | CSV ou padrão | o arquivo de `--saida` | segundos |

### 3. Modelos

[`03_modelos/`](03_modelos/): ajuste, otimização dos hiperparâmetros e a vitrine de todos os modelos.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`rodar_experimento.py`](03_modelos/rodar_experimento.py) | uma rodada: grafo, atributos, 2 detectores × 6 conjuntos, figuras | `data/synthetic/` | `reports/03_modelos/results/metricas.csv`, `reports/03_modelos/figures/grafo_de_calor_*`, `heatmap_risco_*` | ~1 min |
| [`avaliar_modelos.py`](03_modelos/avaliar_modelos.py) | vitrine de todos os modelos nas mesmas contas: não supervisionados, só estrutura (FRAUDAR, node2vec), semi-supervisionados (PageRank, label spreading) e tetos (Random Forest, gradient boosting, GraphSAGE); `--config configs/experimento_otimizado.yaml` avalia os hiperparâmetros otimizados | `configs/cenarios.yaml` | `reports/03_modelos/results/modelos_*`, `modelos_*.png` | ~35 min (5 cenários × 10 sementes, 4 processos) |
| [`otimizar_hiperparametros.py`](03_modelos/otimizar_hiperparametros.py) | busca em grade dos hiperparâmetros de cada modelo, em rodadas: quando o vencedor cai na ponta da grade, ela se amplia e testa de novo, até achar o melhor; escolhida em redes de **validação** (sementes 1001+, nunca usadas na avaliação) dos cenários realistas | `configs/busca_hiperparametros.yaml`, `configs/cenarios.yaml` | `reports/03_modelos/results/otimizacao_*`, `configs/experimento_otimizado.yaml` | ~1 h (3 cenários × 2 redes, 4 processos) |

### 4. Avaliação

[`04_avaliacao/`](04_avaliacao/): repetir com várias sementes e cenários e comparar com inferência.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`avaliar_robustez.py`](04_avaliacao/avaliar_robustez.py) | repete com várias sementes; IC e testes pareados | configuração | `reports/04_avaliacao/results/robustez_*.csv`, `robustez_average_precision.png` | ~4 min (10 sementes) |
| [`avaliar_sementes.py`](04_avaliacao/avaliar_sementes.py) | quantas sementes bastam? AP média e IC 95% com 10, 100, 500 e 1000 sementes; variação da média de 10 sementes sorteadas | configuração | `reports/04_avaliacao/results/sementes_*.csv`, `sementes_convergencia.png` | ~1,5 h (1000 sementes, 4 processos) |
| [`avaliar_cenarios.py`](04_avaliacao/avaliar_cenarios.py) | repete em cada cenário de dificuldade | `configs/cenarios.yaml` | `reports/04_avaliacao/results/cenarios_*.csv`, `cenarios_*.png` | ~40 min (8 cenários × 10 sementes) |
| [`avaliar_deteccao_online.py`](04_avaliacao/avaliar_deteccao_online.py) | detecção ao longo do tempo: bloqueou a tempo? | `configs/cenarios.yaml` | `reports/04_avaliacao/results/online_*`, `online_deteccao.png` | dezenas de minutos |
| [`avaliar_atributos.py`](04_avaliacao/avaliar_atributos.py) | ablação por atributo e teto supervisionado (Random Forest com os rótulos) | `configs/cenarios.yaml` | `reports/04_avaliacao/results/atributos_*`, `atributos_*.png` | ~20 min (5 sementes) |
| [`avaliar_propagacao.py`](04_avaliacao/avaliar_propagacao.py) | culpa por associação: com parte das fraudes conhecidas, quanto se acha do resto? | `configs/cenarios.yaml` | `reports/04_avaliacao/results/propagacao_*`, `propagacao_average_precision.png` | ~10 min (10 sementes) |
| [`avaliar_fraudar.py`](04_avaliacao/avaliar_fraudar.py) | FRAUDAR: blocos densos (só estrutura) contra o melhor detector e combinados | `configs/cenarios.yaml` | `reports/04_avaliacao/results/fraudar_*`, `fraudar_average_precision.png` | ~15 min (10 sementes) |
| [`avaliar_gnn.py`](04_avaliacao/avaliar_gnn.py) | redes neurais para grafos: DOMINANT (não supervisionado) e GraphSAGE (teto supervisionado) contra DBSCAN e Random Forest; precisa de `pip install -e ".[gnn]"` | `configs/cenarios.yaml` | `reports/04_avaliacao/results/gnn_*`, `gnn_average_precision.png` | ~25 min (5 sementes) |
| [`avaliar_gnn_rotulos.py`](04_avaliacao/avaliar_gnn_rotulos.py) | GraphSAGE e Random Forest treinados só com 10% ou 25% das fraudes conhecidas, contra DBSCAN e culpa por associação; precisa do torch | `configs/cenarios.yaml` | `reports/04_avaliacao/results/gnn_rotulos_*`, `gnn_rotulos_average_precision.png` | ~40 min (10 sementes) |
| [`avaliar_externo.py`](04_avaliacao/avaliar_externo.py) | mesma configuração num dataset externo, por janelas; recall por tipologia | `data/external/<nome>/` | `reports/amlworld/` | minutos por janela |

### 5. Interpretação

[`05_interpretacao/`](05_interpretacao/): entender os erros dos modelos.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`investigar_falsos_positivos.py`](05_interpretacao/investigar_falsos_positivos.py) | quem são as contas de maior risco que não são fraude, com o papel real e os atributos que as levam ao topo (reunião de 01/10) | `configs/cenarios.yaml`, `data/synthetic/` | `reports/05_interpretacao/results/falsos_positivos_*`, `falsos_positivos_comercio.png` | ~1 h (4 cenários × 10 sementes) |

### Ferramentas

[`ferramentas/`](ferramentas/): busca, grafo de notas, ilustrações e relatório.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`gerar_ilustracoes.py`](ferramentas/gerar_ilustracoes.py) | figuras explicativas do README: padrões, GIF da quadrilha e recorte da rede | configuração | `reports/ilustracoes/padroes_de_fraude.png`, `quadrilha.gif`, `rede_exemplo.png` | ~1 min |
| [`exportar_grafo_de_notas.py`](ferramentas/exportar_grafo_de_notas.py) | grafo de notas do Obsidian em JSON, para agentes de IA (ver [obsidian.md](../docs/obsidian.md)) | notas `.md` do cofre | `docs/grafo-de-notas.json` | segundos |
| [`buscar.py`](ferramentas/buscar.py) | busca única no código (Graphify) e no texto de todas as notas, sem acentos nem LLM; para agentes de IA (ver [obsidian.md](../docs/obsidian.md)) | `graphify-out/graph.json`, notas `.md`, `docs/grafo-de-notas.json` | só imprime | ~1 s |
| [`ilustrar_grafos_de_conhecimento.py`](ferramentas/ilustrar_grafos_de_conhecimento.py) | figuras do README: grafo de notas (cores do Obsidian) e mapa do código (Graphify) | `docs/grafo-de-notas.json`, `graphify-out/graph.json` | `reports/ilustracoes/grafo_de_notas.png`, `grafo_do_codigo.png` | segundos |

### Pipeline

raiz de `scripts/`: refaz tudo na ordem.

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`reproduzir_tudo.py`](reproduzir_tudo.py) | refaz todos os resultados na ordem certa (ver abaixo); [`reproduzir_tudo.ps1`](reproduzir_tudo.ps1) é um atalho para ele | configuração | `reports/` | algumas horas |

`avaliar_robustez.py`, `avaliar_cenarios.py`, `avaliar_propagacao.py` e `avaliar_modelos.py`
aceitam `--processos N` (sementes em paralelo; a memória cresce com N) e `--modelos` (só
alguns detectores), e usam 20 sementes por padrão. O `reproduzir_tudo.py` passa o nº de
sementes explicitamente, então esse padrão não muda a reprodução oficial.

As avaliações longas (`avaliar_externo.py`, `avaliar_deteccao_online.py` e `avaliar_sementes.py`) salvam cada
janela ou semente assim que terminam. Se forem interrompidas, rodar de novo continua de
onde parou; `--refazer` recalcula tudo.

## Reproduzir os resultados

Um comando refaz tudo na ordem certa. Com a configuração versionada, os resultados saem
idênticos (as sementes são fixas):

```powershell
python scripts/reproduzir_tudo.py              # completo (algumas horas); o AMLworld entra se já tiver sido importado
python scripts/reproduzir_tudo.py --rapido     # poucas sementes, em reports_teste/: só confere que tudo roda
python scripts/reproduzir_tudo.py --refazer    # recalcula também o progresso salvo das avaliações longas
python scripts/reproduzir_tudo.py --etapas dataset experimento   # só algumas etapas, na ordem do pipeline
python scripts/reproduzir_tudo.py --extras     # + rede, ilustrações, grafos e relatório; abre Graphify e Obsidian no fim
python scripts/reproduzir_tudo.py --extras --sem-abrir   # os extras, sem abrir nada
python scripts/reproduzir_tudo.py --listar     # mostra as etapas, o tempo médio e os comandos, sem rodar
```

As etapas são `dataset`, `experimento`, `robustez`, `cenarios`, `online`, `atributos`,
`propagacao`, `fraudar`, `gnn` (pulada se o torch não estiver instalado) e `externo`. O dataset usa `--seed 42`, por isso o modo completo reproduz
`reports/`. Uma etapa que falha interrompe as seguintes. O `.\scripts\reproduzir_tudo.ps1`
continua funcionando (`-Rapido`, `-Refazer`) e só chama o `.py`.

**Extras** (`--extras`, ou escolhidas uma a uma em `--etapas`): `rede`
(`visualizar_rede.py`), `ilustracoes` (`gerar_ilustracoes.py`), `notas`
(`exportar_grafo_de_notas.py`), `graphify` (`graphify update .`, pulada se o Graphify não
estiver instalado) e `relatorio` (`gerar_relatorio.py`, docx em `relatorio/saida/`). No
fim, abre no navegador a página da rede e a do Graphify (`graphify-out/graph.html`) e
abre o cofre no Obsidian pela URI `obsidian://open?path=...`, que só funciona se o cofre
já tiver sido aberto uma vez no Obsidian. `--sem-abrir` desliga isso. Continuam manuais:
o download do BCB (instável, ver [data/README.md](../data/README.md)), o
`importar_dataset.py`, o `criar_grafo.py` e o explorador em Streamlit.

**Tempo médio de cada etapa.** Cada execução anota a duração de cada etapa em
`data/tempos_reproduzir.csv` (fora do git, porque depende da máquina), separada por modo
(completo ou rápido). O `--listar` e o início de cada etapa mostram a média desse
histórico. Enquanto não houver histórico, vale a `duracao_s` do `*_meta.json` da etapa e,
no modo completo, o tempo aproximado da tabela acima. No fim, sai o tempo de cada etapa
nesta execução, a média e o total.

Cada script de avaliação grava, ao lado dos resultados, um `*_meta.json` com o commit do
git, a configuração, as sementes, a duração e as versões dos pacotes usados. Se
`alteracoes_nao_commitadas` for `true`, o resultado foi gerado com código que ainda não
estava num commit.

O que cada arquivo gerado contém está em [`reports/mapa-dos-resultados.md`](../reports/mapa-dos-resultados.md).
