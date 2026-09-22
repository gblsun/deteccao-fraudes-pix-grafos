# Notebooks da pesquisa

Análises que misturam código, figuras e texto. O material de **estudo** (teoria dos
grafos, exercícios) fica em [`estudos/`](../estudos/README.md); aqui ficam as análises
da pesquisa em si.

| Notebook | Etapa do cronograma | Conteúdo |
|----------|---------------------|----------|
| [`01_analise_exploratoria.ipynb`](01_analise_exploratoria.ipynb) | análise exploratória e validação do dataset | visão geral do dataset sintético, valores, horários, estrutura da rede, atributos por papel, escolha do `eps` do DBSCAN |

## Convenções

- Nome com prefixo numérico e descrição: `02_perfis_de_fraude.ipynb`.
- Código que vai ser reaproveitado vai para `src/pixfraud/`, com teste em `tests/`; o
  notebook só chama as funções.
- Commite o notebook **executado**, para as figuras aparecerem no GitHub:

```powershell
jupyter nbconvert --to notebook --execute --inplace notebooks/01_analise_exploratoria.ipynb
```

- Os notebooks leem `data/`, que não é versionada: gere os dados antes
  (`python scripts/gerar_dataset.py`).
