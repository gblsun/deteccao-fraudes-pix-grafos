---
tags: [codigo]
---

# `pixfraud.simulation`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/simulation.py`](../../src/pixfraud/simulation.py) · [mapa do código](mapa-do-codigo.md)

Gerador de um dataset sintético de transações PIX com cenários de fraude.

A ideia não é reproduzir o PIX real, e sim produzir uma rede de transações com
propriedades plausíveis (valores com cauda pesada, sazonalidade ao longo do
dia, círculos de contatos e comércios que concentram pagamentos) na qual são
injetados padrões de fraude conhecidos:

* `falso_suporte`: a vítima faz uma ou mais transferências seguidas para uma
  conta laranja, orientada por um falso atendente do banco;
* `clonagem_whatsapp`: contatos de uma pessoa cujo WhatsApp foi clonado pagam
  a mesma conta laranja em um curto intervalo de tempo;
* `repasse_laranja`: a conta laranja repassa rapidamente o valor recebido
  para a conta coletora da quadrilha;
* `lavagem_em_cadeia`: o repasse passa por uma cadeia de contas
  intermediárias antes de chegar à coletora;
* `espalha_junta`, `ciclo` e `bipartido`: outras formas de lavagem,
  inspiradas nas tipologias do AMLworld (ver `laundering_typologies`);
* `saque`: a coletora tira o dinheiro para uma corretora (`collector_cashout`);
* `saida_coletor`: a coletora esvazia o que recebeu em vários Pix para
  pessoas e comércios (`collector_payouts`).

Os parâmetros ficam em `configs/experimento.yaml` e a semente torna o dataset
reprodutível. Os valores padrão são ilustrativos; o cenário `calibrado` de
`configs/cenarios.yaml` usa os números do BCB (ver `pixfraud.bcb`).

Por padrão o gerador embute sinais "fáceis" (golpes a qualquer hora, contas
fraudulentas recém-abertas, pessoas sempre ativas, só a fraude repassa
dinheiro). Os parâmetros de realismo desligam esses atalhos e **não gastam
nenhum sorteio quando estão desligados**: com os valores padrão, a mesma
semente produz exatamente o mesmo dataset de antes de eles existirem.

Com `estrutura_aleatoria`, as contagens também são sorteadas a cada semente
(`draw_structure`): nº de quadrilhas, laranjas, vítimas e intermediários de
cada uma, como cada coletora tira o dinheiro, nº de comércios e quanto eles
pagam de salários e fornecedores. `audit_roles` confere, conta por conta, que
o papel gravado em `accounts` corresponde ao que a conta fez nas transações.

## Classes e funções

### `SimulationConfig` (classe)

```python
class SimulationConfig
```

Parâmetros da simulação (descritos em `configs/experimento.yaml`).

### `load_config` (função)

```python
def load_config(path: str | Path) -> SimulationConfig
```

Lê a seção `simulacao` do arquivo YAML de experimento.

### `with_overrides` (função)

```python
def with_overrides(cfg: SimulationConfig, overrides: dict) -> SimulationConfig
```

Cópia de `cfg` com alguns parâmetros trocados (usado pelos cenários de `configs/cenarios.yaml`).

### `draw_structure` (função)

```python
def draw_structure(cfg: SimulationConfig) -> tuple[SimulationConfig, list[SimulationConfig]]
```

A configuração geral e a de cada quadrilha.

Sem `estrutura_aleatoria`, é a própria `cfg` repetida `n_rings` vezes
(nenhum sorteio, o dataset não muda). Com ela, um gerador próprio
(`default_rng([seed, 1])`, separado do que gera as transações) sorteia:

* nº de quadrilhas: `1 + Poisson(n_rings - 1)`, então `n_rings` vira a média;
* por quadrilha: laranjas (`1 +` binomial negativa com média
  `mules_per_ring - 1`), vítimas (binomial negativa com média
  `victims_per_ring`), intermediários (Poisson com média `chain_length`,
  de 1 a 6), a fração de laranjas recrutadas entre pessoas com histórico
  (Beta(2, 3), média 40%) e o que a coletora faz (`COLLECTOR_EXITS`);
* comércios: `MERCHANT_SHARE` das pessoas, que pagam salários e
  fornecedores (se a `cfg` não fixou esses valores), em vez de só receber.

