# Dados

Os arquivos de dados **não são versionados** (ver `.gitignore`): podem ser recriados a
qualquer momento pelos scripts, a partir da configuração e da semente.

| Pasta        | Conteúdo                                               | Como gerar                                      |
|--------------|--------------------------------------------------------|-------------------------------------------------|
| `synthetic/` | Dataset sintético (`accounts.csv`, `transactions.csv`, `dataset_meta.json` com a semente) | `python scripts/gerar_dataset.py` (semente sorteada; `--seed N` reproduz) |
| `processed/` | Atributos por conta (`features.csv`)                   | `python scripts/rodar_experimento.py`           |
| `bcb/`       | Estatísticas públicas do PIX (Banco Central)           | `python scripts/baixar_dados_bcb.py <recurso> <AAAAMM>` |
| `external/`  | Datasets públicos convertidos para o formato do projeto | `python scripts/importar_dataset.py <fonte> <arquivo>` |
| `raw/`       | Qualquer outro dado bruto obtido manualmente           | anotar a origem e a data de acesso aqui          |

## Dataset sintético

### `accounts.csv`: uma linha por conta

| Coluna             | Descrição                                                        |
|--------------------|------------------------------------------------------------------|
| `account_id`       | identificador (embaralhado, não revela o papel da conta)          |
| `account_type`     | `PF` ou `PJ`                                                     |
| `account_age_days` | idade da conta em dias                                            |
| `role`             | `normal`, `comercio`, `laranja`, `intermediario` ou `coletor`     |
| `is_fraud`         | rótulo verdadeiro: a conta pertence a uma quadrilha               |
| `is_victim`        | a conta pagou algum golpe                                         |

### `transactions.csv`: uma linha por Pix

| Coluna      | Descrição                                                        |
|-------------|------------------------------------------------------------------|
| `tx_id`     | identificador da transação                                       |
| `timestamp` | data e hora                                                      |
| `sender`    | conta pagadora                                                   |
| `receiver`  | conta recebedora                                                 |
| `amount`    | valor em R$                                                      |
| `is_fraud`  | rótulo verdadeiro da transação                                    |
| `scenario`  | `normal`, `falso_suporte`, `clonagem_whatsapp`, `repasse_laranja`, `lavagem_em_cadeia` ou `saida_coletor` |

`role`, `is_fraud`, `is_victim` e `scenario` são **rótulos**: servem só para avaliar os
modelos e nunca devem entrar como atributo de entrada.

### Como uma quadrilha é simulada

```
vítimas ──golpe──▶ contas laranja ──repasse──▶ [intermediário ▶ intermediário ▶ ...] ──▶ coletora
```

* **falso suporte**: uma vítima faz de 1 a 3 Pix seguidos para uma laranja;
* **clonagem de WhatsApp**: de 2 a 4 contatos (mesma comunidade) de uma pessoa clonada
  pagam a mesma laranja em poucos minutos;
* cada valor recebido é repassado em até ~30 min, com uma pequena comissão retida a cada
  salto, direto para a coletora (`repasse_laranja`) ou por uma cadeia de intermediários
  (`lavagem_em_cadeia`);
* com `collector_cashout` > 0, a coletora esvazia ~90% do que recebeu em vários Pix para
  pessoas e comércios (`saida_coletor`); no padrão (0) ela só recebe;
* as contas fraudulentas também fazem alguns Pix comuns (camuflagem).

### Limitações conhecidas (importantes para a análise)

O gerador **embute** hipóteses sobre como as fraudes acontecem, e um detector que as
encontra está, em parte, apenas redescobrindo essas hipóteses. Ao interpretar os
resultados, lembre-se de que, com a configuração padrão:

