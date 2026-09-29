---
tags: [pesquisa]
---

# Próximos passos

O que ficou em aberto, para retomar numa próxima sessão (de pessoa ou de agente de IA).
Marque `[x]` e aponte para onde foi feito; quando tudo de uma seção acabar, apague-a.
Os próximos passos de pesquisa com mais contexto estão em
[resultados, seção 14](resultados.md) e no [diário](diario/diario-de-pesquisa.md).

Volta para o [índice da documentação](mapa-da-pesquisa.md).

Última atualização: 2026-09-28.

## Pesquisa

- [ ] **GraphSAGE para positivo e não rotulado**: com poucas fraudes conhecidas, a GNN
  perde para o Random Forest e para a propagação de risco
  ([resultados, seção 11](resultados.md)). Testar uma perda própria para contas sem rótulo
  (em vez de tratá-las como normais) e a GraphSAGE partindo do escore de
  [`flow.propagate_risk`](../src/pixfraud/flow.py).
- [ ] Rodar [`avaliar_gnn.py`](../scripts/avaliar_gnn.py) com **10 sementes** (hoje 5; o
  Wilcoxon com 5 não chega a p < 0,05 por construção).
- [ ] FRAUDAR com pesos que levem o tempo em conta, e um critério de parada melhor que
  "5% das contas" ([resultados, seção 9](resultados.md)).
- [ ] Fichar de verdade as 4 leituras de GNN que só têm o esqueleto:
  `guerra2025gnnfraude`, `dou2020caregnn`, `motie2024gnnreview`, `dellagarza2023aml`
  ([leituras](leituras/mapa-das-leituras.md)). Pedido da
  [reunião de 24/09](reunioes/2026-09-24.md).
- [ ] Conferir o TCC de Guerra na fonte primária antes de usar os dados dele no relatório.
- [ ] Decidir se alguma ideia de [`futuro/`](futuro/ideias-futuras.md) vira experimento
  dentro do cronograma.

## Para a próxima reunião

- [ ] Levar as seções 10 e 11 dos [resultados](resultados.md): a GNN só compensa com muitos
  rótulos; no Pix, com poucas contestações, a propagação de risco ainda é melhor.
- [ ] Levar os cenários de dificuldade e a detecção a tempo (pendente desde 22/09).
- [ ] Discutir se a taxa de fraude do cenário `realista` (0,6% das contas) é alta demais.

## Dados

- [ ] **AMLworld não importado nesta máquina** (`data/external/` não existe): a
  reprodução completa pula a validação externa. Ver [data/README.md](../data/README.md).
- [ ] Calibração do gerador com o BCB, bloqueada pelo erro 504 do servidor.

## Repositório

- [ ] Marcar no [cronograma](cronograma.md) as etapas que já têm entrega (dataset, grafos,
  métricas, modelos, visualizações, comparação tabular × grafos): hoje nenhuma está `[x]`.
- [ ] A etapa `gnn_rotulos` do `reproduzir_tudo.py` ainda não rodou dentro de uma
  reprodução completa (foi rodada à parte, com 10 sementes).
- [ ] Os `*_meta.json` da última reprodução completa registram
  `alteracoes_nao_commitadas: true` (o explorador ainda não estava em commit). Os números
  não mudaram; na próxima reprodução completa isso se resolve.
- [ ] `reports/estudos/anel.png` e `trilha.html` são saídas dos exemplos da
  [trilha de estudos](../estudos/trilha-de-estudos.md) e ficaram fora do git: decidir se
  entram no `.gitignore`.
