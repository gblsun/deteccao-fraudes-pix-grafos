---
tags: [codigo]
---

# `scripts/03_modelos/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Etapa 3: rodada única, otimização dos hiperparâmetros e vitrine dos modelos. Guia da pasta: [README.md](../../scripts/03_modelos/README.md) · [mapa do código](mapa-do-codigo.md)

## [`avaliar_modelos.py`](../../scripts/03_modelos/avaliar_modelos.py)

Vitrine de todos os modelos: qual abordagem funciona, e em qual cenário?

Para cada cenário e semente, gera o dataset e avalia quatro famílias de modelos
**nas mesmas contas**, para os números serem comparáveis entre elas:

* **não supervisionados** (`pixfraud.anomaly.DETECTORS`), no conjunto de
  atributos `--conjunto` (padrão: `completo`);
* **estrutura do grafo** (`pixfraud.graph_models.GRAPH_DETECTORS`): FRAUDAR e
  node2vec, que não usam a tabela de atributos, e, com o extra `gnn`, o
  DOMINANT (GNN não supervisionada, que usa o grafo e os atributos);
* **semi-supervisionados**: parte das fraudes já é conhecida e 25% das contas
  legítimas também. No cenário com a coluna `contestado_em`, as fraudes
  conhecidas são as contestadas até o fim do período, como no MED; nos demais,
  são 25% sorteadas. Os métodos são o PageRank relativo, o label spreading e a
  combinação de cada um com o DBSCAN;
* **tetos supervisionados**, treinados com os rótulos em validação cruzada:
  Random Forest, gradient boosting e, com o extra `gnn`, a GraphSAGE.

As contas conhecidas, fraudes ou legítimas, ficam fora da avaliação de
**todos** os modelos. As comparações pareadas (`stats.compare_runs` com
`between="modelo"`) usam o DBSCAN como referência e confrontam as variantes
de cada família.

Saídas em reports/03_modelos/results/:
    modelos_execucoes.csv    uma linha por (cenário, semente, modelo)
    modelos_resumo.csv       média, desvio e IC 95% de cada métrica
    modelos_comparacoes.csv  diferenças pareadas entre modelos
    modelos_friedman.csv     teste de Friedman por cenário: algum modelo difere dos outros?
    modelos_postos.csv       posto médio de cada modelo (Friedman) e a média da AP
    modelos_cenarios_kw.csv  Kruskal-Wallis da AP de cada modelo entre os cenários
    modelos_acaso.csv        o modelo é melhor que o acaso? permutação da AP e hipergeométrico no top-k
    modelos_meta.json        como o resultado foi gerado
e as figuras reports/03_modelos/figures/modelos_average_precision.png, modelos_comparacoes.png e
modelos_diferenca_critica.png (postos médios com a diferença crítica de Nemenyi).

Que teste responde a que pergunta: docs/plano-de-testes-estatisticos.md.

Uso:
    python scripts/03_modelos/avaliar_modelos.py --sementes 20 --processos 3
    python scripts/03_modelos/avaliar_modelos.py --cenarios realista --sementes 2 --sem-gnn
    python scripts/03_modelos/avaliar_modelos.py --so-figuras    # redesenha as figuras a partir dos CSVs

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['base', 'realista', 'calibrado']` |  |
| `--sementes` | `20` |  |
| `--conjunto` | `'completo'` | atributos dos modelos que usam a tabela de atributos |
| `--processos` | `1` | sementes rodando ao mesmo tempo (memória!) |
| `--sem-gnn` | desligada | não roda as GNN (GraphSAGE e DOMINANT) mesmo se estiverem instaladas |
| `--saida` | `'reports/03_modelos'` |  |
| `--so-figuras` | desligada | só redesenha as figuras a partir dos CSVs |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _evaluate_star(job)`: `_evaluate` com os argumentos numa tupla (para o pool de processos).
- `def _evaluate(simulation, name, seed, config, conjunto, use_gnn) -> list[dict]`: Todas as famílias numa semente, avaliadas nas mesmas contas (as que ninguém conhece).
- `def _chance_table(runs: pd.DataFrame, alpha: float=0.05) -> pd.DataFrame`: Por (cenário, modelo): em quantas sementes o modelo foi melhor que o acaso, e a AP contra a taxa de fraude.
- `def _plot_models(summary: pd.DataFrame, names: list, rate: pd.Series, n: int, path: Path) -> None`: Um painel por cenário: cada modelo com a AP média e o IC 95%, agrupados por família.
- `def _plot_comparisons(comparisons: pd.DataFrame, names: list, n: int, path: Path) -> None`: Um painel por cenário: as diferenças pareadas de AP entre modelos.
- `def _plot_critical_difference(friedman: pd.DataFrame, ranks: pd.DataFrame, path: Path) -> None`: Um painel por cenário: postos médios do Friedman com a diferença crítica de Nemenyi.

