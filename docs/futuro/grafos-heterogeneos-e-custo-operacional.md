---
tags: [ideia]
---

# Grafos heterogêneos e custo operacional

Volta para o [índice de ideias futuras](ideias-futuras.md).

Duas ideias menores, mas relacionadas: ambas mudam **o que se mede**, não o detector em
si.

## Grafos heterogêneos

O grafo desta pesquisa tem um tipo só de vértice (conta) e um tipo só de aresta (Pix) —
ver [`src/pixfraud/graph.py`](../../src/pixfraud/graph.py). Uma quadrilha que cria várias
contas "laranja" com identidades diferentes, mas no mesmo aparelho, no mesmo IP ou com o
mesmo número de telefone, não deixa rastro nesse grafo: cada conta aparece isolada do
resto, mesmo compartilhando sinais fortes de ser controlada pela mesma pessoa. Um grafo
**heterogêneo** — vértices de tipos diferentes (conta, dispositivo, CPF, telefone) e
arestas "usa o mesmo dispositivo", "mesmo CPF" além de "fez um Pix" — capturaria esse
padrão de identidade sintética, que é justamente o ponto cego do grafo atual.

Isso exigiria dados que o simulador não gera hoje (device fingerprint, CPF, telefone) e
que o BCB/AMLworld também não trazem — então é uma ideia de dataset antes de ser uma
ideia de modelo: caberia estender `simulation.py` para atribuir dispositivos/CPFs
compartilhados às contas de uma mesma quadrilha, como mais um sinal de vazamento
controlado (do mesmo jeito que hoje existe `p_new_fraud_account` para controlar o viés de
conta nova).

## Custo operacional, não só AP e precision@k

A pesquisa avalia os detectores por average precision e precision@k
(ver [`docs/resultados.md`](../resultados.md)) — métricas de ranking, que assumem que
todo falso positivo custa o mesmo. Na prática não custa: investigar uma conta sinalizada
tem um custo fixo de tempo de analista, e bloquear uma conta legítima por engano tem um
custo de reputação/atrito com o cliente, diferente do custo de deixar passar uma fraude
pequena. Uma avaliação sensível a custo (por exemplo, dado um orçamento de X contas que
os analistas conseguem revisar por dia, quanto dinheiro se recupera com cada detector)
seria uma métrica adicional mais próxima de uma decisão real de operação — e reaproveita
o que já existe: `pixfraud.online.recovered_amount` já calcula dinheiro recuperado por
prazo de bloqueio; faltaria só fixar um orçamento de revisões por corte e comparar os
detectores por essa métrica, em vez de (ou além de) precision@k.

## Horizonte mais distante: aprendizado federado

Uma anotação mais especulativa: fraude no Pix atravessa instituições (a vítima paga de um
banco, a conta laranja recebe em outro). O grafo que qualquer banco enxerga sozinho é
sempre incompleto. Aprendizado federado ou troca de sinais entre instituições (sem trocar
dados brutos de cliente) é a resposta natural a isso, mas é um problema de várias
instituições coordenando, não de um projeto de iniciação científica sozinho — vale como
registro de direção de longo prazo, não como próximo passo.
