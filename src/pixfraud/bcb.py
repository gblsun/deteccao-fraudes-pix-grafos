"""Acesso aos dados abertos do PIX publicados pelo Banco Central do Brasil.

Os dados são agregados (não há transações individuais), então não servem para
montar o grafo diretamente. São úteis para calibrar o gerador sintético (valor
médio por transação, proporção PF/PJ, faixa etária, região, natureza P2P/P2B)
e para dimensionar as fraudes reais (contestações, devoluções pelo MED,
bloqueios cautelares, usuários e chaves com marcação de fraude).

API OData: https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/
"""

from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

import pandas as pd

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata"

# apelido -> (recurso da API, nome do parâmetro obrigatório)
RESOURCES = {
    "transacoes": ("EstatisticasTransacoesPix", "Database"),
    "fraudes": ("EstatisticasFraudesPix", "Database"),
    "municipios": ("TransacoesPixPorMunicipio", "DataBase"),
    "cnae": ("CnaePorteRecebedor", "Database"),
    "chaves": ("ChavesPix", "Data"),
}


def fetch(
    resource: str,
    database: str,
    filter: str | None = None,
    top: int | None = None,
    timeout: float = 300,
    retries: int = 3,
    backoff: float = 30,
) -> pd.DataFrame:
    """Baixa um recurso da API em uma única requisição.

    ``resource`` é um apelido de ``RESOURCES``; ``database`` é o parâmetro
    obrigatório do recurso, no formato ``AAAAMM`` (ou ``AAAA-MM-DD`` para
    ``chaves``). Na prática a API devolve todos os meses disponíveis, então
    use ``filter`` (expressão OData, ex.: ``"AnoMes eq 202506"`` ou
    ``"NATUREZA eq 'P2P'"``) para limitar o volume. A API não aceita
    ``$skip``, por isso não há paginação; ``top`` limita o nº de linhas.
    Sem filtro, ``transacoes`` passa de 50 MB.

    Erros passageiros do servidor (502, 503, 504) e falhas de conexão são tentados
    de novo até ``retries`` vezes no total, esperando ``backoff`` segundos antes da
    2ª tentativa e o dobro a cada nova. O 504 é comum em ``transacoes``: o gateway
    do BCB desiste antes de o servidor montar a resposta (ver data/README.md).
    """
    name, param = RESOURCES[resource]
    query = {f"@{param}": f"'{database}'", "$format": "json"}
    if filter:
        query["$filter"] = filter
    if top is not None:
        query["$top"] = top
    query_string = urlencode(query, safe="$@'", quote_via=quote)
    url = f"{BASE_URL}/{name}({param}=@{param})?{query_string}"
    for attempt in range(1, retries + 1):
        try:
            with urlopen(url, timeout=timeout) as response:
                return pd.DataFrame(json.load(response)["value"])
        except (HTTPError, URLError, TimeoutError) as error:
            transient = not isinstance(error, HTTPError) or error.code in (502, 503, 504)
            if not transient or attempt == retries:
                raise
            wait = backoff * 2 ** (attempt - 1)
            print(f"tentativa {attempt} de {retries} falhou ({error}); nova tentativa em {wait:.0f} s")
            time.sleep(wait)
