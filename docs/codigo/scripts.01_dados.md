---
tags: [codigo]
---

# `scripts/01_dados/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Etapa 1: gerar, importar e baixar dados, auditar o gabarito, validar o realismo. Guia da pasta: [README.md](../../scripts/01_dados/README.md) · [mapa do código](mapa-do-codigo.md)

## [`auditar_papeis.py`](../../scripts/01_dados/auditar_papeis.py)

O papel de cada conta corresponde ao que ela fez? (reunião de 01/10)

Confere, conta por conta, se o papel gravado pelo gerador (comércio, laranja,
intermediário, coletor, vítima, normal) bate com as transações da conta, usando
as regras de `pixfraud.simulation.audit_roles`: o comércio só paga salário e
fornecedor, a laranja recebe golpe e repassa, a coletora recebe repasses e é a
única que tira o dinheiro, e assim por diante.

Roda no dataset gravado (`--dados`) e em `--sementes` sementes de cada
cenário, incluindo o `aleatorio` (estrutura sorteada). Também resume o
comportamento típico de cada papel (graus, volume, repasse), para mostrar o que
cada um faz na prática.

Saídas em reports/01_dados/results/:
    auditoria_papeis.csv          uma linha por violação (vazio se tudo confere)
    auditoria_resumo.csv          uma linha por (cenário, semente): contas por papel e violações
    auditoria_perfis.csv          mediana de graus, volumes e repasse por papel e cenário
    auditoria_meta.json           como o resultado foi gerado

Uso:
    python scripts/01_dados/auditar_papeis.py
    python scripts/01_dados/auditar_papeis.py --cenarios base aleatorio --sementes 50

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `None` | padrão: todos os de --arquivo-cenarios |
| `--sementes` | `20` |  |
| `--dados` | `'data/synthetic'` |  |
| `--saida` | `'reports/01_dados'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _profile(tx: pd.DataFrame, roles: pd.Series) -> pd.DataFrame`: Mediana, por papel, do que as contas fazem: quem paga, quem recebe e quanto repassam.

## [`baixar_dados_bcb.py`](../../scripts/01_dados/baixar_dados_bcb.py)

Baixa estatísticas do PIX da API de dados abertos do Banco Central.

Exemplos:
    python scripts/01_dados/baixar_dados_bcb.py fraudes 202506
    python scripts/01_dados/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506"
    python scripts/01_dados/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506" --top 1000 --tentativas 5

Erros passageiros do servidor (como o 504 frequente em `transacoes`) são tentados de
novo com espera crescente entre as tentativas.

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `recurso` | obrigatória |  |
| `database` | obrigatória | parâmetro obrigatório da API, ex.: 202506 |
| `--filtro` | — | expressão OData $filter, ex.: "AnoMes eq 202506" |
| `--top` | — | limita o nº de linhas (a API não pagina) |
| `--tentativas` | `3` | tentativas em 502/503/504 ou falha de conexão |
| `--espera` | `30` | segundos antes da 2ª tentativa (dobra a cada nova) |
| `--saida` | `'data/bcb'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`gerar_dataset.py`](../../scripts/01_dados/gerar_dataset.py)

Gera o dataset sintético de transações PIX.

Cada execução sorteia uma semente nova, então o dataset muda a cada vez. A semente usada
é impressa e gravada em `dataset_meta.json` na pasta de saída; `--seed N` refaz
exatamente aquele dataset. A `seed` de `simulacao` no YAML não é usada aqui.

Uso:
    python scripts/01_dados/gerar_dataset.py                  # dataset novo, semente sorteada
    python scripts/01_dados/gerar_dataset.py --seed 42        # o dataset dos resultados em reports/
    python scripts/01_dados/gerar_dataset.py --aleatorio      # sorteia nº de quadrilhas, laranjas, vítimas, comércios
    python scripts/01_dados/gerar_dataset.py --config configs/experimento.yaml --saida data/synthetic

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--saida` | `'data/synthetic'` |  |
| `--seed` | `None` | semente do gerador; sem ela, sorteia uma nova a cada execução |
| `--aleatorio` | desligada | sorteia a estrutura (estrutura_aleatoria): os valores do YAML viram médias |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`importar_dataset.py`](../../scripts/01_dados/importar_dataset.py)

Converte um dataset público (AMLworld ou PaySim) para o formato do projeto.