| Limitação | Efeito | Como desligar (`simulacao`) |
|-----------|--------|-----------------------------|
| os golpes acontecem em **qualquer horário com a mesma probabilidade**, enquanto os Pix legítimos seguem o perfil horário `HOUR_WEIGHTS` | `night_ratio` é um sinal forte **por construção** | `fraud_hours: comercial` |
| 70% das contas fraudulentas são recém-abertas (`account_age_days` < 60) | a idade da conta denuncia a fraude | `p_new_fraud_account: 0.0` |
| toda pessoa legítima é razoavelmente ativa (~18 Pix enviados por mês) | qualquer conta com poucos Pix já parece anômala (exercício 4 de `estudos/04_padroes_de_fraude.ipynb`) | `quiet_fraction: 0.3` |
| a taxa de fraude (~2% das contas) é muito maior que a real: segundo o BCB, há cerca de 5 contestações aceitas a cada 100 mil Pix | métricas mais altas do que num cenário real | menos quadrilhas (`n_rings`) ou mais pessoas (`n_people`) |
| as laranjas repassam em ~30 min | o tempo de permanência (`dwell_time_min`) é um sinal forte | `forward_delay_min: 360` |
| comércios só recebem (não pagam fornecedores nem salários) | comércios nunca parecem contas de passagem | ainda não configurável |

A taxa de fraude foi inflada de propósito, para haver exemplos suficientes. Os cenários
de [`configs/cenarios.yaml`](../configs/cenarios.yaml) combinam esses parâmetros, do mais
fácil ao mais difícil, e `python scripts/avaliar_cenarios.py` mede o quanto cada
resultado depende deles (ver [`docs/resultados.md`](../docs/resultados.md)). Validar e
calibrar essas escolhas faz parte da etapa de análise exploratória.

## Dados públicos do Banco Central

A API de dados abertos do PIX (`pixfraud.bcb`) oferece estatísticas **agregadas** (não há
transações individuais, então elas não formam um grafo). Recursos disponíveis:

| Apelido      | Recurso da API               | Uso sugerido                                                   |
|--------------|------------------------------|----------------------------------------------------------------|
| `transacoes` | `EstatisticasTransacoesPix`  | valor e quantidade por PF/PJ, região, faixa etária e natureza (P2P, P2B...): calibrar o gerador |
| `fraudes`    | `EstatisticasFraudesPix`     | contestações, devoluções pelo MED, bloqueios cautelares, usuários e chaves marcados por fraude |
| `municipios` | `TransacoesPixPorMunicipio`  | volume por município                                            |
| `cnae`       | `CnaePorteRecebedor`         | recebedores PJ por setor e porte                                |
| `chaves`     | `ChavesPix`                  | chaves cadastradas por instituição e tipo                       |

Sem filtro, `transacoes` tem mais de 50 MB. Use `--filtro "AnoMes eq 202506"` para baixar
um único mês.

### Problema conhecido: 504 ao baixar `transacoes`

`python scripts/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506"` pode
falhar com `HTTP Error 504: Gateway Time-out` (visto em 26/09/2026). O `fraudes` baixa
normalmente, então não é conexão nem código.

- **Causa:** o gateway da API de dados abertos do BCB (olinda.bcb.gov.br) desiste antes de
  o servidor montar a resposta. O recurso `EstatisticasTransacoesPix` é grande, e mesmo com
  `--filtro` o servidor às vezes não termina a tempo. O timeout do nosso lado (300 s em
  `src/pixfraud/bcb.py`) não chega a ser atingido.
- **Contorno:** o script já tenta de novo sozinho (`--tentativas`, padrão 3, com espera
  crescente a partir de `--espera` segundos). Se ainda falhar, tente mais tarde ou filtre
  mais no `--filtro` (conferir antes os nomes dos campos do recurso). Em 26/09/2026 falhou
  mesmo com 3 tentativas e com `--top 100`, então o gargalo é o servidor montar o filtro.
  Nova tentativa no mesmo dia, perto do meio-dia, também deu 504.
