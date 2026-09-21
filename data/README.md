# Dados

Os arquivos de dados **não são versionados** (ver `.gitignore`): podem ser recriados a
qualquer momento pelos scripts, a partir da configuração e da semente.

| Pasta        | Conteúdo                                               | Como gerar                                      |
|--------------|--------------------------------------------------------|-------------------------------------------------|
| `synthetic/` | Dataset sintético (`accounts.csv`, `transactions.csv`) | `python scripts/gerar_dataset.py`               |
| `processed/` | Atributos por conta (`features.csv`)                   | `python scripts/rodar_experimento.py`           |
| `bcb/`       | Estatísticas públicas do PIX (Banco Central)           | `python scripts/baixar_dados_bcb.py <recurso> <AAAAMM>` |
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
| `scenario`  | `normal`, `falso_suporte`, `clonagem_whatsapp`, `repasse_laranja` ou `lavagem_em_cadeia` |

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
* as contas fraudulentas também fazem alguns Pix comuns (camuflagem).

### Limitações conhecidas (importantes para a análise)

O gerador **embute** hipóteses sobre como as fraudes acontecem, e um detector que as
encontra está, em parte, apenas redescobrindo essas hipóteses. Ao interpretar os
resultados, lembre-se de que, na versão atual:

* os golpes acontecem em **qualquer horário com a mesma probabilidade**, enquanto os Pix
  legítimos seguem o perfil horário `HOUR_WEIGHTS`. Por isso `night_ratio` é um sinal
  forte **por construção**;
* 70% das contas fraudulentas são recém-abertas (`account_age_days` < 60);
* comércios só recebem (não pagam fornecedores nem salários);
* a taxa de fraude (~2% das contas) é muito maior que a real. Segundo o BCB, há cerca de
  5 contestações aceitas a cada 100 mil Pix. A taxa foi inflada de propósito para haver
  exemplos suficientes; vale testar cenários mais realistas via `configs/experimento.yaml`.

Validar e calibrar essas escolhas faz parte da etapa de análise exploratória.

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
