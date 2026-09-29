"""Download dos dados abertos do BCB, sem rede: o ``urlopen`` é substituído."""

import io
import json
from urllib.error import HTTPError, URLError

import pytest

from pixfraud import bcb


class _Resposta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _servidor(monkeypatch, falhas):
    """Faz o ``urlopen`` levantar cada erro de ``falhas`` e depois responder com uma linha."""
    urls, pendentes = [], list(falhas)

    def urlopen(url, timeout):
        urls.append(url)
        if pendentes:
            raise pendentes.pop(0)
        return _Resposta(json.dumps({"value": [{"AnoMes": 202506, "VALOR": 1.0}]}).encode())

    monkeypatch.setattr(bcb, "urlopen", urlopen)
    monkeypatch.setattr(bcb.time, "sleep", lambda s: None)
    return urls


def _http(code):
    return HTTPError("https://olinda.bcb.gov.br", code, "erro", None, None)


def test_tenta_de_novo_em_504_e_falha_de_conexao(monkeypatch):
    urls = _servidor(monkeypatch, [_http(504), URLError("sem conexão")])
    df = bcb.fetch("transacoes", "202506", filter="AnoMes eq 202506", top=10, retries=3, backoff=0)
    assert len(df) == 1 and len(urls) == 3
    assert "$filter=AnoMes%20eq%20202506" in urls[0] and "$top=10" in urls[0]


def test_desiste_depois_das_tentativas(monkeypatch):
    urls = _servidor(monkeypatch, [_http(504)] * 3)
    with pytest.raises(HTTPError):
        bcb.fetch("transacoes", "202506", retries=3, backoff=0)
    assert len(urls) == 3


def test_nao_tenta_de_novo_em_erro_definitivo(monkeypatch):
    urls = _servidor(monkeypatch, [_http(404)])
    with pytest.raises(HTTPError):
        bcb.fetch("fraudes", "202506", retries=3, backoff=0)
    assert len(urls) == 1
