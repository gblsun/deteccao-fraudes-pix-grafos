---
tags: [metodo]
---

# Plano de testes estatísticos

Que teste de hipótese usar em cada etapa do [fluxo da pesquisa](fluxo-da-pesquisa.md), o que já
existe no projeto e o que falta implementar. As caixas da última seção acompanham o andamento.

## Kruskal-Wallis ou Friedman?

A escolha depende de os grupos serem **independentes** ou **pareados**:

| | Grupos independentes | Mesmas unidades medidas várias vezes (pareado) |
|---|---|---|
| **2 grupos** | [Mann-Whitney](glossario/mann-whitney.md) | [Wilcoxon pareado](glossario/teste-de-wilcoxon-pareado.md) |
| **3 ou mais grupos** | [Kruskal-Wallis](glossario/kruskal-wallis.md) + Dunn | Friedman + Nemenyi |

- **Kruskal-Wallis** serve quando cada observação pertence a um grupo só. Exemplos: um
  atributo comparado entre os 6 papéis das contas (normal, comércio, vítima, laranja,
  intermediário, coletor), ou a AP de um modelo comparada entre cenários.
- **Friedman** serve quando todos os grupos são medidos nas mesmas unidades. É o caso dos
  modelos: todos rodam nas **mesmas sementes** (mesmas redes). Usar Kruskal-Wallis aí
  jogaria fora o pareamento e perderia poder. O Friedman ordena os modelos dentro de cada
  semente. O post-hoc de Nemenyi dá a diferença crítica: dois modelos cujos postos médios
  ficam mais perto que ela não se distinguem. É o procedimento de Demšar (2006) para
  comparar vários classificadores.

## Testes por etapa

| Etapa | Pergunta | Teste | Tamanho do efeito | No projeto |
|---|---|---|---|---|
| 1. Dados: realismo | o sintético bate com o BCB (ticket médio P2P e P2B, % P2B, golpe médio)? | IC 95% entre sementes contém o valor do BCB + erro relativo com tolerância (o BCB só publica agregados, então KS não se aplica) | erro relativo | feito |
| 1. Dados: estrutura | a rede tem mais reciprocidade, triângulos ou ciclos que o acaso? | modelo nulo com graus preservados | escore z | `stats.null_model_test`, em `validar_realismo.py` |
| 2. Exploração | o atributo difere entre fraude e legítima? | Mann-Whitney + [Holm](glossario/correcao-de-holm.md) | [delta de Cliff](glossario/delta-de-cliff.md) | `stats.compare_groups` |
| 2. Exploração | o atributo difere entre os 6 papéis? | **Kruskal-Wallis** + Holm; post-hoc **Dunn** + Holm | ε² = H / (n − 1) | feito |
| 2. Exploração | categórica (madrugada, conta nova, PJ) × fraude | qui-quadrado; Fisher exato se 2×2 | V de Cramér; razão de chances | `stats.contingency_test` (com Fisher), em `inferencia_atributos.py` |
| 2. Exploração | o efeito se repete entre sementes? | fração das sementes com p de Holm < 0,05 e IC do delta | delta médio ± IC | `inferencia_*.csv` (sementes significativas) |
| 3. Modelos | o modelo é melhor que o acaso? | permutação da AP (embaralha o gabarito); hipergeométrico no top-k | AP − taxa de fraude | feito |
| 4. Avaliação | algum modelo difere dos outros? | **Friedman** (blocos = sementes) + **Nemenyi**, com diagrama de diferença crítica | W de Kendall; posto médio | feito |
| 4. Avaliação | o modelo A é melhor que o B? | Wilcoxon pareado + Holm, com IC t | diferença média de AP | `stats.compare_runs` |
| 4. Avaliação | a dificuldade do cenário muda a AP de um modelo? | **Kruskal-Wallis** entre cenários + Dunn | ε² | feito |
| 5. Interpretação | o modelo confunde comércio com fraude? | Fisher exato "está no top-k" × "é comércio", só nas contas legítimas | razão de chances | feito |
| 5. Interpretação | o escore de risco ordena os papéis? | Kruskal-Wallis do escore por papel + Dunn | ε² | feito |
| Validação externa | os resultados valem no AMLworld? | os mesmos testes, com as janelas de tempo no lugar das sementes | idem | parcial (`compare_runs` com `unit="janela"`) |