Depois de importar, o mesmo pipeline roda sobre os dados externos:

    python scripts/01_dados/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --dias 3
    python scripts/03_modelos/rodar_experimento.py --dados data/external/amlworld --saida reports/amlworld
    python scripts/02_exploracao/visualizar_rede.py --dados data/external/amlworld --saida reports/amlworld/rede.html

Para a avaliação por janelas e por tipologia (scripts/04_avaliacao/avaliar_externo.py), importe
também o arquivo de padrões; --formatos ACH Wire mantém só as transferências
parecidas com o Pix:

    python scripts/01_dados/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv \
        --padroes data/raw/HI-Small_Patterns.txt --formatos ACH Wire --saida data/external/amlworld_pix

Os arquivos originais vêm do Kaggle (ver data/README.md).

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `fonte` | obrigatória |  |
| `arquivo` | obrigatória | CSV original baixado do Kaggle |
| `--saida` | — | pasta de saída (padrão: data/external/<fonte>) |
| `--linhas` | — | lê só as primeiras N linhas do arquivo |
| `--dias` | — | AMLworld: mantém só os primeiros N dias |
| `--moeda` | `'US Dollar'` | AMLworld: moeda mantida ('todas' para não filtrar) |
| `--formatos` | — | AMLworld: formas de pagamento mantidas (ex.: ACH Wire); padrão: todas |
| `--padroes` | — | AMLworld: arquivo *_Patterns.txt, salvo como patterns.csv |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).

## [`validar_realismo.py`](../../scripts/01_dados/validar_realismo.py)

O dataset sintético parece o Pix real? Validação do gerador contra o Banco Central.

Duas perguntas, antes de qualquer modelo (etapa 1 do fluxo da pesquisa, ver
docs/plano-de-testes-estatisticos.md):

* **Os números batem com o BCB?** Para cada estatística que o BCB publica
  agregada (fração de Pix de pessoa física que vai para empresas, ticket médio
  P2P e P2B, golpes a cada 100 mil Pix, valor médio de um golpe), calcula a
  média do gerador em `--sementes` redes de cada cenário, com IC 95% t, e
  compara com o valor do BCB: o BCB cai no IC? o erro relativo fica dentro de
  `--tolerancia`? Como o BCB só publica agregados, não há distribuição para
  um teste de aderência (KS); o IC entre sementes é o teste possível.
* **A estrutura é diferente do acaso?** Reciprocidade e transitividade da rede
  contra grafos aleatórios com os mesmos graus (`stats.null_model_test`):
  se a rede sintética tem mais ciclos e triângulos que o acaso, os atributos de
  grafo têm o que medir.

A taxa de golpes do gerador é maior que a real de propósito (para haver
exemplos de fraude); a tabela mostra o quanto.

Lê data/bcb/transacoes_*.csv e fraudes_*.csv (baixados por baixar_dados_bcb.py).

Saídas em reports/01_dados/results/:
    realismo_execucoes.csv   uma linha por (cenário, semente): as estatísticas do gerador
    realismo_comparacao.csv  uma linha por (cenário, estatística): BCB, média, IC 95%, erro relativo
    realismo_estrutura.csv   uma linha por (cenário, estatística): observado, nulo, z e p empírico
    realismo_meta.json       como o resultado foi gerado

Uso:
    python scripts/01_dados/validar_realismo.py
    python scripts/01_dados/validar_realismo.py --cenarios calibrado aleatorio --sementes 20

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['calibrado', 'aleatorio']` |  |
| `--sementes` | `10` |  |
| `--tolerancia` | `0.2` | erro relativo aceito (0,2 = 20%) |
| `--amostras-nulas` | `50` | grafos aleatórios do modelo nulo |
| `--bcb` | `'data/bcb'` |  |
| `--saida` | `'reports/01_dados'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def bcb_reference(folder: Path) -> dict[str, float]`: As mesmas estatísticas, nos dados abertos do Pix (só agregados, sem dado pessoal).
- `def synthetic_statistics(accounts: pd.DataFrame, tx: pd.DataFrame) -> dict[str, float]`: As estatísticas do BCB calculadas numa rede sintética.
- `def compare_with_reference(runs: pd.DataFrame, reference: dict[str, float], tolerance: float) -> pd.DataFrame`: Para cada (cenário, estatística): média do gerador, IC 95% t, valor do BCB e erro relativo.
