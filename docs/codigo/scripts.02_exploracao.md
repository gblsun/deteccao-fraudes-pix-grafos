---
tags: [codigo]
---

# `scripts/02_exploracao/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Etapa 2: forma da rede, inferência sobre os atributos e visualização. Guia da pasta: [README.md](../../scripts/02_exploracao/README.md) · [mapa do código](mapa-do-codigo.md)

## [`analisar_tipo_de_rede.py`](../../scripts/02_exploracao/analisar_tipo_de_rede.py)

Que tipo de rede é a do Pix sintético? E o que passeios e cosseno dizem sobre as fraudes?

Pedido da reunião de 24/09 (estudar tipo de rede, lei de potência, Barabási–Albert,
componente gigante, passeio aleatório e similaridade de cosseno, depois implementar).
Para cada cenário e semente, gera o dataset e mede (`pixfraud.network`):

* **componentes**: fração das contas na componente gigante fraca e na forte;
* **lei de potência**: expoente `alpha`, `k_min` e distância KS da cauda dos graus
  (total, de entrada e de saída);
* **passeios aleatórios** que seguem o dinheiro a partir das vítimas: em que papel de
  conta eles terminam e que fração passa pelas coletoras;
* **cosseno × Jaccard**: para cada laranja, que fração das 5 contas mais parecidas com
  ela (pelos valores pagos, `cosine_out`, ou só pelos parceiros, `jaccard_out`) também
  é fraudulenta.

Na primeira semente do primeiro cenário, compara ainda a rede com um Erdős–Rényi e um
Barabási–Albert do mesmo tamanho (`compare_network_models`).

Saídas em reports/02_exploracao/results/:
    tipo_de_rede_execucoes.csv  uma linha por (cenário, semente)
    tipo_de_rede_resumo.csv     média e desvio por cenário
    tipo_de_rede_modelos.csv    rede × Erdős–Rényi × Barabási–Albert
    tipo_de_rede_passeios.csv   onde terminam os passeios que saem das vítimas, por papel
    tipo_de_rede_meta.json      como o resultado foi gerado
e a figura reports/02_exploracao/figures/tipo_de_rede_graus.png.

Uso:
    python scripts/02_exploracao/analisar_tipo_de_rede.py
    python scripts/02_exploracao/analisar_tipo_de_rede.py --cenarios base coletor_ativo --sementes 10

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['base', 'realista', 'coletor_ativo']` |  |
| `--sementes` | `5` |  |
| `--passeios` | `20` | passeios por vítima |
| `--saida` | `'reports/02_exploracao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _measure(graph: nx.DiGraph, accounts: pd.DataFrame, walks_per_start: int, seed: int)`: As medidas de uma semente: componentes, lei de potência, passeios e cosseno × Jaccard.
- `def _degree_graphs(graph: nx.DiGraph, seed: int) -> dict[str, nx.Graph]`: A rede e dois grafos aleatórios de mesmo tamanho (Erdős–Rényi e Barabási–Albert).
- `def _ccdf(degrees: np.ndarray) -> tuple[np.ndarray, np.ndarray]`: Distribuição acumulada complementar dos graus positivos: P(grau ≥ k).
- `def _plot_degrees(graphs: dict[str, nx.Graph], graph: nx.DiGraph, path: Path, scenario: str) -> None`: Acumulada complementar dos graus (log-log) em dois painéis.

## [`criar_grafo.py`](../../scripts/02_exploracao/criar_grafo.py)

Cria, resume e salva grafos sem precisar escrever código.

O formato de saída vem da extensão: .png/.svg/.pdf (imagem), .html (interativo,
abre no navegador) ou .gexf/.graphml (para o Gephi).

