# Detecção de Fraudes em Transações PIX utilizando Teoria dos Grafos e Machine Learning

Repositório da pesquisa de iniciação científica que investiga como a teoria dos grafos e
métodos de detecção de anomalias podem identificar e **explicar** fraudes em transações
PIX. As contas são modeladas como vértices e as transferências como arestas. Métricas
estruturais (grau, centralidade, intermediação) alimentam detectores não supervisionados
(Isolation Forest e DBSCAN), e os resultados são interpretados com grafos de calor e
heatmaps de risco.

Texto completo da proposta: [docs/proposta.md](docs/proposta.md) ([PDF original](docs/proposta-original.pdf)).

**Para estudar:** a pasta [estudos/](estudos/) tem notebooks sobre teoria dos grafos aplicada
a fraudes no Pix, com exercícios e gabarito, além das ferramentas para criar, recortar,
desenhar e exportar grafos.

## Estrutura

```
├── configs/experimento.yaml   parâmetros da simulação, dos atributos e dos modelos
├── data/                      dados (não versionados), ver data/README.md
├── docs/
│   ├── proposta.md            proposta da pesquisa (e proposta-original.pdf)
│   ├── cronograma.md          etapas e acompanhamento
│   ├── revisao-bibliografica.md  fichamentos e sugestões de leitura
│   ├── referencias.bib        referências em BibTeX
│   └── reunioes/              atas das reuniões de orientação
├── estudos/                   notebooks de estudo, gabarito e cola de NetworkX
├── notebooks/                 análises exploratórias da pesquisa
├── reports/
│   ├── figures/               grafos de calor e heatmaps de risco
│   ├── estudos/               grafos gerados nos estudos
│   └── results/               métricas dos experimentos
├── scripts/                   pontos de entrada (pipeline e criar_grafo.py)
├── src/pixfraud/              código da pesquisa (pacote Python)
│   ├── simulation.py          gerador do dataset sintético de transações PIX
│   ├── bcb.py                 acesso aos dados abertos do PIX (Banco Central)
│   ├── graph.py               criação de grafos, trilha do dinheiro, resumo
│   ├── patterns.py            padrões de fraude (fan-in, cadeia, ciclo...) e injeção
│   ├── features.py            atributos tabulares e de grafo por conta
│   ├── anomaly.py             Isolation Forest e DBSCAN
│   ├── evaluation.py          métricas de desempenho
│   └── visualization.py       desenho, HTML interativo, Gephi, grafo de calor, heatmap
└── tests/                     testes automatizados (pytest)
```

## Como começar

Requer Python 3.10 ou superior. No PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,notebooks]"
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
(interativo, abre no navegador) ou `.gexf`/`.graphml` (Gephi).

Todos os parâmetros ficam em [configs/experimento.yaml](configs/experimento.yaml). Com a
mesma configuração e a mesma semente, o resultado é idêntico.

O experimento compara **2 detectores × 3 conjuntos de atributos** (tabular, grafo e
combinado) e grava:

- `reports/results/metricas.csv`: precision, recall, F1, ROC-AUC, average precision e
  precision@k de cada combinação;
- `reports/figures/grafo_de_calor_*.png`: as contas mais suspeitas e sua vizinhança,
  coloridas pelo risco;
- `reports/figures/heatmap_risco_*.png`: os atributos que explicam o risco de cada conta
  suspeita.

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
- Leituras: [docs/revisao-bibliografica.md](docs/revisao-bibliografica.md)
- Reuniões de orientação: copiar [docs/reunioes/modelo.md](docs/reunioes/modelo.md)
- Novos notebooks: prefixo numérico e nome descritivo (`02_perfis_de_fraude.ipynb`).
  Código reaproveitável vai para `src/pixfraud/`, com teste em `tests/`.
