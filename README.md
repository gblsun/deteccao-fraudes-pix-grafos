# Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning

Repositório da pesquisa de iniciação científica que investiga como a teoria dos grafos e
métodos de detecção de anomalias podem identificar e **explicar** fraudes em transações
PIX. As contas são modeladas como vértices e as transferências como arestas. Métricas
estruturais (grau, centralidade, intermediação) alimentam detectores não supervisionados
(Isolation Forest e DBSCAN), e os resultados são interpretados com grafos de calor e
heatmaps de risco.

Texto completo da proposta: [docs/proposta.md](docs/proposta.md) ([PDF original](docs/proposta-original.pdf)).
**Mapa de toda a documentação**: [docs/README.md](docs/README.md). Cada pasta tem o seu
README (por exemplo, [scripts/](scripts/README.md) e [reports/](reports/README.md)).

**Para estudar:** a pasta [estudos/](estudos/) tem notebooks sobre teoria dos grafos aplicada
a fraudes no Pix, com exercícios e gabarito, além das ferramentas para criar, recortar,
desenhar e exportar grafos.

## Estrutura

```
├── app/explorador.py          explorador interativo (Streamlit)
├── configs/
│   ├── experimento.yaml       parâmetros da simulação, dos atributos e dos modelos
│   └── cenarios.yaml          cenários de dificuldade (desligam os atalhos do gerador)
├── data/                      dados (não versionados), ver data/README.md
├── docs/
│   ├── proposta.md            proposta da pesquisa (e proposta-original.pdf)
│   ├── cronograma.md          etapas e acompanhamento
│   ├── resultados.md          resultados e interpretação dos experimentos
│   ├── revisao-bibliografica.md  índice das leituras e sugestões
│   ├── referencias.bib        referências em BibTeX
│   ├── obsidian.md            como usar o repositório como cofre do Obsidian
│   ├── leituras/              um fichamento por leitura
│   ├── diario/                diário de pesquisa (uma nota por dia)
│   ├── reunioes/              atas das reuniões de orientação
│   └── modelos/               modelos de fichamento, reunião e diário
├── estudos/                   notebooks de estudo, gabarito e cola de NetworkX
├── notebooks/                 análises exploratórias da pesquisa
├── reports/
│   ├── figures/               grafos de calor, heatmaps de risco, robustez e cenários
│   ├── estudos/               grafos gerados nos estudos (inclui a rede inteira em HTML)
│   └── results/               métricas dos experimentos
├── scripts/                   pontos de entrada (ver "Pipeline")
├── src/pixfraud/              código da pesquisa (pacote Python)
│   ├── simulation.py          gerador do dataset sintético de transações PIX
│   ├── bcb.py                 acesso aos dados abertos do PIX (Banco Central)
│   ├── external.py            datasets públicos (AMLworld, PaySim) no formato do projeto
│   ├── graph.py               criação de grafos, trilha do dinheiro, resumo
│   ├── temporal.py            caminhos que respeitam a ordem dos Pix, tempo de permanência
│   ├── communities.py         comunidades (Louvain), k-núcleos, subgrafo denso, OddBall
│   ├── flow.py                fluxo máximo, corte mínimo ("onde bloquear"), propagação de risco
│   ├── algorithms.py          ramificação máxima, caminho gargalo, VF2, HITS, SimRank
│   ├── patterns.py            padrões de fraude (fan-in, cadeia, ciclo...) e injeção
│   ├── features.py            atributos por conta, em conjuntos (tabular, grafo...)
│   ├── anomaly.py             Isolation Forest e DBSCAN
│   ├── evaluation.py          métricas de desempenho
│   ├── stats.py               testes estatísticos, bootstrap, comparações pareadas, modelo nulo
│   ├── experiment.py          núcleo do experimento (uma semente ou várias)
│   ├── online.py              detecção ao longo do tempo: a conta foi bloqueada a tempo?
│   ├── visualization.py       desenho, HTML interativo, Gephi, grafo de calor, heatmap
│   └── explorer.py            página da rede inteira (sigma.js), com filtros e linha do tempo
└── tests/                     testes automatizados (pytest)
```

## Como começar

Requer Python 3.10 ou superior. No PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,notebooks,app]"
pytest
```

(No Linux/macOS, ative com `source .venv/bin/activate`.)

## Pipeline

```powershell
# 1. gera o dataset sintético em data/synthetic/
python scripts/gerar_dataset.py

# 2. monta o grafo, extrai atributos, roda os detectores e salva métricas e figuras
python scripts/rodar_experimento.py

# 3. (opcional) baixa estatísticas públicas do PIX para calibrar o gerador
python scripts/baixar_dados_bcb.py fraudes 202506
python scripts/baixar_dados_bcb.py transacoes 202506 --filtro "AnoMes eq 202506"

# criar grafos avulsos: padrões de fraude, CSVs quaisquer, trilha do dinheiro de uma conta
python scripts/criar_grafo.py padrao mule_ring --saida reports/estudos/anel.png
python scripts/criar_grafo.py csv data/synthetic/transactions.csv --conta C000333 --saltos 5 --direcao tras --saida reports/estudos/trilha.html
```

O formato de saída de `criar_grafo.py` vem da extensão: `.png`/`.svg`/`.pdf`, `.html`
(interativo, abre no navegador) ou `.gexf`/`.graphml` (Gephi). `criar_grafo.py fluxo`
calcula o fluxo máximo e as contas a bloquear entre origens e um destino.

```powershell
# repete o experimento com 10 sementes: médias, intervalos de confiança e testes pareados
python scripts/avaliar_robustez.py --sementes 10

