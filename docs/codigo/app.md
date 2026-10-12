---
tags: [codigo]
---

# `app/explorador.py`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Guia de uso: [guia do explorador](../../app/guia-do-explorador.md) · [mapa do código](mapa-do-codigo.md)

Explorador interativo da pesquisa (Streamlit).

Rodar na raiz do repositório (só neste computador):
    streamlit run app/explorador.py --server.address localhost

Na barra lateral, escolha a **semente** (digitando ou por um atalho) e o
**cenário**, e clique em "Gerar rede": a rede é gerada na hora, com todos os
modelos pontuados (não supervisionados e supervisionados). Depois escolha o
modelo que pinta o risco e quantas contas seriam investigadas (top-k).

Abas:
    Resumo             os números da rede e o desempenho do modelo escolhido
    Rede inteira       todas as contas, com filtros, linha do tempo e o modo "Acertos" (pixfraud.explorer)
    Ranking            as contas mais suspeitas do modelo, com o gabarito
    Modelos            a AP de todos os modelos nesta rede
    Conta              ficha da conta e trilha do dinheiro (comum ou temporal)
    Padrões de fraude  gera e desenha os padrões de pixfraud.patterns
    Fluxo e bloqueio   fluxo máximo, corte mínimo e contas a bloquear (pixfraud.flow)
    Resultados         estudos com várias sementes e testes estatísticos por atributo

Com a variável de ambiente PIXFRAUD_DADOS apontando para uma pasta, o app
também oferece aquele dataset salvo (ex.: o AMLworld importado).

**Funções**

- `def network(source: str, scenario: str, seed: int, config_name: str)`: Contas, Pix e a rede preparada: gerada (semente + cenário) ou lida do dataset salvo.
- `def model_scores(source: str, scenario: str, seed: int, config_name: str, feature_set: str)`: Escores de todos os modelos e a tabela com a nota de cada um.
- `def explorer_page(source: str, scenario: str, seed: int, config_name: str, feature_set: str, model: int) -> str`: HTML da aba "Rede inteira", com todos os modelos no seletor e o escolhido já selecionado.
- `def roles_with_victims(info: pd.DataFrame) -> pd.Series`: Papel de cada conta, com as vítimas de golpe destacadas como `vitima`.
- `def with_roles(graph, roles: pd.Series)`: Cópia do grafo com o atributo `role` em cada vértice (para colorir os desenhos).
- `def network_title(source: str, scenario: str, seed: int, config_name: str) -> str`: Legenda da rede escolhida: o dataset salvo ou semente, cenário e hiperparâmetros.
- `def brl(value: float) -> str`: Valor em reais sem centavos, com ponto de milhar.
- `def br(value: float, digits: int=0) -> str`: Número no formato brasileiro (ponto de milhar e vírgula decimal).
- `def use_shortcut()`: Põe na semente o atalho escolhido na barra lateral.
- `def roll_dice()`: Sorteia uma semente nova (o botão do dado).
