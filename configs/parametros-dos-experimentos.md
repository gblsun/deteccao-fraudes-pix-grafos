---
tags: [mapa]
---

# Configurações

Todos os parâmetros dos experimentos ficam aqui, versionados junto com os resultados:
com a mesma configuração e a mesma semente, o resultado é idêntico.

| Arquivo | Usado por | O que define |
|---------|-----------|--------------|
| [`experimento.yaml`](experimento.yaml) | todos os scripts | `simulacao` (o gerador sintético), `atributos` (intermediação aproximada) e `modelos` (Isolation Forest e DBSCAN) |
| [`cenarios.yaml`](cenarios.yaml) | `avaliar_cenarios.py`, `avaliar_deteccao_online.py` | cenários de dificuldade: cada um troca alguns parâmetros de `simulacao` |

Os comentários dentro de cada arquivo explicam os parâmetros. Um deles decide quanta
memória o experimento pode usar: `modelos.dbscan.max_exact` é o número de contas até o
qual o rótulo binário vem do DBSCAN completo (que guarda a vizinhança de cada conta, e
por isso gasta memória proporcional ao **quadrado** do nº de contas). Acima disso, o
rótulo passa a ser "não é ponto de núcleo", e as métricas principais (average precision e
precision@k) não mudam, porque dependem só do escore.

Os parâmetros de realismo da simulação (`fraud_hours`, `p_new_fraud_account`,
`quiet_fraction`...) desligam sinais que o gerador embute por construção; a tabela de
"Limitações conhecidas" em [`data/README.md`](../data/README.md) mostra qual parâmetro
desliga qual sinal.

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
