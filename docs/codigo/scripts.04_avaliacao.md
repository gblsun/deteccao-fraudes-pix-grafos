---
tags: [codigo]
---

# `scripts/04_avaliacao/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Etapa 4: repetições com sementes e cenários e comparações com inferência. Guia da pasta: [README.md](../../scripts/04_avaliacao/README.md) · [mapa do código](mapa-do-codigo.md)

## [`avaliar_atributos.py`](../../scripts/04_avaliacao/avaliar_atributos.py)

Quanto cada atributo contribui, e quão longe estamos de um modelo que viu os rótulos?

Duas análises, nos cenários escolhidos e com várias sementes:

* **ablação**: tira um atributo de cada vez do conjunto (padrão: `completo`) e
  mede a queda da average precision de cada detector;
* **teto supervisionado**: modelos treinados com os rótulos (validação cruzada
  de 5 partes), ao lado dos detectores não supervisionados: Random Forest e
  gradient boosting em cada conjunto de atributos, e, se o extra `gnn` estiver
  instalado, uma GraphSAGE com os atributos `tabular` e `completo` (ela
  aprende a estrutura do grafo sozinha, então dá para ver se isso supre a
  falta dos atributos de grafo).

Saídas em reports/04_avaliacao/results/:
    atributos_ablacao.csv          uma linha por (cenário, semente, modelo, atributo removido)
    atributos_ablacao_resumo.csv   queda média de AP por (cenário, modelo, atributo)
    atributos_teto.csv             AP de cada (cenário, semente, conjunto, modelo), com o supervisionado
    atributos_teto_resumo.csv      média e IC 95% da AP
    atributos_meta.json            como o resultado foi gerado
e as figuras reports/04_avaliacao/figures/atributos_ablacao.png e atributos_teto.png.

Uso:
    python scripts/04_avaliacao/avaliar_atributos.py --sementes 5
    python scripts/04_avaliacao/avaliar_atributos.py --cenarios realista --sementes 2 --conjunto grafo_avancado

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['sem_atalhos', 'realista']` |  |
| `--sementes` | `10` |  |
| `--conjunto` | `'completo'` | conjunto de atributos da ablação |
| `--modelos` | — | detectores (padrão: todos) |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _plot_ablation(summary: pd.DataFrame, args, path: Path) -> None`: Matriz atributo × (cenário, modelo) da queda média de AP ao tirar o atributo.
- `def _plot_ceiling(summary: pd.DataFrame, args, path: Path) -> None`: Um painel por cenário: conjunto de atributos × modelo, da AP média (tetos supervisionados à direita).

## [`avaliar_cenarios.py`](../../scripts/04_avaliacao/avaliar_cenarios.py)

Avalia os detectores em cenários de dificuldade (configs/cenarios.yaml).

O gerador sintético embute sinais "fáceis" por construção (golpes a qualquer
hora, contas fraudulentas recém-abertas, pessoas sempre ativas). Cada cenário
desliga parte deles; o script repete o experimento com várias sementes em
cada cenário para mostrar quais conclusões sobrevivem, em especial a
comparação entre atributos tabulares e de grafo.

Saídas em reports/04_avaliacao/results/:
    cenarios_execucoes.csv    uma linha por (cenário, semente, atributos, modelo)
    cenarios_resumo.csv       média, desvio e IC 95% de cada métrica, por cenário
    cenarios_comparacoes.csv  testes pareados entre conjuntos de atributos, por cenário
    cenarios_efeitos.csv      delta de Cliff (fraude × normal) de cada atributo, por cenário
e as figuras reports/04_avaliacao/figures/cenarios_average_precision.png e cenarios_efeitos.png.