## Regras gerais

- **Efeito ao lado do p.** Com milhares de contas, quase tudo sai significativo. O que diz se a
  diferença importa é o tamanho do efeito.
- **Holm por família.** Uma família é uma métrica num cenário. Corrigir por todas as métricas
  juntas deixaria qualquer diferença "não significativa", porque com 10 sementes o menor p do
  Wilcoxon exato é ≈ 0,002 (ver `compare_runs`).
- **Separar validação e teste.** A inferência sobre atributos (etapa 2) e a otimização
  (etapa 3) usam as sementes de validação (1001, 1002…); as comparações finais (etapa 4) usam
  as sementes 1 a 10.
- **Não paramétrico por padrão.** Os atributos têm cauda pesada, e com 10 sementes não dá para
  confiar na normalidade.

## Implementação

### Funções em [`stats.py`](../src/pixfraud/stats.py)

- [x] `kruskal_groups(features, groups)`: H, p, p de Holm e ε² por atributo.
- [x] `dunn_posthoc(values, groups)`: z dos postos médios (com correção de empates) e p de Holm por par.
- [x] `friedman_models(runs, metric, ...)`: χ², p, W de Kendall, postos médios e diferença crítica de Nemenyi.
- [x] `permutation_test_metric(labels, scores, metric, n_perm)`: p empírico (b + 1) / (n + 1).
- [x] `topk_hypergeom(labels, scores, k)`: fraudes no top-k e p hipergeométrico.
- [x] `contingency_test` com Fisher exato e razão de chances nas tabelas 2×2.

### Scripts

- [x] [`01_dados/validar_realismo.py`](../scripts/01_dados/): sintético × BCB e modelo nulo da estrutura.
- [x] [`02_exploracao/inferencia_atributos.py`](../scripts/02_exploracao/): Mann-Whitney, Kruskal-Wallis + Dunn
  por papel e contingência, nas sementes de validação.
- [x] [`03_modelos/avaliar_modelos.py`](../scripts/03_modelos/avaliar_modelos.py): Friedman + diagrama de diferença
  crítica, teste contra o acaso e Kruskal-Wallis entre cenários.
- [x] [`05_interpretacao/investigar_falsos_positivos.py`](../scripts/05_interpretacao/investigar_falsos_positivos.py):
  Fisher top-k × comércio e Kruskal-Wallis do escore por papel.
- [x] [`reproduzir_tudo.py`](../scripts/reproduzir_tudo.py): etapas `realismo`, `inferencia`, `otimizacao` e
  `modelos` no pipeline oficial.

### Documentação

- [x] Glossário: Friedman e Nemenyi, teste de Dunn e teste de permutação; atualizar
  [Kruskal-Wallis](glossario/kruskal-wallis.md) e [testes para classificadores](glossario/testes-para-classificadores.md).
- [ ] [Resultados](resultados.md): os números, depois das rodadas completas.

## Como os testes aparecem nas figuras

[`ilustrar_testes.py`](../scripts/ferramentas/ilustrar_testes.py) desenha uma figura por etapa
(`reports/<etapa>/figures/testes_<etapa>.png`). Em cima, a estatística do teste sob a hipótese
nula (normal, t, χ² ou o nulo da permutação), com as caudas de α = 5% sombreadas e o valor
observado como linha vertical. Embaixo, os dados contra a curva normal: histograma, Q-Q plot e
Shapiro-Wilk, que mostram a cauda pesada e justificam os testes não paramétricos. A ressalva
vale para todas: com milhares de contas, quase tudo cai muito além da zona crítica, e por isso
o tamanho do efeito importa mais que o p.

## Referências

- Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. *JMLR*, 7, 1–30.
- Dunn, O. J. (1964). Multiple comparisons using rank sums. *Technometrics*, 6(3), 241–252.
- Romano, J. et al. (2006). Appropriate statistics for ordinal level data (limiares do delta de Cliff).
