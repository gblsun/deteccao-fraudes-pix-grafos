---
tags: [mapa]
---

# Testes

Testes automatizados com [pytest](https://docs.pytest.org). Rodam no GitHub a cada push
(`.github/workflows/testes.yml`) e devem passar antes de qualquer commit.

```powershell
pytest                            # todos
pytest tests/test_simulation.py   # um arquivo
pytest -k online                  # só os testes com "online" no nome
pytest -m "not lento"             # pula os que rodam scripts inteiros e o app (~15 s no total)
ruff check .                      # estilo e erros comuns (configuração no pyproject.toml)
```

Os testes usam datasets minúsculos gerados na hora (centenas de contas, poucos dias),
então não dependem de `data/`. O teste do app é pulado se o Streamlit não estiver
instalado.

## O que cada arquivo testa

| Arquivo | Módulo | Principais verificações |
|---------|--------|-------------------------|
| `test_simulation.py` | `simulation` | mesma semente = mesmo dataset; papéis e rótulos; parâmetros de realismo (horário, idade, inativos, relógio de atividade) |
| `test_graph_tools.py` | `graph` | agregação de Pix repetidos, CSV de exemplo, matriz de adjacência, trilha do dinheiro |
| `test_features.py` | `features` | cada atributo calculado à mão num grafo pequeno |
| `test_temporal.py` | `temporal` | caminhos que respeitam o tempo, espera máxima, tempo de permanência |
| `test_communities.py` | `communities` | comunidades, k-núcleos, subgrafo denso plantado, FRAUDAR acha as quadrilhas uma depois da outra e ignora o bloco que é a rede inteira, OddBall acha a estrela |
| `test_flow.py` | `flow` | fluxo máximo = corte mínimo, contas a bloquear, propagação de risco |
| `test_algorithms.py` | `algorithms` | caminho gargalo, ramificação máxima, VF2, HITS, cosseno = ângulo entre vetores |
| `test_network.py` | `network` | expoente da lei de potência recuperado, BA × ER, componente gigante fraca e forte, passeios que terminam na coletora (ou passam por ela, com `collector_payouts`) |
| `test_patterns.py` | `patterns` | formato dos padrões, comissão por salto, injeção |
| `test_anomaly.py` | `anomaly`, `evaluation` | o detector acha o ponto isolado; métricas num ranking perfeito |
| `test_evaluation.py` | `evaluation`, `visualization` | recall por grupo; matriz de resultados |
| `test_stats.py` | `stats` | delta de Cliff, Holm, bootstrap, testes pareados, modelo nulo |
| `test_experiment.py` | `experiment` | uma rodada por semente; cenários válidos |
| `test_external.py` | `external` | AMLworld e PaySim (com arquivos de exemplo embutidos), formas de pagamento, tipologias, janelas |
| `test_buscar.py` | `scripts/buscar.py` | acentos e separadores ignorados, palavras de parada, nota do título primeiro, vizinhos sem bibliotecas, código citado nas notas |
| `test_online.py` | `online` | dinheiro recuperado calculado à mão, exposição, pontos de corte |
| `test_bcb.py` | `bcb` | novas tentativas em 504 e falha de conexão, sem tentar de novo em erro definitivo (404); parâmetros da URL (sem rede) |
| `test_gnn_direcionada.py` | `gnn` | a GraphSAGE direcionada (`graphsage_scores`) fica bem acima do acaso e é reproduzível pela semente (pulado sem `torch_geometric`) |
| `test_graph_models.py` | `graph_models` | FRAUDAR por remoção gulosa e node2vec + Isolation Forest |
| `test_gnn.py` | `gnn` | a GraphSAGE acha a quadrilha só pela estrutura (atributos são ruído); o DOMINANT pontua mais a quadrilha; recusa grafo grande demais (pulado sem torch) |
| `test_explorer.py` | `explorer` | layout por comunidades e página HTML |
| `test_pipeline.py` | tudo | o pipeline de ponta a ponta num dataset pequeno |
| `test_scripts.py` | `scripts/` | os scripts de avaliação rodam e gravam o que prometem; progresso salvo é reaproveitado |
| `test_app.py` | `app/` | o explorador Streamlit abre todas as abas sem erro |
| `test_docs.py` | documentação | links relativos existem, toda nota tem tag, cada pasta tem nota-mapa, docstrings, `docs/grafo-de-notas.json` atualizado |

## Escrevendo um teste novo

Um arquivo por módulo (`test_<módulo>.py`). Prefira casos pequenos em que o resultado
certo dá para calcular à mão (veja `test_online.py`) e use `SimulationConfig` com poucas
contas quando precisar de um dataset.
