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
| `scenario`  | o que gerou o Pix (ver abaixo)                                    |
| `contestado_em` | quando a vítima contestou o golpe; **só existe** com `p_contested > 0`, e fica vazia nos demais Pix |

Valores de `scenario`:

* legítimos: `normal` e, com os negativos difíceis ligados, `salario`, `fornecedor`,
  `vaquinha` e `repasse_salario`;
* golpes: `falso_suporte` e `clonagem_whatsapp`;
* lavagem: `repasse_laranja`, `lavagem_em_cadeia`, `espalha_junta`, `ciclo` e `bipartido`;
* `saque`: a coletora tira o dinheiro para uma corretora (`collector_cashout`);
* `saida_coletor`: a coletora espalha o dinheiro em vários Pix para pessoas e comércios
  (`collector_payouts`).

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
* com `collector_payouts` (alternativa ao `collector_cashout`), a coletora esvazia ~90%
  do que recebeu em vários Pix para pessoas e comércios (`saida_coletor`);
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
| o **tamanho** de tudo é fixo: toda quadrilha tem 4 laranjas e 15 vítimas, sempre há 6 quadrilhas e 100 comércios | o detector vê sempre a mesma estrutura | `estrutura_aleatoria: true` (cenário `aleatorio`, abaixo) |

A taxa de fraude foi inflada de propósito, para haver exemplos suficientes. Os cenários
de [`configs/cenarios.yaml`](../configs/cenarios.yaml) combinam esses parâmetros, do mais
fácil ao mais difícil, e `python scripts/avaliar_cenarios.py` mede o quanto cada
resultado depende deles (ver [`docs/resultados.md`](../docs/resultados.md)).

Com todos os parâmetros de realismo desligados (o padrão), o gerador produz **exatamente**
o mesmo dataset de antes de eles existirem. Um teste confere isso com uma impressão
digital do dataset. Por isso os resultados antigos continuam reproduzíveis. O cenário
**`calibrado`** liga tudo e usa os números do BCB; é o cenário principal da pesquisa.

### Estrutura sorteada (`estrutura_aleatoria`, cenário `aleatorio`)

Pedido da [reunião de 01/10](../docs/reunioes/2026-10-01.md). Com `estrutura_aleatoria: true`, a
cada semente o gerador sorteia, antes de criar as contas (`simulation.draw_structure`):

| O quê | Como | Por quê |
|-------|------|---------|
| nº de quadrilhas | `1 + Poisson(n_rings - 1)` | `n_rings` vira a média |
| laranjas por quadrilha | `1 +` binomial negativa, média `mules_per_ring - 1` | quadrilhas muito desiguais: muitas pequenas, poucas grandes |
| vítimas por quadrilha | binomial negativa, média `victims_per_ring` (pelo menos uma por laranja) | idem |
| intermediários | Poisson com média `chain_length`, de 1 a 6 (2 a 6 se houver tipologias além da cadeia) | |
| laranjas recrutadas | fração Beta(2, 3), média 40%, por quadrilha | parte das laranjas é conta antiga cedida ou alugada |
| o que a coletora faz | acumula (30%), saca para uma corretora (40%) ou espalha em 5 a 29 Pix (30%) | cada quadrilha tira o dinheiro de um jeito |
| nº de comércios | 3% a 7% das pessoas | |
| folha e fornecedores | 2 a 6 funcionários e 0,5 a 2 pagamentos por semana, em média, por comércio | o comércio também paga, em vez de só receber |

Os papéis de cada conta já eram sorteados (os ids são embaralhados); agora o tamanho de cada
papel também é. O sorteio usa um gerador próprio (`default_rng([seed, 1])`), então o resto do
dataset continua determinado pela semente. `gerar_dataset.py --aleatorio` grava o que foi
sorteado em `dataset_meta.json` (`estrutura`). Desligado (o padrão), nada muda: o teste da
impressão digital continua passando.

### O papel de cada conta confere? (`audit_roles`)

`simulation.audit_roles` confere, conta por conta, se o papel bate com o que a conta fez. O
comércio é PJ e só paga salário e fornecedor; a laranja recebe golpe e repassa; a coletora
recebe repasses e é a única que tira o dinheiro; a vítima pagou um golpe e não é fraudadora.
`python scripts/auditar_papeis.py` roda isso em todos os cenários (20 sementes cada). O
resultado está em [`docs/resultados.md`](../docs/resultados.md). Com a estrutura fixa, há
duas falhas raras do gerador, mantidas para os resultados antigos não mudarem:

* **laranja sem golpe:** cada vítima sorteia a laranja da quadrilha, então ~1,7% das laranjas
  nunca recebe golpe. Ela continua com o rótulo de fraude, mas só faz Pix de camuflagem;
* **vítima recrutada:** com `p_recruited_mule`, uma pessoa que foi vítima de uma quadrilha pode
  ser recrutada como laranja de outra (2 casos nos 40 datasets com laranjas recrutadas).

Com `estrutura_aleatoria`, as duas são evitadas: cada laranja recebe ao menos um golpe, e
vítimas não são recrutadas.

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
