---
tags: [pesquisa]
---

# Próximos passos

O que ficou em aberto, para retomar numa próxima sessão (de pessoa ou de agente de IA).
Marque `[x]` e aponte para onde foi feito; quando tudo de uma seção acabar, apague-a.
Os próximos passos de pesquisa com mais contexto estão em
[resultados, seção 16](resultados.md) e no [diário](diario/diario-de-pesquisa.md).

Volta para o [índice da documentação](mapa-da-pesquisa.md).

Última atualização: 2026-09-29.

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

- [ ] Levar as anotações da [reunião de 24/09](reunioes/2026-09-24.md) já resolvidas: tipo de
  rede (só os recebimentos têm lei de potência), cosseno × Jaccard e coletora ativa
  ([resultados, seção 13](resultados.md)).

- [ ] **Quantas sementes usar** (pedido de 24/09): 1000 sementes serviram uma vez, como
  referência. Proposta: 10 para explorar, **100 nos números do relatório**, e o número
  exato pela análise de poder (`reports/results/sementes_pareadas.csv`). Com sementes
  demais, diferenças irrelevantes (0,006 de AP) viram "significativas", e mais sementes não
  corrigem o viés do gerador. Argumento completo no [diário de 29/09](diario/2026-09-29.md)
  e em [resultados, seção 12](resultados.md).

- [ ] Levar as seções 10 e 11 dos [resultados](resultados.md): a GNN só compensa com muitos
  rótulos; no Pix, com poucas contestações, a propagação de risco ainda é melhor.
- [ ] Levar os cenários de dificuldade e a detecção a tempo (pendente desde 22/09).
- [ ] Discutir se a taxa de fraude do cenário `realista` (0,6% das contas) é alta demais.

## Pesquisa (reunião de 24/09)

- [ ] Refazer as seções 1 e 2 dos resultados com 100 sementes, se o orientador concordar
  ([resultados, seção 12](resultados.md)).
- [ ] Transformar a conferência por papel da coletora (percentil no ranking) num script; hoje
  ela é avulsa ([resultados, seção 13](resultados.md)).
- [ ] Usar o cosseno e os passeios aleatórios como escore (similaridade com as fraudes
  conhecidas; visitas a partir das vítimas) e comparar com a propagação de risco.

## Dados

- [ ] **AMLworld não importado nesta máquina** (`data/external/` não existe): a
  reprodução completa pula a validação externa. Ver [data/README.md](../data/README.md).
- [ ] Calibração do gerador com o BCB, bloqueada pelo erro 504 do servidor.

## Repositório

- [x] Integrar o branch local `local-2026-09-24` (29/09; ver [modelos, seção 10](modelos.md)
  e o [diário](diario/2026-09-29.md)).
- [ ] Rodar [`avaliar_modelos.py`](../scripts/avaliar_modelos.py) pela primeira vez e
  levar ECOD, One-Class SVM, autoencoder, node2vec, label spreading e gradient boosting para
  os resultados.
- [ ] Rodar os cenários novos do branch integrado (`negativos_dificeis`,
  `quadrilhas_realistas`, `calibrado`) com `avaliar_cenarios.py`.
- [ ] Comparar as duas GraphSAGE (`sage_supervised_scores` × `graphsage_scores`, direcionada)
  e os dois FRAUDAR (blocos × remoção gulosa), e ficar com uma de cada, ou explicar por que
  manter as duas.
- [ ] Incluir `avaliar_sementes.py`, `analisar_tipo_de_rede.py` e `avaliar_modelos.py` no
  `reproduzir_tudo.py`.
- [ ] O Controle Inteligente de Aplicativos do Windows bloqueia a `_liblinear.pyd` do
  scikit-learn 1.9.1 nesta máquina; o `.venv` usa o 1.8.0. Se outro computador tiver o
  mesmo erro ("política de Controle de Aplicativo"), `pip install scikit-learn==1.8.0`.

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
