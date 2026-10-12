---
tags: [codigo]
---

# `pixfraud.bcb`

> Nota gerada por [`documentar_codigo.py`](../../scripts/ferramentas/documentar_codigo.py) a partir das docstrings. Não edite à mão: mude a docstring no código e rode o script de novo.

Arquivo: [`src/pixfraud/bcb.py`](../../src/pixfraud/bcb.py) · [mapa do código](mapa-do-codigo.md)

Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil.

Os dados são agregados (não há transações individuais), então não servem para
montar o grafo diretamente. São úteis para calibrar o gerador sintético (valor
médio por transação, proporção PF/PJ, faixa etária, região, natureza P2P/P2B)
e para dimensionar as fraudes reais (contestações, devoluções pelo MED,
bloqueios cautelares, usuários e chaves com marcação de fraude).

API OData: https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/

## Classes e funções

### `fetch` (função)

```python
def fetch(resource: str, database: str, filter: str | None=None, top: int | None=None, timeout: float=300, retries: int=3, backoff: float=30) -> pd.DataFrame
```

Baixa um recurso da API em uma única requisição.

`resource` é um apelido de `RESOURCES`; `database` é o parâmetro
obrigatório do recurso, no formato `AAAAMM` (ou `AAAA-MM-DD` para
`chaves`). Na prática a API devolve todos os meses disponíveis, então
use `filter` (expressão OData, ex.: `"AnoMes eq 202506"` ou
`"NATUREZA eq 'P2P'"`) para limitar o volume. A API não aceita
`$skip`, por isso não há paginação; `top` limita o nº de linhas.
Sem filtro, `transacoes` passa de 50 MB.

Erros passageiros do servidor (502, 503, 504) e falhas de conexão são tentados
de novo até `retries` vezes no total, esperando `backoff` segundos antes da
2ª tentativa e o dobro a cada nova. O 504 é comum em `transacoes`: o gateway
do BCB desiste antes de o servidor montar a resposta (ver data/README.md).

## Quem usa este módulo

- [`scripts/01_dados/baixar_dados_bcb.py`](scripts.01_dados.md)
- [`tests/test_bcb.py`](testes.md)