# repete em cada cenário de configs/cenarios.yaml (do mais fácil ao mais difícil)
python scripts/avaliar_cenarios.py --sementes 10

# a rede inteira numa página HTML, com busca, filtros e linha do tempo
python scripts/visualizar_rede.py

# explorador interativo: rede, ficha da conta, padrões, fluxo e resultados
streamlit run app/explorador.py

# validação externa no AMLworld, só com transferências parecidas com o Pix (ver data/README.md)
python scripts/importar_dataset.py amlworld data/raw/HI-Small_Trans.csv --padroes data/raw/HI-Small_Patterns.txt --formatos ACH Wire --saida data/external/amlworld_pix
python scripts/avaliar_externo.py --dados data/external/amlworld_pix --saida reports/amlworld

# detecção ao longo do tempo: quanto do dinheiro roubado seria bloqueado a tempo?
python scripts/avaliar_deteccao_online.py --sementes 3
```

As avaliações longas salvam o progresso: se forem interrompidas, rodar de novo continua
de onde parou.

Todos os parâmetros ficam em [configs/experimento.yaml](configs/experimento.yaml). Com a
mesma configuração e a mesma semente, o resultado é idêntico.

O experimento compara **2 detectores × 6 conjuntos de atributos** (tabular, grafo,
combinado, temporal, grafo avançado e completo) e grava:

- `reports/results/metricas.csv`: precision, recall, F1, ROC-AUC, average precision e
  precision@k de cada combinação;
- `reports/figures/grafo_de_calor_*.png`: as contas mais suspeitas e sua vizinhança,
  coloridas pelo risco;
- `reports/figures/heatmap_risco_*.png`: os atributos que explicam o risco de cada conta
  suspeita.

Um único dataset não basta para afirmar que uma abordagem é melhor: `avaliar_robustez.py`
e `avaliar_cenarios.py` repetem tudo com várias sementes e aplicam testes pareados,
`avaliar_externo.py` testa a mesma configuração num dataset que não fomos nós que geramos
(AMLworld), e `avaliar_deteccao_online.py` mede se a detecção acontece a tempo de bloquear
o dinheiro. Os resultados e sua interpretação estão em [docs/resultados.md](docs/resultados.md).

## Atributos

| Conceito da proposta            | Atributo (`features.py`)                                   | Conjunto |
|---------------------------------|------------------------------------------------------------|----------|
| Grau                            | `in_degree`, `out_degree`                                  | grafo    |
| Centralidade                    | `pagerank` (ponderado pelo valor)                           | grafo    |
| Intermediação (*betweenness*)   | `betweenness`                                              | grafo    |
| Coesão da vizinhança            | `clustering`, `avg_neighbor_degree`                        | grafo    |
| Volume e frequência             | `n_sent`, `n_received`, `amount_sent`, `amount_received`, `max_amount_received` | tabular |
| Repasse rápido (conta laranja)  | `pass_through`                                             | tabular  |
| Comportamento temporal          | `night_ratio`                                              | tabular  |
| Perfil da conta                 | `account_age_days`                                         | tabular  |
| Velocidade de repasse           | `dwell_time_min` (mediana do tempo até o próximo Pix enviado) | temporal |
| Picos de recebimento            | `max_daily_in_degree` (maior nº de pagadores distintos num dia) | temporal |
| Coesão estrutural               | `core_number` (k-núcleo)                                   | grafo avançado |
| Ponte entre comunidades         | `participation` (coeficiente de participação, Louvain)     | grafo avançado |
| Egonet fora do padrão (OddBall) | `oddball_en` (estrela ou quase clique), `oddball_ew` (dinheiro demais para a vizinhança) | grafo avançado |

Os conjuntos (`FEATURE_SETS` em `features.py`) são **tabular**, **grafo**, **combinado**
(tabular + grafo), **temporal**, **grafo_avancado** (grafo + grafo avançado) e
**completo** (todos).

## Dados

O dataset sintético simula contas legítimas (pessoas em círculos de contatos e comércios)
e quadrilhas com contas laranja, intermediários e coletoras, nos cenários de falso
suporte, clonagem de WhatsApp, repasse e lavagem em cadeia. Esquema, cenários e
**limitações conhecidas** do gerador estão em [data/README.md](data/README.md). Leia antes
de interpretar os resultados.

## Ética e LGPD

O projeto não usa dados pessoais reais. Os dados sintéticos não correspondem a pessoas
reais, e os dados do Banco Central são estatísticas agregadas e públicas.

## Organização do trabalho

- Etapas e andamento: [docs/cronograma.md](docs/cronograma.md)
- Estudos: [estudos/README.md](estudos/README.md)
- Leituras: [docs/revisao-bibliografica.md](docs/revisao-bibliografica.md) (índice) e um
  fichamento por leitura em `docs/leituras/`
- Diário de pesquisa: `docs/diario/AAAA-MM-DD.md`, a partir de [docs/modelos/diario.md](docs/modelos/diario.md)
- Reuniões de orientação: `docs/reunioes/AAAA-MM-DD.md`, a partir de [docs/modelos/reuniao.md](docs/modelos/reuniao.md)
- Notas no Obsidian: o repositório já é um cofre configurado, ver [docs/obsidian.md](docs/obsidian.md)
- Novos notebooks: prefixo numérico e nome descritivo (`02_perfis_de_fraude.ipynb`).
  Código reaproveitável vai para `src/pixfraud/`, com teste em `tests/`.