O papel de cada conta já é sorteado em `generate_dataset` (os ids são
embaralhados); aqui muda o tamanho de cada papel.

### `structure_summary` (função)

```python
def structure_summary(cfg: SimulationConfig) -> dict
```

O que `draw_structure` sorteou, para gravar junto com o dataset (`dataset_meta.json`).

### `generate_dataset` (função)

```python
def generate_dataset(cfg: SimulationConfig) -> tuple[pd.DataFrame, pd.DataFrame]
```

Gera as tabelas `accounts` (uma linha por conta) e `transactions`.

### `audit_roles` (função)

```python
def audit_roles(accounts: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame
```

Contas cujo comportamento nas transações não bate com o papel gravado em `accounts`.

Devolve uma linha por violação (`account_id`, `role`, `regra`); vazia
quando todo papel confere. As regras dizem o que cada papel **faz**:

* `comercio`: é PJ; só paga salário ou fornecedor; não aplica nem repassa golpe;
* `laranja`: recebe golpe de vítimas e repassa para a quadrilha;
* `intermediario`: recebe repasse da quadrilha e repassa adiante, sem
  receber golpe direto de vítima;
* `coletor`: recebe repasse da quadrilha, nunca golpe direto, e só ele
  tira o dinheiro (saque ou saída para pessoas e comércios);
* vítima (`is_victim`): fez ao menos um Pix de golpe, e não é fraudadora;
* `normal`: não enviou golpe nem repassou dinheiro de quadrilha.

Os repasses de quadrilha só podem ir de uma conta fraudulenta para outra, e
todo golpe sai de uma vítima e chega a uma laranja. Receber dinheiro que
saiu da coletora (saque ou `saida_coletor`) não é violação: o comércio ou
a pessoa do outro lado não sabe de onde ele veio.

### `save_dataset` (função)

```python
def save_dataset(accounts: pd.DataFrame, transactions: pd.DataFrame, out_dir: str | Path) -> None
```

Grava `accounts.csv` e `transactions.csv` em `out_dir` (criada se não existir).

### `load_dataset` (função)

```python
def load_dataset(data_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]
```

Lê as tabelas gravadas por `save_dataset` (vale também para os datasets externos).

## Funções internas

Usadas só dentro do módulo (o nome começa com `_`).

- `def _negative_binomial(rng, mean: float, dispersion: float=DISPERSION) -> int`: Contagem com média `mean` e cauda longa (variância `mean + mean²/dispersion`).
- `def _chain_slots(cfg: SimulationConfig) -> int`: Quantas posições de intermediário a quadrilha tem, conforme as tipologias de lavagem.
- `def _day_weights(cfg: SimulationConfig) -> np.ndarray | None`: Probabilidade de cada dia do período (`None` no calendário uniforme).
- `def _random_seconds(rng: np.random.Generator, n: int, n_days: int, day_p: np.ndarray | None=None) -> np.ndarray`: Instantes (em segundos desde o início) seguindo o perfil horário `HOUR_WEIGHTS`.
- `def _after_activity(t: float, delay: float) -> float`: Instante em que `delay` segundos de atividade terão passado a partir de `t`.
- `def _merchant_popularity(n: int) -> np.ndarray`: Popularidade tipo Zipf: poucos comércios concentram a maior parte dos pagamentos.
- `def _amounts(rng, cfg, to_merchant: np.ndarray) -> np.ndarray`: Valores dos Pix comuns: P2P e P2B com a mesma lognormal, a menos que o P2B tenha a sua.
- `def _or(value, default)`: `value`, ou `default` se `value` for `None`.
- `def _normal_transactions(rng, cfg, people, merchants, community, day_p=None) -> pd.DataFrame`: Pagamentos a comércios e transferências P2P, em geral dentro do círculo de contatos.
- `def _fraud_ring(rng, cfg, people, merchants, community, fraud_pool, recruited, day_p=None, avoid=frozenset())`: Simula uma quadrilha: vítimas -> contas laranja -> [intermediários] -> coletora [-> saque].
- `def _recruit(rng, people, recruited: set, avoid=frozenset()) -> str`: Uma pessoa que ainda não é laranja: a conta cedida ou alugada para a quadrilha.
- `def _pick_person(rng, people, excluded: set) -> str`: Sorteia uma pessoa que não esteja em `excluded`.
- `def _launder(rng, cfg, t, amount, mule, chain, collector, typology='cadeia', exchange=None)`: Leva o valor da laranja até a coletora, seguindo a tipologia da quadrilha.
- `def _hops(rng, cfg, t, amount, path, scenario)`: Repassa o valor ao longo de `path`, retendo uma pequena comissão a cada salto.
- `def _later(cfg, t, delay)`: Instante `delay` depois de `t`, empurrado para o horário de atividade se for o caso.
- `def _collector_payouts(rng, cfg, ring_tx, collector, people, merchants) -> pd.DataFrame`: A coletora esvazia o que recebeu: vários Pix de saída para pessoas e comércios.
- `def _camouflage_transactions(rng, cfg, accounts, people, merchants, day_p=None) -> pd.DataFrame`: Movimentações comuns das contas criadas para a fraude, para que não sejam triviais de isolar.
- `def _has_look_alikes(cfg) -> bool`: O cenário tem contas legítimas parecidas com fraude (salários, vaquinhas, repasses)?
- `def _look_alike_transactions(rng, cfg, people, merchants, community, day_p=None) -> pd.DataFrame`: Pix legítimos que se parecem com partes de uma quadrilha ("negativos difíceis").
- `def _salary_days(cfg) -> list[int]`: Dias do período (a partir de 0) em que cai o `salary_business_day`-ésimo dia útil do mês.
- `def _contestations(rng, cfg, tx: pd.DataFrame) -> pd.DataFrame`: Coluna `contestado_em`: quando a vítima contestou o golpe (vazia nos demais Pix).
- `def _accounts_table(rng, people, merchants, roles, victims, p_new_fraud_account) -> pd.DataFrame`: Tabela de contas: tipo, idade (contas de fraude tendem a ser novas), papel e se é vítima.

