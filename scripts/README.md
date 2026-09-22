# Scripts

Pontos de entrada da pesquisa. Rode sempre da **raiz do repositório**, com o ambiente
ativado (`.venv\Scripts\Activate.ps1`). Cada script tem `--help` e uma docstring no topo
com exemplos de uso.

## Mapa

| Script | O que faz | Lê | Grava | Tempo aprox. |
|--------|-----------|----|-------|--------------|
| [`gerar_dataset.py`](gerar_dataset.py) | gera o dataset sintético | `configs/experimento.yaml` | `data/synthetic/` | segundos |
| [`rodar_experimento.py`](rodar_experimento.py) | uma rodada: grafo, atributos, 2 detectores × 6 conjuntos, figuras | `data/synthetic/` | `reports/results/metricas.csv`, `reports/figures/grafo_de_calor_*`, `heatmap_risco_*` | ~1 min |
| [`avaliar_robustez.py`](avaliar_robustez.py) | repete com várias sementes; IC e testes pareados | configuração | `reports/results/robustez_*.csv`, `robustez_average_precision.png` | ~4 min (10 sementes) |
| [`avaliar_cenarios.py`](avaliar_cenarios.py) | repete em cada cenário de dificuldade | `configs/cenarios.yaml` | `reports/results/cenarios_*.csv`, `cenarios_*.png` | ~40 min (8 cenários × 10 sementes) |
| [`avaliar_deteccao_online.py`](avaliar_deteccao_online.py) | detecção ao longo do tempo: bloqueou a tempo? | `configs/cenarios.yaml` | `reports/results/online_*`, `online_deteccao.png` | dezenas de minutos |
| [`avaliar_externo.py`](avaliar_externo.py) | mesma configuração num dataset externo, por janelas; recall por tipologia | `data/external/<nome>/` | `reports/amlworld/` | minutos por janela |
| [`importar_dataset.py`](importar_dataset.py) | converte AMLworld ou PaySim para o formato do projeto | `data/raw/` | `data/external/<nome>/` | ~1 min |
| [`baixar_dados_bcb.py`](baixar_dados_bcb.py) | baixa estatísticas do Pix do Banco Central | API do BCB | `data/bcb/` | segundos |
| [`visualizar_rede.py`](visualizar_rede.py) | página HTML da rede inteira, com filtros e linha do tempo | `data/synthetic/` | `reports/estudos/rede_completa.html` | ~1 min |
| [`criar_grafo.py`](criar_grafo.py) | grafos avulsos: padrões, CSVs quaisquer, trilha do dinheiro, fluxo | CSV ou padrão | o arquivo de `--saida` | segundos |

As avaliações longas (`avaliar_externo.py` e `avaliar_deteccao_online.py`) salvam cada
janela ou semente assim que terminam. Se forem interrompidas, rodar de novo continua de
onde parou; `--refazer` recalcula tudo.

## Reproduzir os resultados

Na ordem, com a configuração versionada, os resultados saem idênticos (as sementes são
fixas):

```powershell
python scripts/gerar_dataset.py
python scripts/rodar_experimento.py
python scripts/avaliar_robustez.py --sementes 10
python scripts/avaliar_cenarios.py --sementes 10
python scripts/avaliar_deteccao_online.py --sementes 3
# só se o AMLworld tiver sido baixado e importado (ver data/README.md)
python scripts/avaliar_externo.py --dados data/external/amlworld_pix --saida reports/amlworld
```

O que cada arquivo gerado contém está em [`reports/README.md`](../reports/README.md).
