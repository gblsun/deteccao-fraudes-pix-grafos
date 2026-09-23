---
tags: [mapa]
---

# Relatório final

Esqueleto do relatório científico da iniciação científica, escrito em Markdown (um arquivo
por capítulo) e convertido para DOCX, HTML ou PDF pelo [Pandoc](https://pandoc.org), com
as citações de [`docs/referencias.bib`](../docs/referencias.bib) no estilo ABNT.

```powershell
pip install -e ".[relatorio]"            # traz o Pandoc dentro do .venv; nada a instalar no sistema
python scripts/gerar_relatorio.py        # relatorio/saida/relatorio.docx
python scripts/gerar_relatorio.py --formato html
```

O PDF (`--formato pdf`) precisa de uma instalação de LaTeX; o DOCX abre no Word e pode ser
ajustado ao modelo exigido pela instituição.

## Estrutura

| Arquivo | Estado |
|---------|--------|
| [`capitulos/00_resumo.md`](capitulos/00_resumo.md) | roteiro: escrever por último |
| [`capitulos/01_introducao.md`](capitulos/01_introducao.md) | roteiro de tópicos |
| [`capitulos/02_fundamentacao.md`](capitulos/02_fundamentacao.md) | roteiro de tópicos, com as leituras de apoio |
| [`capitulos/03_metodologia.md`](capitulos/03_metodologia.md) | **rascunho** tirado do código: reescrever com suas palavras |
| [`capitulos/04_resultados.md`](capitulos/04_resultados.md) | **rascunho** tirado de `docs/resultados.md`: reescrever e escolher o que entra |
| [`capitulos/05_conclusao.md`](capitulos/05_conclusao.md) | roteiro de tópicos |
| [`metadados.yaml`](metadados.yaml) | título, idioma e opções do documento |
| [`abnt.csl`](abnt.csl) | estilo de citação ABNT ([Citation Style Language](https://citationstyles.org), licença CC BY-SA 3.0) |

## Como escrever

- Cite pela chave do `.bib`: `[@liu2008isolation]` vira "(LIU; TING; ZHOU, 2008)", e
  `@liu2008isolation` sem colchetes vira "Liu, Ting e Zhou (2008)". As referências usadas
  aparecem sozinhas no fim.
- Figuras: `![Legenda](../../reports/figures/arquivo.png)`, com o caminho relativo ao
  capítulo. Assim elas também aparecem no GitHub e no Obsidian.
- Os rascunhos existem para não começar da página em branco: o texto final é seu.
- **Sem nomes** de autor, orientador ou curso no repositório: acrescente esses dados só no
  arquivo final gerado, que fica fora do git (`relatorio/saida/`).
