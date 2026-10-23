"""Regras de validação do CAR — as mesmas do ValidadorImovel do back-end, com uma diferença:
geometria inválida vai para a quarentena em vez de ser corrigida em silêncio (decisão D11).

Isto é provisório: quando o pkg_qualidade (Tarefa 2) estiver pronto, a validação passa para
o Oracle e este módulo deixa de ser usado.
"""

import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import pandas as pd
import shapely
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity

# Nomes das colunas no .dbf do CAR (a busca ignora maiúsculas/minúsculas)
COLUNA_COD_IMOVEL = "cod_imovel"
COLUNA_MUNICIPIO = "municipio"
COLUNA_AREA = "num_area"
COLUNA_SITUACAO = "ind_status"


@dataclass
class Resultado:
    linha: int
    atributos: dict
    cod_imovel: str | None = None
    municipio: str | None = None
    area_ha: Decimal | None = None
    situacao: str | None = None
    geometria: BaseGeometry | None = None
    campo: str | None = None
    motivo: str | None = None

    @property
    def aprovado(self) -> bool:
        return self.motivo is None

    @property
    def estado(self) -> str | None:
        """UF pelo prefixo do código do CAR: "PR-4113700-..." → "PR"."""
        cod = self.cod_imovel
        if cod and len(cod) > 3 and cod[2] == "-":
            return cod[:2].upper()
        return None

    def payload_json(self) -> str:
        """As colunas do .dbf, sem a geometria (que pode ter milhares de pontos)."""
        return json.dumps(self.atributos, ensure_ascii=False, default=str)


class ValidadorImovel:
    """Valida os imóveis de UM arquivo. Guarda os códigos já vistos para achar duplicados,
    então crie uma instância nova para cada arquivo processado."""

    def __init__(self) -> None:
        self._codigos_vistos: set[str] = set()

    def validar(self, linha: int, atributos: dict, geometria: BaseGeometry | None) -> Resultado:
        colunas = {nome.lower(): nome for nome in atributos}
        r = Resultado(
            linha=linha,
            atributos={k: _valor_json(v) for k, v in atributos.items()},
            cod_imovel=_texto(atributos.get(colunas.get(COLUNA_COD_IMOVEL, ""))),
            municipio=_texto(atributos.get(colunas.get(COLUNA_MUNICIPIO, ""))),
            area_ha=_numero(atributos.get(colunas.get(COLUNA_AREA, ""))),
            situacao=_texto(atributos.get(colunas.get(COLUNA_SITUACAO, ""))),
        )

        if not r.cod_imovel:
            return _reprovar(r, "cod_imovel", "cod_imovel vazio")
        # Igual ao back-end hoje: a primeira ocorrência passa e as seguintes vão para a quarentena.
        # A regra definitiva (todas as repetições na quarentena) chega com o pkg_qualidade.
        if r.cod_imovel in self._codigos_vistos:
            return _reprovar(r, "cod_imovel", "cod_imovel duplicado")
        self._codigos_vistos.add(r.cod_imovel)

        if geometria is None or geometria.is_empty:
            return _reprovar(r, "geometria", "sem geometria")
        if geometria.geom_type not in ("Polygon", "MultiPolygon"):
            return _reprovar(r, "geometria", f"geometria não é polígono ({geometria.geom_type})")
        if not geometria.is_valid:
            # Não corrige: quem decide é o operador, na quarentena.
            return _reprovar(r, "geometria", f"geometria inválida: {explain_validity(geometria)}")

        # O Oracle exige o anel externo no sentido anti-horário; o shapefile guarda horário.
        r.geometria = shapely.orient_polygons(geometria, exterior_cw=False)
        return r


def _reprovar(r: Resultado, campo: str, motivo: str) -> Resultado:
    r.campo = campo
    r.motivo = motivo
    return r


def _vazio(valor) -> bool:
    """None, NaN, NaT e pd.NA: as formas de "vazio" que o pandas devolve."""
    try:
        return bool(pd.isna(valor))
    except (TypeError, ValueError):
        return False


def _texto(valor) -> str | None:
    if _vazio(valor):
        return None
    texto = str(valor).strip()
    return texto or None


def _numero(valor) -> Decimal | None:
    if _vazio(valor):
        return None
    try:
        return Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        return None


def _valor_json(valor):
    """Converte os tipos do pandas/numpy para algo que vira JSON."""
    if _vazio(valor):
        return None
    if hasattr(valor, "item"):  # numpy.int64, numpy.float64...
        return valor.item()
    return valor
