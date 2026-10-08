"""O espaço de busca: quais valores de cada hiperparâmetro testar, e como ampliá-lo.

As grades ficam em ``configs/busca_hiperparametros.yaml``. Cada hiperparâmetro
é um ``Param``: a lista de valores testados e, se numérico, os limites. Quando
o vencedor cai numa ponta da lista, ``expand`` acrescenta um valor além dela
(ver ``Param.beyond``).
"""

from __future__ import annotations

import inspect
import itertools
import json
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from pixfraud.models import DETECTORS, FACTORIES, GRAPH_DETECTORS, SUPERVISED

DEFAULT_PATH = Path("configs/busca_hiperparametros.yaml")


@dataclass(frozen=True)
class Param:
    """Os valores testados de um hiperparâmetro e, se ele puder crescer, os limites."""

    values: tuple
    low: float | None = None  # sem limites, a lista é fixa
    high: float | None = None
    integer: bool = False

    @property
    def expandable(self) -> bool:
        return self.low is not None and self.high is not None

    def numeric(self) -> list[float]:
        """Os valores numéricos testados, em ordem (``None``, textos e booleanos ficam de fora)."""
        return sorted(v for v in self.values if isinstance(v, (int, float)) and not isinstance(v, bool))

    def beyond(self, value) -> object | None:
        """Um valor além de ``value``, se ele for a ponta da lista; ``None`` se não houver para onde ir.

        O passo é o multiplicativo entre a ponta e o valor vizinho (ex.: 20, 40 ->
        80; 0,03, 0,01 -> 0,0033), cortado nos limites. Valores inteiros andam
        pelo menos 1.
        """
        numbers = self.numeric()
        if not self.expandable or len(numbers) < 2 or value not in numbers:
            return None
        if value == numbers[-1]:
            new = value * value / numbers[-2] if numbers[-2] > 0 else value + (value - numbers[-2])
            new = min(new, self.high)
            new = max(round(new), value + 1) if self.integer else new
            return new if new > value and new <= self.high else None
        if value == numbers[0]:
            new = value * value / numbers[1] if value > 0 else value - (numbers[1] - value)
            new = max(new, self.low)
            new = min(round(new), value - 1) if self.integer else new
            return new if new < value and new >= self.low else None
        return None

    def with_value(self, value) -> Param:
        return replace(self, values=(*self.values, _tidy(value)))


def _tidy(value):
    """Arredonda floats a 4 algarismos significativos, para os valores gravados ficarem legíveis."""
    return float(f"{value:.4g}") if isinstance(value, float) else value


def load_search_spaces(path: str | Path = DEFAULT_PATH) -> dict[str, dict[str, Param]]:
    """Lê as grades do YAML: ``{modelo: {hiperparâmetro: Param}}``."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    spaces = {}
    for model, params in raw.items():
        model_function(model)  # falha cedo se o nome do modelo estiver errado
        spaces[model] = {}
        for name, spec in params.items():
            if isinstance(spec, dict):
                spaces[model][name] = Param(tuple(spec["valores"]), spec.get("min"), spec.get("max"),
                                            bool(spec.get("inteiro", False)))
            else:
                spaces[model][name] = Param(tuple(spec))
    return spaces


def model_function(model: str):
    """A função de ``model`` num dos registros de ``pixfraud.models``."""
    for registry in (DETECTORS, GRAPH_DETECTORS, SUPERVISED):
        if model in registry:
            return registry[model]
    raise ValueError(f"modelo desconhecido: {model}")


def full_params(model: str, current: dict, space: dict | None = None) -> dict:
    """``current`` completado com o valor padrão de cada hiperparâmetro de ``space``.

    Assim a configuração atual é reconhecida quando a grade testa o mesmo valor
    (ex.: ``method="mean"`` do kNN, que a configuração não escreve). Os
    supervisionados recebem os hiperparâmetros pela fábrica do classificador.
    """
    function = FACTORIES.get(model) or model_function(model)
    signature = inspect.signature(function).parameters
    names = space if space is not None else signature
    defaults = {k: signature[k].default for k in names
                if k in signature and signature[k].default is not inspect.Parameter.empty}
    return {**defaults, **current}


def grid(space: dict) -> list[dict]:
    """Todas as combinações de ``space`` (``{hiperparâmetro: Param ou lista de valores}``)."""
    keys = list(space)
    values = [space[k].values if isinstance(space[k], Param) else space[k] for k in keys]
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def candidates(model: str, current: dict, space: dict) -> list[dict]:
    """A configuração atual (primeiro) e cada combinação da grade aplicada sobre ela, sem repetir."""
    current = full_params(model, current, space)
    found, seen = [], set()
    for change in [{}, *grid(space)]:
        params = {**current, **change}
        key = params_key(params)
        if key not in seen:
            seen.add(key)
            found.append(params)
    return found


def params_key(params: dict) -> str:
    """Texto estável de um conjunto de hiperparâmetros (para agrupar e gravar em CSV)."""
    return json.dumps(params, sort_keys=True, default=str)


def expand(space: dict[str, Param], chosen: dict) -> tuple[dict[str, Param], list[str]]:
    """Amplia ``space`` onde o vencedor ``chosen`` caiu numa ponta da lista.

    Devolve o espaço novo e a descrição do que mudou (vazia se nada mudou, e aí
    a busca daquele modelo terminou).
    """
    new_space, changes = dict(space), []
    for name, param in space.items():
        value = param.beyond(chosen.get(name))
        if value is not None and _tidy(value) not in param.values:
            new_space[name] = param.with_value(value)
            changes.append(f"{name}: {chosen.get(name)} -> testa {_tidy(value)}")
    return new_space, changes
