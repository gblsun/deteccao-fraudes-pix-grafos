# Notas da pesquisa no Obsidian

O repositório inteiro funciona como um cofre (*vault*) do [Obsidian](https://obsidian.md):
os arquivos `.md` já são as notas. O Obsidian serve para **escrever e ligar** as notas
(fichamentos, diário, atas, resultados). O código continua no VS Code e no Jupyter, e o
git continua sendo o backup e o histórico.

## Abrir

1. Instale o Obsidian e escolha **Abrir pasta como cofre** (*Open folder as vault*).
2. Selecione a **raiz do repositório** (a pasta `deteccao-fraudes-pix-grafos`), e não
   `docs/`: só assim as figuras de `reports/` aparecem dentro de `docs/resultados.md`.
3. Se o Obsidian perguntar, confie no cofre (a configuração vem do repositório).

A configuração já vem pronta em `.obsidian/`:

| Ajuste | Valor | Por quê |
|--------|-------|---------|
| Formato dos links | Markdown, caminho relativo | os mesmos links funcionam no GitHub |
| Atualizar links ao mover/renomear | sim | reorganizar pastas não quebra nada |
| Pasta de anexos | `docs/anexos/` | imagens coladas nas notas não se espalham |
| Arquivos excluídos | `.venv/`, `data/`, `src/`, `.pytest_cache/` | a busca e o grafo mostram só as notas |
| Modelos | `docs/modelos/` | fichamento, reunião e diário |
| Notas diárias | `docs/diario/AAAA-MM-DD.md` | diário de pesquisa |

Se os comandos de modelos ou de nota diária não aparecerem, ative os plugins principais
**Modelos** (*Templates*) e **Notas diárias** (*Daily notes*) em Configurações →
Plugins principais.

## Rotina

| Quando | O que fazer | Onde |
|--------|-------------|------|
| terminou uma leitura | nova nota com a chave do `.bib` como nome, depois **Modelos: Inserir modelo** → `fichamento`; acrescentar uma linha no índice | `docs/leituras/`, [revisao-bibliografica.md](revisao-bibliografica.md) |
| dia de trabalho na pesquisa | **Notas diárias: Abrir a nota de hoje** (já vem com o modelo): o que rodou, o que deu errado, o que foi decidido e por quê | `docs/diario/` |
| reunião de orientação | nova nota `AAAA-MM-DD`, depois inserir o modelo `reuniao` | `docs/reunioes/` |
| saiu um resultado | ligar o resultado às leituras e decisões que o explicam | [resultados.md](resultados.md) |

O diário é o que mais ajuda no fim: na escrita do relatório (meses 11 e 12), a
justificativa de cada escolha já está registrada, com data.

Para ligar notas, digite `[` e escolha o arquivo, ou arraste o arquivo para dentro da
nota. Com a configuração acima, o link sai como `[texto](../caminho.md)`, que também
funciona no GitHub. Evite `[[wikilinks]]`, que o GitHub não entende.

## Plugins da comunidade (opcionais)

- **Tasks**: junta numa lista só os `- [ ]` espalhados pelas atas e pelo diário. Numa nota
  qualquer, escreva:

  ````markdown
  ```tasks
  not done
  path includes docs/
  ```
  ````

  No GitHub esse bloco aparece como código, o que não atrapalha.
- **Zotero Integration**: cria o fichamento a partir do Zotero, com título, autores,
  resumo e os seus destaques do PDF. Combine com o Better BibTeX para manter o
  `referencias.bib` atualizado.

Plugins e aparência ficam só na sua máquina (o `.gitignore` versiona apenas `app.json`,
`templates.json` e `daily-notes.json`).

## Regras

- **Nenhum nome de pessoa, orientador ou curso** nas notas do repositório: a proposta é
  submetida de forma anônima. Anotações pessoais com nomes ficam num cofre separado,
  fora desta pasta.
- Commits pelo VS Code ou pelo terminal, como o resto do projeto. Plugins de git
  automático não são necessários.
- Notebooks (`.ipynb`) não abrem no Obsidian: para citá-los, use um link comum para o
  arquivo.
