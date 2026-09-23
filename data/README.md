# Dados

Os arquivos de dados **não são versionados** (ver `.gitignore`): podem ser recriados a
qualquer momento pelos scripts, a partir da configuração e da semente.

| Pasta        | Conteúdo                                               | Como gerar                                      |
|--------------|--------------------------------------------------------|-------------------------------------------------|
| `synthetic/` | Dataset sintético (`accounts.csv`, `transactions.csv`) | `python scripts/gerar_dataset.py`               |
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
| `scenario`  | o que gerou o Pix (ver abaixo)                                    |
| `contestado_em` | quando a vítima contestou o golpe; **só existe** com `p_contested > 0`, e fica vazia nos demais Pix |

Valores de `scenario`:

* legítimos: `normal` e, com os negativos difíceis ligados, `salario`, `fornecedor`,
  `vaquinha` e `repasse_salario`;
* golpes: `falso_suporte` e `clonagem_whatsapp`;
* lavagem: `repasse_laranja`, `lavagem_em_cadeia`, `espalha_junta`, `ciclo` e `bipartido`;
* `saque`: a coletora tira o dinheiro para uma corretora.

`role`, `is_fraud`, `is_victim`, `scenario` e `contestado_em` são **rótulos**: servem só
para avaliar os modelos e nunca devem entrar como atributo de entrada. A exceção é
`contestado_em` na propagação de risco, que simula o que o banco fica sabendo pelo MED, e
só a partir do instante da contestação.

### Como uma quadrilha é simulada

```
vítimas ──golpe──▶ contas laranja ──repasse──▶ [intermediário ▶ intermediário ▶ ...] ──▶ coletora ──▶ [saque]
```

* **falso suporte**: uma vítima faz de 1 a 3 Pix seguidos para uma laranja;
* **clonagem de WhatsApp**: de 2 a 4 contatos (mesma comunidade) de uma pessoa clonada
  pagam a mesma laranja em poucos minutos;
* cada valor recebido é repassado em até ~30 min, com uma pequena comissão retida a cada
  salto, direto para a coletora (`repasse_laranja`) ou por uma cadeia de intermediários
  (`lavagem_em_cadeia`);
* com `laundering_typologies`, cada quadrilha sorteia a forma de lavagem, inspirada nas
  tipologias do AMLworld:
  * `espalha_junta`: a laranja divide o valor entre os intermediários, e eles o juntam
    de novo na coletora;
  * `ciclo`: o dinheiro dá uma volta e passa pela laranja de novo;
  * `bipartido`: cada repasse usa um intermediário sorteado;
* com `collector_cashout`, a coletora saca cada valor para uma corretora (um comércio)
  depois de algumas horas, em vez de só acumular;
* as contas criadas para a fraude fazem alguns Pix comuns (camuflagem); com
  `p_recruited_mule`, parte das laranjas é uma pessoa que já existia, com todo o seu
  histórico (conta cedida ou alugada).

### Negativos difíceis

São contas **legítimas** que se comportam como partes de uma quadrilha. Sem elas, só a
fraude repassa dinheiro, e isso é um atalho:

* `salario`: comércios pagam a folha no 5º dia útil (`employees_per_merchant`). É um leque
  de saída, como o de uma coletora que espalha dinheiro;
* `fornecedor`: comércios pagam outros comércios toda semana (`supplier_tx_per_week`);
* `vaquinha`: uma pessoa junta dinheiro de 3 a 8 contatos em poucas horas e paga um
  comércio (`p_organizer`), como uma laranja que recebe de várias vítimas e repassa;
* `repasse_salario`: uma pessoa repassa de 30% a 60% do salário (o aluguel) em poucas
  horas (`p_fast_forwarder`), o que dá tempo de permanência curto a uma conta legítima.

### Limitações conhecidas (importantes para a análise)

O gerador **embute** hipóteses sobre como as fraudes acontecem, e um detector que as
encontra está, em parte, apenas redescobrindo essas hipóteses. Ao interpretar os
resultados, lembre-se de que, com a configuração padrão:

| Limitação | Efeito | Como desligar (`simulacao`) |
|-----------|--------|-----------------------------|
| os golpes acontecem em **qualquer horário com a mesma probabilidade**, enquanto os Pix legítimos seguem o perfil horário `HOUR_WEIGHTS` | `night_ratio` é um sinal forte **por construção** | `fraud_hours: comercial` |
| 70% das contas fraudulentas são recém-abertas (`account_age_days` < 60) | a idade da conta denuncia a fraude | `p_new_fraud_account: 0.0` |
| toda pessoa legítima é razoavelmente ativa (~18 Pix enviados por mês) | qualquer conta com poucos Pix já parece anômala (exercício 4 de `estudos/04_padroes_de_fraude.ipynb`) | `quiet_fraction: 0.3` |
| a taxa de fraude (~2% das contas) é muito maior que a real: segundo o BCB, há cerca de 5 contestações aceitas a cada 100 mil Pix | métricas mais altas do que num cenário real | menos quadrilhas (`n_rings`) e mais pessoas (`n_people`); o `calibrado` fica em ~10x a real |
| P2P e P2B têm o mesmo valor, e o golpe vale ~3x um Pix comum (BCB: R$ 257, R$ 114 e ~9x) | valores fora da escala real | `amount_mu`, `merchant_amount_mu`, `fraud_amount_shift`, `p_merchant` (valores no `calibrado`) |
| as laranjas repassam em ~30 min | o tempo de permanência (`dwell_time_min`) é um sinal forte | `forward_delay_min: 360` |
| **só a fraude repassa dinheiro**: comércios só recebem, e nenhuma pessoa legítima recebe e repassa logo | comércios nunca parecem contas de passagem; repasse rápido denuncia a fraude | negativos difíceis: `employees_per_merchant`, `supplier_tx_per_week`, `p_organizer`, `p_fast_forwarder` |
| as laranjas são contas novas, com ~3 Pix de camuflagem | a falta de histórico denuncia a laranja | `p_recruited_mule` |
| a coletora só acumula | a coletora é um "sumidouro" fácil de achar | `collector_cashout: true` |
| toda quadrilha lava em cadeia ou repassa direto | uma única forma de lavagem | `laundering_typologies` |
| todo dia tem o mesmo movimento | sem ritmo de semana nem de começo de mês | `calendar: semanal` |

A taxa de fraude foi inflada de propósito, para haver exemplos suficientes. Os cenários
de [`configs/cenarios.yaml`](../configs/cenarios.yaml) combinam esses parâmetros, do mais
fácil ao mais difícil, e `python scripts/avaliar_cenarios.py` mede o quanto cada
resultado depende deles (ver [`docs/resultados.md`](../docs/resultados.md)).

Com todos os parâmetros de realismo desligados (o padrão), o gerador produz **exatamente**
o mesmo dataset de antes de eles existirem. Um teste confere isso com uma impressão
digital do dataset. Por isso os resultados antigos continuam reproduzíveis. O cenário
**`calibrado`** liga tudo e usa os números do BCB; é o cenário principal da pesquisa.

O que continua simplificado, mesmo no `calibrado`:

* as vítimas do falso suporte são sorteadas ao acaso;
* os feriados não entram no calendário;
* a contestação é um sorteio, com atraso lognormal, e não depende do valor;
* não há dispositivos, CPFs nem telefones: o grafo tem um só tipo de vértice (ver
  [grafos heterogêneos](../docs/futuro/grafos-heterogeneos-e-custo-operacional.md)).

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