Uso:
    python scripts/04_avaliacao/avaliar_cenarios.py --sementes 20 --processos 3
    python scripts/04_avaliacao/avaliar_cenarios.py --cenarios base realista --sementes 3
    python scripts/04_avaliacao/avaliar_cenarios.py --cenarios calibrado --modelos isolation_forest dbscan ecod
    python scripts/04_avaliacao/avaliar_cenarios.py --so-figuras    # redesenha as figuras sem rodar de novo

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | — | cenários a rodar (padrão: todos, na ordem do arquivo) |
| `--sementes` | `20` | nº de repetições por cenário (sementes 1, 2, ...) |
| `--modelos` | — | detectores (padrão: todos) |
| `--processos` | `1` | sementes rodando ao mesmo tempo (memória!) |
| `--saida` | `'reports/04_avaliacao'` |  |
| `--so-figuras` | desligada | não roda nada: redesenha as figuras a partir dos CSVs já salvos em --saida |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _evaluate(config: dict, base, scenarios: dict[str, dict], n_seeds: int, models: list[str] | None=None, processes: int=1)`: Roda cada cenário com `n_seeds` sementes; devolve execuções, resumo, comparações e efeitos.
- `def _plot_metric(summary: pd.DataFrame, names: list, fraud_rate: pd.Series, path: Path, n: int) -> None`: Matriz conjunto de atributos × cenário da média da métrica, um painel por modelo.
- `def _plot_effects(effects: pd.DataFrame, names: list, path: Path) -> None`: Matriz atributo × cenário do delta de Cliff médio (> 0: maior nas contas fraudulentas).

## [`avaliar_deteccao_online.py`](../../scripts/04_avaliacao/avaliar_deteccao_online.py)

Avalia a detecção ao longo do tempo: a quadrilha é sinalizada a tempo de bloquear o dinheiro?

Para cada cenário e semente, gera o dataset e roda os detectores a cada
--frequencia, vendo só os Pix feitos até cada ponto de corte. A cada corte, um
analista revisa as k contas mais suspeitas (k = nº de contas fraudulentas).
Depois reproduz os Pix da quadrilha, bloqueando cada conta no corte em que ela
foi sinalizada (ver pixfraud.online).

Métricas por (cenário, semente, atributos, modelo):
    detectadas_72h     fração das contas fraudulentas sinalizadas até --horizonte depois
                       do primeiro golpe que receberam
    atraso_mediano_h   atraso mediano (horas) até a sinalização, entre as detectadas
    recuperado_<prazo> fração do dinheiro roubado que ficou retida em contas bloqueadas,
                       supondo que o dinheiro parado numa conta da quadrilha é sacado
                       depois de <prazo>. Há um valor para cada prazo de --saque,
                       porque essa premissa pesa muito no resultado.
A linha "oráculo" sinaliza cada conta fraudulenta no primeiro corte depois da
exposição: é o teto imposto só pela frequência dos cortes.

Saídas: reports/04_avaliacao/results/online_execucoes.csv, online_resumo.csv e
online_comparacoes.csv, e a figura reports/04_avaliacao/figures/online_deteccao.png. As
sinalizações de cada cenário e semente ficam em reports/04_avaliacao/results/online_cortes/
e são reaproveitadas se o script rodar de novo (--refazer recalcula).

Uso:
    python scripts/04_avaliacao/avaliar_deteccao_online.py --sementes 3
    python scripts/04_avaliacao/avaliar_deteccao_online.py --cenarios realista --sementes 1 --frequencia 12h

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['sem_atalhos', 'realista']` |  |
| `--sementes` | `5` |  |
| `--conjuntos` | `['tabular', 'grafo', 'temporal', 'compl…` |  |
| `--frequencia` | `'6h'` | intervalo entre os pontos de corte |
| `--horizonte` | `'72h'` | prazo para a detecção contar (bloqueio cautelar) |
| `--saque` | `['1h', '6h', '24h']` | tempos até o dinheiro parado ser sacado (um resultado para cada) |
| `--modelos` | — | detectores (padrão: todos) |
| `--saida` | `'reports/04_avaliacao'` |  |
| `--refazer` | desligada | recalcula as sinalizações já salvas |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _metrics(first: pd.Series, exposure: pd.Series, tx: pd.DataFrame, fraud, horizon: pd.Timedelta, cashouts: list[str]) -> dict`: Fração detectada em até 72 h, atraso mediano e dinheiro recuperado em cada prazo de saque.
- `def _plot(summary: pd.DataFrame, names: list, sets: list, models: list, path: Path, args) -> None`: Painéis modelo × métrica; em cada um, conjunto de atributos (e oráculo) × cenário.

## [`avaliar_externo.py`](../../scripts/04_avaliacao/avaliar_externo.py)

Avalia os detectores num dataset externo (AMLworld), janela por janela.

Usa a mesma configuração do dataset sintético (configs/experimento.yaml), sem
reajustar nada. Cada janela de --dias-janela dias é uma repetição, no lugar das
sementes: as comparações entre conjuntos de atributos são pareadas por janela.
Se a pasta de dados tiver patterns.csv (importar_dataset.py --padroes), mede
também o recall@k de cada tipologia de lavagem.

Saídas em <saida>/results/, com o nome da pasta de dados como prefixo:
    <nome>_execucoes.csv     uma linha por (janela, atributos, modelo)
    <nome>_resumo.csv        média, desvio e IC 95% de cada métrica
    <nome>_comparacoes.csv   testes pareados entre conjuntos de atributos
    <nome>_tipologias.csv    recall@k por tipologia (se houver patterns.csv)
e a figura <saida>/figures/<nome>_tipologias.png.

Uso:
    python scripts/04_avaliacao/avaliar_externo.py --dados data/external/amlworld_pix --saida reports/amlworld
    python scripts/04_avaliacao/avaliar_externo.py --dados data/external/amlworld --max-janelas 1   # teste rápido

Cada janela é salva em <saida>/results/<nome>_janelas/ assim que termina. Se a
execução for interrompida, rodar de novo reaproveita as janelas prontas
(--refazer recalcula tudo, por exemplo depois de mudar a configuração).

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--dados` | — | pasta com accounts.csv e transactions.csv (e patterns.csv) |
| `--dias-janela` | `3` |  |
| `--min-fraudes` | `20` | pula janelas com menos contas fraudulentas |
| `--max-fracao-fraude` | `0.2` | pula janelas em que as contas fraudulentas passam dessa fração (sem movimento normal) |
| `--max-janelas` | — | para depois de N janelas avaliadas (teste rápido) |
| `--modelos` | — | detectores (padrão: todos) |
| `--saida` | `'reports/externo'` |  |
| `--refazer` | desligada | recalcula as janelas já salvas |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _pool(recalls: pd.DataFrame) -> pd.DataFrame`: Junta as janelas: acertos somados sobre contas somadas, por tipologia, atributos e modelo.
- `def _plot_typologies(typologies: pd.DataFrame, path: Path, name: str) -> None`: Matriz tipologia × conjunto de atributos do recall@k, um painel por modelo.

## [`avaliar_fraudar.py`](../../scripts/04_avaliacao/avaliar_fraudar.py)

FRAUDAR: blocos densos acham as quadrilhas? E quando a rede legítima também é densa?

O FRAUDAR (Hooi et al., 2016) procura, um depois do outro, os subgrafos mais densos com
pesos que resistem a camuflagem (`pixfraud.communities.fraudar_blocks`). Não usa rótulos
nem atributos, só a estrutura do grafo. Este script compara, em cada cenário e semente:

* `fraudar`: escore por conta = densidade do bloco em que ela está
  (`fraudar_scores`; blocos com mais de 5% das contas não pontuam);
* `completo_dbscan`: o melhor detector não supervisionado de atributos;
* `combinado`: média dos percentis dos dois.

Também mede o conjunto marcado pelo FRAUDAR (contas com escore > 0): quantas contas e que
fração das fraudes ele cobre.

Saídas em reports/04_avaliacao/results/: fraudar_execucoes.csv, fraudar_resumo.csv,
fraudar_comparacoes.csv e fraudar_meta.json, e a figura
reports/04_avaliacao/figures/fraudar_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_fraudar.py --sementes 10
    python scripts/04_avaliacao/avaliar_fraudar.py --cenarios base realista --sementes 3

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['base', 'sem_atalhos', 'com_inativos',…` |  |
| `--sementes` | `10` |  |
| `--blocos` | `10` | nº máximo de blocos do FRAUDAR |
| `--fatia-maxima` | `0.05` | blocos com mais que esta fração das contas não pontuam |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _plot(summary: pd.DataFrame, args, path: Path) -> None`: Matriz método × cenário da AP média.

## [`avaliar_gnn.py`](../../scripts/04_avaliacao/avaliar_gnn.py)

Redes neurais para grafos: aprender a estrutura ajuda a achar fraude?

Compara, em cada cenário e semente, as GNN de `pixfraud.gnn` com o que o projeto
já tinha:

* não supervisionados (sem rótulos): `dominant_tabular` e `dominant_completo`
  (autoencoder de grafo DOMINANT com os atributos tabulares ou com todos) contra
  `completo_dbscan`, o melhor detector de atributos;
* supervisionados (tetos, em validação cruzada de 5 dobras): `sage_tabular` e
  `sage_completo` (GraphSAGE) contra `rf_tabular` e `rf_completo` (o Random Forest
  de `avaliar_atributos.py`). A pergunta do `tabular`: com os mesmos atributos
  simples, a GNN aprende sozinha o que os atributos de grafo feitos à mão capturam?

Precisa do torch: `pip install -e ".[gnn]"`.

Saídas em reports/04_avaliacao/results/: gnn_execucoes.csv, gnn_resumo.csv, gnn_comparacoes.csv e
gnn_meta.json, e a figura reports/04_avaliacao/figures/gnn_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_gnn.py --sementes 10
    python scripts/04_avaliacao/avaliar_gnn.py --cenarios realista --sementes 3

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['sem_atalhos', 'realista']` |  |
| `--sementes` | `10` |  |
| `--epocas` | `None` | épocas de treino (padrão: as de pixfraud.gnn) |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _plot(summary: pd.DataFrame, args, path: Path) -> None`: Matriz método × cenário da AP média.

## [`avaliar_gnn_rotulos.py`](../../scripts/04_avaliacao/avaliar_gnn_rotulos.py)

GraphSAGE com poucos rótulos: a vantagem da GNN sobrevive quando só parte das fraudes é conhecida?

Em `avaliar_gnn.py` a GraphSAGE treina com os rótulos de 80% das contas. No Pix,
só uma fração das contas fraudulentas vira conhecida (quando as vítimas contestam pelo
MED) e todas as outras aparecem como "não fraude". Como em `avaliar_propagacao.py`,
este script sorteia uma fração das fraudes como "já contestadas" e mede, **só nas contas
restantes**, a average precision de:

* `sage_tabular` e `sage_completo`: GraphSAGE treinada com as fraudes conhecidas
  (`pixfraud.gnn.sage_known_fraud_scores`), com os atributos tabulares ou com todos;
* `rf_tabular` e `rf_completo`: Random Forest com os mesmos rótulos e atributos
  (`pixfraud.experiment.known_fraud_scores`);
* `completo_dbscan`: o melhor detector não supervisionado, que não usa rótulo nenhum;
* `propagacao_combinado`: o melhor método da culpa por associação (média dos
  percentis da propagação relativa e do `completo_dbscan`).

Precisa do torch: `pip install -e ".[gnn]"`.

Saídas em reports/04_avaliacao/results/: gnn_rotulos_execucoes.csv, gnn_rotulos_resumo.csv,
gnn_rotulos_comparacoes.csv e gnn_rotulos_meta.json, e a figura
reports/04_avaliacao/figures/gnn_rotulos_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_gnn_rotulos.py --sementes 10
    python scripts/04_avaliacao/avaliar_gnn_rotulos.py --cenarios realista --fracoes 0.1 --sementes 3

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['sem_atalhos', 'realista']` |  |
| `--sementes` | `10` |  |
| `--fracoes` | `[0.1, 0.25]` | frações das contas fraudulentas tratadas como já conhecidas |
| `--epocas` | `None` | épocas de treino (padrão: as de pixfraud.gnn) |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _plot(summary: pd.DataFrame, args, path: Path) -> None`: Matriz método × (cenário, fração conhecida) da AP média.

## [`avaliar_propagacao.py`](../../scripts/04_avaliacao/avaliar_propagacao.py)

Culpa por associação: com algumas fraudes já conhecidas, quanto se acha do resto?

No Pix, parte das contas fraudulentas vira conhecida quando as vítimas contestam
(MED). Este script sorteia uma fração das contas fraudulentas como "já
contestadas" e mede, **só nas contas restantes**, a average precision de:

* `propagacao` e `propagacao_relativa`: PageRank personalizado a partir das
  contas conhecidas (`pixfraud.flow.propagate_risk`); a relativa divide pelo
  PageRank comum, para não favorecer as contas muito conectadas;
* `completo_dbscan` e `temporal_if`: os melhores detectores não supervisionados,
  que não usam as contas conhecidas;
* `combinado`: média dos percentis da propagação relativa e do `completo_dbscan`;
* `label_spreading`: propagação de rótulos com as fraudes conhecidas (+1) **e**
  uma fração das contas legítimas também tratadas como conhecidas (-1), a mesma
  fração das fraudes (`pixfraud.flow.label_spreading`);
* `label_spreading_combinado`: média dos percentis do label spreading e do
  `completo_dbscan`.

As contas conhecidas (fraudes e legítimas) ficam fora da avaliação de todos os
métodos. Com `--conhecidas contestacao`, as fraudes conhecidas deixam de ser
sorteadas: são as contas que receberam um golpe contestado até o fim do período
(coluna `contestado_em`, só nos cenários com `p_contested` > 0), como no MED.

Saídas em reports/04_avaliacao/results/: propagacao_execucoes.csv, propagacao_resumo.csv,
propagacao_comparacoes.csv e propagacao_meta.json, e a figura
reports/04_avaliacao/figures/propagacao_average_precision.png.

Uso:
    python scripts/04_avaliacao/avaliar_propagacao.py --sementes 10
    python scripts/04_avaliacao/avaliar_propagacao.py --cenarios realista --fracoes 0.1 --sementes 3
    python scripts/04_avaliacao/avaliar_propagacao.py --cenarios calibrado --conhecidas contestacao

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['sem_atalhos', 'realista']` |  |
| `--sementes` | `20` |  |
| `--fracoes` | `[0.1, 0.25]` | frações das contas fraudulentas tratadas como já conhecidas |
| `--conhecidas` | `'fracao'` | fraudes conhecidas sorteadas (--fracoes) ou vindas das contestações |
| `--fracao-legitimas` | `None` | fração das legítimas conhecidas no modo contestacao (padrão: 0,25) |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _known_frauds(args, rng, fraud, tx)`: As fraudes tratadas como conhecidas: `(rótulo, contas)` para cada nível avaliado.
- `def _mean_percentile(scores: dict, labels: pd.Series, *methods: str) -> pd.Series`: Combinação de métodos: média dos percentis de cada um, nas contas avaliadas.
- `def _known_label(level) -> str`: Rótulo do nível de conhecimento: as contestações ou a fração de fraudes conhecidas.
- `def _scores(prepared, feature_set: str, model: str, models: dict) -> pd.Series`: Escore de um detector não supervisionado (não usa as contas conhecidas).
- `def _plot(summary: pd.DataFrame, args, path: Path) -> None`: Matriz método × (cenário, fração conhecida) da AP média.

## [`avaliar_robustez.py`](../../scripts/04_avaliacao/avaliar_robustez.py)

Avalia a robustez do experimento repetindo-o com várias sementes.

Cada semente gera um dataset sintético diferente (e muda a semente dos
detectores aleatórios). Para cada conjunto de atributos e modelo, o script calcula
a média e o intervalo de confiança das métricas. Depois compara abordagens
com testes pareados (a mesma semente é avaliada pelas duas abordagens), com
correção de Holm para as várias comparações de cada métrica. Para repetir a
avaliação em cenários de dificuldade diferentes, use `avaliar_cenarios.py`.

Saídas em reports/04_avaliacao/results/:
    robustez_execucoes.csv    uma linha por (semente, atributos, modelo)
    robustez_resumo.csv       média, desvio e IC de cada métrica
    robustez_comparacoes.csv  testes pareados entre conjuntos de atributos
e a figura reports/04_avaliacao/figures/robustez_<métrica>.png.

Uso:
    python scripts/04_avaliacao/avaliar_robustez.py --sementes 20 --processos 3
    python scripts/04_avaliacao/avaliar_robustez.py --modelos isolation_forest ecod   # só alguns detectores

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--sementes` | `20` | nº de repetições (sementes 1, 2, ...) |
| `--modelos` | — | detectores (padrão: todos) |
| `--processos` | `1` | sementes rodando ao mesmo tempo (memória!) |
| `--saida` | `'reports/04_avaliacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _plot(summary: pd.DataFrame, path: Path, n: int) -> None`: AP média e IC 95% de cada detector em cada conjunto de atributos.