Exemplos:
    # padrões de fraude prontos (fan_in, fan_out, chain, cycle, scatter_gather, mule_ring)
    python scripts/02_exploracao/criar_grafo.py padrao mule_ring --saida reports/estudos/anel.png
    python scripts/02_exploracao/criar_grafo.py padrao chain --tamanho 6 --saida reports/estudos/cadeia.html

    # qualquer CSV de transações (colunas de origem, destino e, opcionalmente, valor)
    python scripts/02_exploracao/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --contas estudos/dados/exemplo_contas.csv --saida reports/estudos/exemplo.png

    # o caminho do dinheiro em volta de uma conta do dataset sintético
    python scripts/02_exploracao/criar_grafo.py csv data/synthetic/transactions.csv --conta C000167 --saltos 2 --direcao tras --saida reports/estudos/trilha.html

    # só os Pix em ordem cronológica, com no máximo 2h de espera em cada conta
    python scripts/02_exploracao/criar_grafo.py csv data/synthetic/transactions.csv --conta C000167 --temporal --espera 2h --saltos 4 --saida trilha_temporal.png

    # cores pelos grupos (comunidades de Louvain) em vez dos papéis
    python scripts/02_exploracao/criar_grafo.py csv estudos/dados/exemplo_transacoes.csv --cor grupo --saida grupos.png

    # fluxo máximo e o que bloquear entre contas de origem e um destino
    python scripts/02_exploracao/criar_grafo.py fluxo estudos/dados/exemplo_transacoes.csv --de carla fabio --para conta_z --saida fluxo.png

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `nome` | obrigatória |  |
| `--tamanho` | — | nº de vítimas, contas na cadeia etc. (depende do padrão) |
| `arquivo` | obrigatória |  |
| `--origem` | `'sender'` | coluna da conta pagadora |
| `--destino` | `'receiver'` | coluna da conta recebedora |
| `--valor` | `'amount'` | coluna do valor (opcional) |
| `--contas` | — | CSV com account_id e role, para colorir por papel (padrão: accounts.csv na mesma pasta, se existir) |
| `--conta` | — | recorta o grafo em volta desta conta |
| `--saltos` | `2` | alcance do recorte (padrão: 2) |
| `--direcao` | `'ambos'` | frente = para onde o dinheiro foi; tras = de onde veio |
| `--temporal` | desligada | com --conta: só segue Pix em ordem cronológica (precisa da coluna timestamp) |
| `--espera` | — | com --temporal: tempo máximo parado em cada conta, ex.: 30min, 2h, 1D |
| `--cor` | `'papel'` | papel (padrão) ou grupo = comunidades de Louvain |
| `arquivo` | obrigatória |  |
| `--de` | — | conta(s) de origem |
| `--para` | — | conta de destino |
| `--contas` | — | CSV com account_id e role, para colorir por papel |
| `--saida` | — | arquivo de saída (.png, .svg, .pdf, .html, .gexf, .graphml) |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _attach_roles(graph: nx.DiGraph, accounts_path: str | None, transactions_path: Path) -> None`: Copia o papel de cada conta (de accounts.csv) para os vértices do grafo, se houver.

## [`inferencia_atributos.py`](../../scripts/02_exploracao/inferencia_atributos.py)

Inferência sobre os atributos, antes dos modelos: o que distingue as contas fraudulentas?

Etapa 2 do fluxo da pesquisa (ver docs/plano-de-testes-estatisticos.md). Roda
nas **sementes de validação** (1001, 1002...), as mesmas da otimização dos
hiperparâmetros, para não tocar nas redes de teste (sementes 1 a 10).

Para cada cenário e semente:

* **fraude × legítima** (2 grupos): Mann-Whitney com delta de Cliff e Holm
  (`stats.compare_groups`);
* **entre os 6 papéis** (normal, comércio, vítima, laranja, intermediário,
  coletor): Kruskal-Wallis com ε² e Holm (`stats.kruskal_groups`) e, nos
  atributos com efeito pelo menos médio na primeira semente, o teste de Dunn
  para saber que pares de papéis diferem (`stats.dunn_posthoc`);
* **variáveis categóricas × fraude** (conta de empresa, conta nova, recebeu Pix
  de madrugada): qui-quadrado, Fisher exato e razão de chances
  (`stats.contingency_test`).

O resumo diz, para cada atributo, o efeito médio entre as sementes e em quantas
delas o teste deu significativo depois do Holm: um efeito que só aparece numa
semente não é um efeito.

Saídas em reports/02_exploracao/results/:
    inferencia_fraude.csv        (cenário, atributo): delta de Cliff médio, IC 95% e sementes significativas
    inferencia_papeis.csv        (cenário, atributo): ε² médio, IC 95%, sementes significativas e papel de maior mediana
    inferencia_dunn.csv          (cenário, atributo, par de papéis): z, p de Holm, na primeira semente
    inferencia_categoricas.csv   (cenário, variável): V de Cramér, razão de chances e sementes significativas
    inferencia_execucoes.csv     uma linha por (cenário, semente, teste, atributo): tudo o que foi calculado
    inferencia_meta.json         como o resultado foi gerado
e a figura reports/02_exploracao/figures/inferencia_papeis.png (ε² atributo × cenário).

Uso:
    python scripts/02_exploracao/inferencia_atributos.py
    python scripts/02_exploracao/inferencia_atributos.py --cenarios calibrado --sementes 5

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['realista', 'negativos_dificeis', 'cal…` |  |
| `--sementes` | `5` | sementes de validação: 1001, 1002, ... |
| `--saida` | `'reports/02_exploracao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def categorical_variables(accounts: pd.DataFrame, tx: pd.DataFrame) -> dict[str, pd.Series]`: Variáveis sim/não de cada conta, para cruzar com o gabarito.
- `def summarize(runs: pd.DataFrame) -> pd.DataFrame`: Por (cenário, atributo): efeito médio, IC 95% t entre as sementes e em quantas o p de Holm < alfa.
- `def _plot_roles(summary: pd.DataFrame, names: list, n: int, path: Path) -> None`: Matriz atributo × cenário do ε² médio do Kruskal-Wallis entre os papéis.

## [`visualizar_rede.py`](../../scripts/02_exploracao/visualizar_rede.py)

Gera o explorador interativo da rede inteira (HTML).

A página mostra todas as contas e relações, com busca, filtros por papel, cor
por papel / risco / grupo (Louvain), clique para ver a vizinhança e uma linha
do tempo dia a dia. O risco vem de **todos os modelos**, e um seletor na página
escolhe qual deles pinta as contas, com a lista separada em não
supervisionados e supervisionados (os que usam os rótulos, com validação
cruzada: cada conta recebe o escore de um modelo treinado sem ela). Em cada
grupo, os modelos vêm do mais eficaz ao menos, pela average precision (AP)
que tiveram nesta rede, mostrada ao lado do nome. As redes
neurais para grafos (DOMINANT e GraphSAGE) entram só se o extra `gnn`
estiver instalado. Com `--modelo`, a página usa um detector só, como antes.

Uso:
    python scripts/02_exploracao/visualizar_rede.py
    python scripts/02_exploracao/visualizar_rede.py --modelo isolation_forest --atributos grafo_avancado --saida reports/estudos/rede_if.html

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--dados` | `'data/synthetic'` |  |
| `--modelo` | — | usa só este detector (padrão: todos os modelos, com seletor na página) |
| `--atributos` | `'completo'` |  |
| `--seed` | `42` | semente dos modelos supervisionados e das GNN |
| `--saida` | `'reports/estudos/rede_completa.html'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
