---
tags: [mapa]
---

# Configurações

Todos os parâmetros dos experimentos ficam aqui, versionados junto com os resultados:
com a mesma configuração e a mesma semente, o resultado é idêntico.

A exceção é o `gerar_dataset.py`: ele ignora `simulacao.seed` e sorteia uma semente nova
a cada execução, gravada em `data/synthetic/dataset_meta.json`. Para refazer um dataset,
passe `--seed N` (o `reproduzir_tudo.py` usa `--seed 42`, o dataset dos resultados em
`reports/`). O `rodar_experimento.py` copia essa semente para o `metricas_meta.json`
(`seed_do_dataset`). O explorador (`app/`) e os scripts de avaliação continuam usando
`simulacao.seed` ou as próprias sementes.

| Arquivo | Usado por | O que define |
|---------|-----------|--------------|
| [`experimento.yaml`](experimento.yaml) | todos os scripts | `simulacao` (o gerador sintético), `atributos` (intermediação aproximada) e `modelos` (os hiperparâmetros de cada modelo, escolhidos à mão) |
| [`busca_hiperparametros.yaml`](busca_hiperparametros.yaml) | `otimizar_hiperparametros.py` | os valores testados de cada hiperparâmetro e os limites até onde a grade pode crescer |
| `experimento_otimizado.yaml` | `avaliar_modelos.py --config` | cópia gerada por `scripts/otimizar_hiperparametros.py`, com os hiperparâmetros que venceram nas redes de validação (ver [mapa dos modelos](../src/pixfraud/models/mapa-dos-modelos.md)) |
| [`cenarios.yaml`](cenarios.yaml) | `avaliar_cenarios.py`, `avaliar_deteccao_online.py` | cenários de dificuldade: cada um troca alguns parâmetros de `simulacao` |

Os comentários dentro de cada arquivo explicam os parâmetros. Um deles decide quanta
memória o experimento pode usar: `modelos.dbscan.max_exact` é o número de contas até o
qual o rótulo binário vem do DBSCAN completo (que guarda a vizinhança de cada conta, e
por isso gasta memória proporcional ao **quadrado** do nº de contas). Acima disso, o
rótulo passa a ser "não é ponto de núcleo", e as métricas principais (average precision e
precision@k) não mudam, porque dependem só do escore.

Os parâmetros de realismo da simulação desligam sinais que o gerador embute por
construção. A tabela de "Limitações conhecidas" em [`data/README.md`](../data/README.md)
mostra qual parâmetro desliga qual sinal. Eles se dividem em quatro grupos:

| Grupo | Parâmetros |
|-------|------------|
| atalhos originais | `fraud_hours`, `p_new_fraud_account`, `quiet_fraction`, `forward_delay_min` |
| calibração com o BCB | `p_merchant`, `amount_mu`, `merchant_amount_mu` e `merchant_amount_sigma`, `fraud_amount_shift`, `calendar`, e a escala (`n_people`, `n_merchants`, `n_rings`) |
| negativos difíceis | `employees_per_merchant`, `salary_business_day`, `supplier_tx_per_week`, `p_organizer`, `p_fast_forwarder` |
| quadrilhas | `p_recruited_mule`, `collector_cashout` e `cashout_delay_min`, `collector_payouts`, `laundering_typologies`, `p_contested` e `contest_delay_h` |

Todos ficam desligados no `base`, que por isso continua gerando o mesmo dataset de sempre.
Os cenários `negativos_dificeis`, `quadrilhas_realistas` e `calibrado` os ligam. O
`calibrado` tem ~10 mil pessoas, e só o cálculo dos atributos leva perto de 1 minuto por
semente (contra ~5 s no `base`).

`collector_cashout` e `collector_payouts` são duas formas de a coletora mover o dinheiro,
e não podem ser ligadas juntas: a primeira saca cada valor para uma corretora (uma aresta
só); a segunda, pedida na reunião de 24/09, espalha ~90% do recebido em vários Pix para
pessoas e comércios (muitas arestas, rótulo `saida_coletor`). O cenário `coletor_ativo`
liga a segunda (`collector_payouts: 20`).

## Criar um cenário

Acrescente um bloco em `cenarios.yaml` com os parâmetros que mudam:

```yaml
meu_cenario:
  fraud_hours: comercial
  n_rings: 3
```

Nomes errados são recusados logo na leitura, antes de qualquer cálculo. Depois:
`python scripts/avaliar_cenarios.py --cenarios base meu_cenario --sementes 3`.

## Mudar um parâmetro

Mudar `experimento.yaml` muda todos os resultados que dependem dele. Refaça os scripts
de [`scripts/mapa-dos-scripts.md`](../scripts/mapa-dos-scripts.md) e commite a configuração junto com os
resultados novos.