## [`avaliar_sementes.py`](../../scripts/04_avaliacao/avaliar_sementes.py)

Quantas sementes bastam? Convergência da average precision média.

Pedido da reunião de 24/09: os estudos de robustez usam 10 sementes por chave
(atributos, modelo); a pergunta é se a média da average precision (AP) muda
com 100, 500 ou 1000 sementes. O script roda o experimento de
`avaliar_robustez.py` com muitas sementes e mede, para cada chave:

* a média, o desvio e o IC 95% da AP usando só as primeiras `n` sementes,
  para cada `n` de `--marcos` (10, 100, 500, 1000);
* quanto a média de **10 sementes sorteadas** varia em torno da média com
  todas as sementes (faixa de 95% em `--sorteios` sorteios sem reposição);
* com que frequência 10 sementes elegem a mesma melhor chave que todas;
* para cada comparação pareada de `experiment.COMPARISONS` (ex.: completo -
  tabular), a diferença média, o desvio das diferenças e quantas sementes um
  teste pareado precisa para detectar essa diferença com poder de 80%.

Cada semente é gravada assim que termina, então dá para interromper e rodar
de novo: as sementes que já estão no CSV são puladas.

Saídas em reports/04_avaliacao/results/:
    sementes_execucoes.csv     uma linha por (semente, atributos, modelo)
    sementes_convergencia.csv  média, desvio e IC 95% da AP para cada marco
    sementes_sorteios.csv      variação da média de 10 sementes sorteadas
    sementes_pareadas.csv      sementes necessárias para cada comparação pareada
    sementes_meta.json         como o resultado foi gerado