## [`otimizar_hiperparametros.py`](../../scripts/03_modelos/otimizar_hiperparametros.py)

Otimiza os hiperparâmetros de cada modelo em redes de validação, até achar o melhor, e grava a configuração.

Para cada cenário de `--cenarios` e cada semente de validação (1001, 1002...,
nunca usadas pelos estudos de avaliação), gera a rede, calcula os atributos e
dá nota (average precision) a cada candidato. A busca roda em rodadas:

1. a grade de `configs/busca_hiperparametros.yaml`, mais a configuração atual;
2. para cada modelo cujo vencedor caiu numa ponta da lista (o maior ou o menor
   valor testado), acrescenta um valor além da ponta e testa só as combinações
   novas;
3. repete até nenhum vencedor estar numa ponta que possa crescer, ou até
   `--rodadas`.

O vencedor de cada modelo vai para `--config-saida`, uma cópia de
`--config` com a seção `modelos` trocada. Para medir o ganho sem trapaça,
avalie depois nas sementes de teste (1, 2, 3...):

    python scripts/03_modelos/avaliar_modelos.py --config configs/experimento_otimizado.yaml --saida reports/otimizado

As redes neurais para grafos (DOMINANT e GraphSAGE) ficam de fora: precisam
do extra `gnn` e custam minutos por treino.

Saídas:
    reports/03_modelos/results/otimizacao_execucoes.csv  uma linha por (rodada, cenário, semente, modelo, candidato)
    reports/03_modelos/results/otimizacao_resumo.csv     AP média de cada candidato e qual foi escolhido
    reports/03_modelos/results/otimizacao_meta.json      como o resultado foi gerado, com as grades finais
    configs/experimento_otimizado.yaml        a configuração com os hiperparâmetros escolhidos

Uso:
    python scripts/03_modelos/otimizar_hiperparametros.py --processos 4
    python scripts/03_modelos/otimizar_hiperparametros.py --modelos knn kmeans pca --sementes 1 --rodadas 2

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--grades` | `str(DEFAULT_PATH)` | valores testados de cada hiperparâmetro |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['realista', 'negativos_dificeis', 'qua…` | cenários das redes de validação (padrão: os mais realistas) |
| `--sementes` | `2` | redes de validação por cenário |
| `--rodadas` | `6` | máximo de rodadas de ampliação da grade |
| `--conjunto` | `'completo'` |  |
| `--modelos` | — | padrão: todos os que têm grade |
| `--processos` | `1` | redes avaliadas ao mesmo tempo |
| `--saida` | `'reports/03_modelos'` |  |
| `--config-saida` | `'configs/experimento_otimizado.yaml'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _score_star(job)`: Avalia os candidatos de hiperparâmetros numa rede de validação (para o pool de processos).
- `def _write_config(source: str, target: str, best: dict, scenarios: list, seeds: list, rounds: int) -> None`: Grava a configuração com os hiperparâmetros escolhidos e um cabeçalho de como foram escolhidos.

## [`rodar_experimento.py`](../../scripts/03_modelos/rodar_experimento.py)

Executa o experimento: grafo -> atributos -> detectores -> métricas e figuras.

Compara Isolation Forest e DBSCAN em cada conjunto de atributos de
`pixfraud.features.FEATURE_SETS`. Salva as métricas em
reports/03_modelos/results/metricas.csv e as figuras (grafo de calor e heatmap de risco)
em reports/03_modelos/figures/.

Uso:
    python scripts/03_modelos/rodar_experimento.py --config configs/experimento.yaml --dados data/synthetic

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--dados` | `'data/synthetic'` |  |
| `--atributos` | `'data/processed/features.csv'` |  |
| `--saida` | `'reports/03_modelos'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
