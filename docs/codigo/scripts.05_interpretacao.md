---
tags: [codigo]
---

# `scripts/05_interpretacao/`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Etapa 5: os erros dos modelos. Guia da pasta: [README.md](../../scripts/05_interpretacao/README.md) · [mapa do código](mapa-do-codigo.md)

## [`investigar_falsos_positivos.py`](../../scripts/05_interpretacao/investigar_falsos_positivos.py)

Quem são as contas no topo do risco que não são fraude? (reunião de 01/10)

Na reunião, contas de comércio apareceram com "percentil de risco 100%" no
explorador da rede. Este script responde, para cada detector:

* quais contas ficam no topo do risco e qual é o **papel real** de cada uma
  (vindo do gerador: o modelo não prevê papel nenhum, só dá um escore);
* quantos falsos positivos há entre as k primeiras (k = nº de fraudes), e de
  que papel eles são: comércio, vítima ou conta normal;
* que atributos levam esses falsos positivos ao topo (percentil de cada
  atributo da conta entre todas as contas);
* se isso muda nos cenários em que o comércio também paga (salários,
  fornecedores), como `negativos_dificeis`, `calibrado` e `aleatorio`.

A primeira semente de cada cenário é a do YAML (42), a do dataset em
`data/synthetic` e do explorador mostrado na reunião; o script confere se o
dataset gravado é mesmo esse.

Saídas em reports/05_interpretacao/results/:
    falsos_positivos_papeis.csv     uma linha por (cenário, semente, modelo): papéis no top-k
    falsos_positivos_top.csv        as `--top` contas de maior risco de cada modelo (semente 42)
    falsos_positivos_atributos.csv  percentil de cada atributo dessas contas
    falsos_positivos_testes.csv     (cenário, modelo): o modelo confunde comércio com fraude? (Fisher
                                    "no top-k" × "é comércio", só nas legítimas) e o escore ordena os
                                    papéis? (Kruskal-Wallis do escore por papel, com ε²)
    falsos_positivos_dunn.csv       que pares de papéis o escore separa (teste de Dunn, semente do YAML)
    falsos_positivos_meta.json      como o resultado foi gerado
e a figura reports/05_interpretacao/figures/falsos_positivos_comercio.png.

Uso:
    python scripts/05_interpretacao/investigar_falsos_positivos.py
    python scripts/05_interpretacao/investigar_falsos_positivos.py --cenarios base --sementes 1 --top 30

**Opções de linha de comando**

| Opção | Padrão | Para quê |
|---|---|---|
| `--config` | `'configs/experimento.yaml'` |  |
| `--arquivo-cenarios` | `'configs/cenarios.yaml'` |  |
| `--cenarios` | `['base', 'negativos_dificeis', 'calibra…` |  |
| `--sementes` | `10` | a do YAML e mais sementes 1, 2, ... |
| `--conjunto` | `'completo'` |  |
| `--top` | `20` | contas listadas por modelo na semente do YAML |
| `--dados` | `'data/synthetic'` | dataset gravado, conferido contra a semente do YAML |
| `--saida` | `'reports/05_interpretacao'` |  |

**Funções**

- `def main() -> None`: Ponto de entrada: lê os argumentos da linha de comando e roda o script (ver a docstring do módulo).
- `def _tests_table(runs: pd.DataFrame, alpha: float=0.05) -> pd.DataFrame`: Por (cenário, modelo): razão de chances mediana do comércio no top-k, em quantas sementes o Fisher deu p < alfa, e o ε² médio do Kruskal-Wallis do escore entre os papéis.
- `def _check_saved_dataset(base, data_dir: str) -> None`: Avisa se `data_dir` não é o dataset da semente do YAML (o do explorador da reunião).
- `def _plot_share(share: pd.DataFrame, n: int, path: Path) -> None`: Mapa de calor: fração das k primeiras contas de cada modelo que são comércios.