e a figura reports/04_avaliacao/figures/sementes_convergencia.png.

Uso:
    python scripts/04_avaliacao/avaliar_sementes.py --sementes 1000 --processos 4
    python scripts/04_avaliacao/avaliar_sementes.py --cenario realista --sementes 100
    python scripts/04_avaliacao/avaliar_sementes.py --so-analise    # refaz tabelas e figura a partir do CSV

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenario` | `'base'` | cenário de configs/cenarios.yaml |
| `--sementes` | `1000` | sementes 1, 2, ..., N |
| `--processos` | `1` | sementes rodando ao mesmo tempo |
| `--modelos` | `list(MODEL_COLORS)` | detectores (padrão: os 3 das 1000 sementes salvas, para a retomada continuar comparável) |
| `--marcos` | `[10, 100, 500, 1000]` |  |
| `--sorteios` | `2000` | nº de sorteios de --tamanho-sorteio sementes |
| `--tamanho-sorteio` | `10` | sementes por sorteio (hoje, 10) |
| `--atributos-figura` | `'completo'` | conjunto de atributos da figura |
| `--saida` | `'reports/04_avaliacao'` |  |
| `--so-analise` | desligada | não roda sementes novas |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _paired_needs(runs: pd.DataFrame, power: float=0.8, alpha: float=0.05) -> pd.DataFrame`: Diferença pareada média de cada comparação e o nº de sementes para detectá-la.
- `def _seeds_for_power(effect: float, power: float, alpha: float, minimum: int=6, maximum: int=100000)`: Menor nº de sementes para um teste t pareado detectar o efeito padronizado `effect`.
- `def _suffix(scenario: str) -> str`: Sufixo dos arquivos de saída: vazio no cenário `base`.
- `def _one_seed(simulation, config, seed: int, models: list[str]) -> pd.DataFrame`: Roda uma semente (em outro processo, com `--processos` > 1).
- `def _run(simulation, config, seeds: list[int], processes: int, models: list[str], path: Path) -> None`: Roda `seeds` e acrescenta cada resultado ao CSV assim que fica pronto.
- `def _convergence(runs: pd.DataFrame, marks: list[int]) -> pd.DataFrame`: Média, desvio e IC 95% da AP usando só as sementes 1..n, para cada marco n.
- `def _draws(runs: pd.DataFrame, n_draws: int, size: int=10, seed: int=0) -> tuple[pd.DataFrame, float]`: Quanto a média de `size` sementes sorteadas se afasta da média com todas as sementes.
- `def _plot(convergence: pd.DataFrame, feature_set: str, path: Path, scenario: str) -> None`: Dois painéis: AP média com IC 95% e meia-largura do IC, ambos contra o nº de sementes.