## Quem usa este módulo

- [`app/explorador.py`](app.md)
- [`pixfraud.experiment`](pixfraud.experiment.md)
- [`pixfraud.exploration`](pixfraud.exploration.md)
- [`pixfraud.patterns`](pixfraud.patterns.md)
- [`scripts/01_dados/auditar_papeis.py`](scripts.01_dados.md)
- [`scripts/01_dados/gerar_dataset.py`](scripts.01_dados.md)
- [`scripts/01_dados/importar_dataset.py`](scripts.01_dados.md)
- [`scripts/01_dados/validar_realismo.py`](scripts.01_dados.md)
- [`scripts/02_exploracao/analisar_tipo_de_rede.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/inferencia_atributos.py`](scripts.02_exploracao.md)
- [`scripts/02_exploracao/visualizar_rede.py`](scripts.02_exploracao.md)
- [`scripts/03_modelos/avaliar_modelos.py`](scripts.03_modelos.md)
- [`scripts/03_modelos/otimizar_hiperparametros.py`](scripts.03_modelos.md)
- [`scripts/03_modelos/rodar_experimento.py`](scripts.03_modelos.md)
- [`scripts/04_avaliacao/avaliar_atributos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_cenarios.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_deteccao_online.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_externo.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_fraudar.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_gnn_rotulos.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_propagacao.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_robustez.py`](scripts.04_avaliacao.md)
- [`scripts/04_avaliacao/avaliar_sementes.py`](scripts.04_avaliacao.md)
- [`scripts/05_interpretacao/investigar_falsos_positivos.py`](scripts.05_interpretacao.md)
- [`scripts/ferramentas/gerar_ilustracoes.py`](scripts.ferramentas.md)
- [`scripts/ferramentas/ilustrar_testes.py`](scripts.ferramentas.md)
- [`tests/test_app.py`](testes.md)
- [`tests/test_experiment.py`](testes.md)
- [`tests/test_explorer.py`](testes.md)
- [`tests/test_flow.py`](testes.md)
- [`tests/test_gnn_direcionada.py`](testes.md)
- [`tests/test_graph_models.py`](testes.md)
- [`tests/test_network.py`](testes.md)
- [`tests/test_online.py`](testes.md)
- [`tests/test_pipeline.py`](testes.md)
- [`tests/test_scripts.py`](testes.md)
- [`tests/test_simulation.py`](testes.md)
- [`tests/test_tuning.py`](testes.md)
