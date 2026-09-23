---
tags: [glossario]
---

# Teste de Wilcoxon pareado

Compara duas abordagens avaliadas **nas mesmas condições** (aqui: a mesma semente, o mesmo
dataset), olhando só o sinal e a ordem das diferenças.

**Por que pareado.** A diferença entre dois datasets é muito maior que a diferença entre
dois detectores. Comparando na mesma semente, o que sobra é o efeito da abordagem.

**Limite prático.** Com $n$ sementes, o menor p-valor possível é $2/2^n$: com 10 sementes,
$\approx 0{,}002$; depois da [correção de Holm](correcao-de-holm.md) para 10 comparações,
$\approx 0{,}02$. Ou seja, "p = 0,02" nos nossos resultados quer dizer **todas as sementes
apontaram para o mesmo lado**. Com 3 sementes, o menor p possível é 0,25: nada pode ser
significativo, e por isso a seção de detecção a tempo é descritiva.

**No projeto.** [`stats.paired_comparison`](../../src/pixfraud/stats.py) e
[`stats.compare_runs`](../../src/pixfraud/stats.py); colunas `p Wilcoxon` e
`a vence em` dos arquivos `*_comparacoes.csv`.