- **Impacto:** nenhum resultado em `reports/` depende desse download. Ele serve só para
  calibrar o gerador sintético, que por enquanto **não está calibrado** com esses dados.

- [x] Tornar o download robusto: novas tentativas com espera entre elas no `fetch` e as
  opções `--top`, `--tentativas` e `--espera` no script (a API não aceita `$skip`).
- [ ] Calibrar o gerador com as estatísticas de transações do BCB quando o download funcionar.

## Datasets públicos externos

Para não avaliar os detectores só nos padrões que nós mesmos injetamos, `pixfraud.external`
converte dois datasets públicos para o formato acima (`accounts.csv` e `transactions.csv`).
Os arquivos originais ficam no Kaggle. Anote aqui a versão e a data de acesso.

| Fonte | O que é | Arquivos | Observações |
|-------|---------|----------|-------------|
| **AMLworld** (IBM; Altman et al., 2023) | transações bancárias sintéticas com rótulo de lavagem e padrões em grafo (fan-in, fan-out, ciclos, cadeias...) | `HI-Small_Trans.csv`, `HI-Small_Patterns.txt`, `LI-Small_*` etc. | grandes: recorte com `--dias` ou `--linhas`. Só pagamentos em dólar, por padrão (`--moeda`) |
| **PaySim** (Lopez-Rojas et al., 2016) | simulação de dinheiro móvel | `PS_20174392719_1491204439457_log.csv` | quase toda conta de origem aparece uma única vez, então a estrutura em grafo é fraca; serve de contraste |

### Baixar pela API do Kaggle

1. Em kaggle.com: foto do perfil → *Settings* → *API* → *Create New Token*. Salve o
   `kaggle.json` em `C:\Users\<usuário>\.kaggle\kaggle.json` (Linux/macOS: `~/.kaggle/`).
   O token é pessoal: **nunca** o coloque dentro do repositório.
2. Com o ambiente ativado:

```powershell
pip install kaggle
kaggle datasets files ealtman2019/ibm-transactions-for-anti-money-laundering-aml
kaggle datasets download ealtman2019/ibm-transactions-for-anti-money-laundering-aml -f HI-Small_Trans.csv -p data/raw --unzip
kaggle datasets download ealtman2019/ibm-transactions-for-anti-money-laundering-aml -f HI-Small_Patterns.txt -p data/raw --unzip
```

### Importar e avaliar

```powershell
# todas as formas de pagamento
python scripts/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --padroes data/raw/HI-Small_Patterns.txt --saida data/external/amlworld
# só transferências eletrônicas (ACH e Wire), as mais parecidas com o Pix
python scripts/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --padroes data/raw/HI-Small_Patterns.txt --formatos ACH Wire --saida data/external/amlworld_pix

# mesma configuração do sintético, janelas de 3 dias como repetições, recall por tipologia
python scripts/avaliar_externo.py --dados data/external/amlworld_pix --saida reports/amlworld
```

`--padroes` grava `patterns.csv` (conta → tipologia de lavagem), usado para medir quais
formatos cada abordagem encontra. Para um teste rápido, use `--max-janelas 1` no
`avaliar_externo.py`, ou `--dias` na importação.

**Tamanho das janelas e memória.** Uma janela de 3 dias da versão "só transferências" tem
~79 mil contas e leva ~20 min; a mesma janela com todas as formas de pagamento tem ~160
mil. O que pesa é o rótulo binário do DBSCAN, cuja memória cresce com o quadrado do nº de
contas; o parâmetro `modelos.dbscan.max_exact` (ver
[`configs/parametros-dos-experimentos.md`](../configs/parametros-dos-experimentos.md)) define até onde vale a pena gastar essa
memória. Para janelas menores, use `--dias-janela 1`.

Nos dois datasets não existe idade da conta: `account_age_days` fica 0 e deixa de informar.
Os papéis também não existem: as contas envolvidas em fraude/lavagem recebem `role = suspeita`.
