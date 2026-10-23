"""Conversão de polígonos do shapely para SDO_GEOMETRY do Oracle.

Por que não mandar WKB e converter no banco (como o Java faz com SDO_GEOMETRY(blob, srid)):
o python-oracledb em modo thin envia bytes como RAW, que tem limite de 32 KB, e os imóveis
grandes do CAR passam disso. Montar o objeto aqui não tem limite de tamanho e é rápido
(~2 s para 5 mil polígonos, testado contra o Oracle 23ai).

O sentido dos anéis tem que estar certo antes (anel externo anti-horário, buracos horário):
validacao.py já faz isso com shapely.orient_polygons.
"""

import shapely
from shapely.geometry.base import BaseGeometry

SRID_BANCO = 4326

GTYPE_POLIGONO = 2003       # 2 = duas dimensões, 003 = polígono
GTYPE_MULTIPOLIGONO = 2007  # 007 = multipolígono
ETYPE_ANEL_EXTERNO = 1003
ETYPE_BURACO = 2003
INTERPRETACAO_RETAS = 1     # vértices ligados por segmentos de reta


def elementos(geometria: BaseGeometry) -> tuple[int, list[int], list[float]]:
    """(SDO_GTYPE, SDO_ELEM_INFO, SDO_ORDINATES) de um Polygon ou MultiPolygon.

    Cada anel vira um trio no ELEM_INFO: (posição do primeiro valor em ORDINATES, tipo, 1).
    ORDINATES é a lista corrida x1, y1, x2, y2... de todos os anéis.
    """
    if geometria.geom_type == "Polygon":
        poligonos, gtype = [geometria], GTYPE_POLIGONO
    elif geometria.geom_type == "MultiPolygon":
        poligonos, gtype = list(geometria.geoms), GTYPE_MULTIPOLIGONO
    else:
        raise ValueError(f"Só polígonos são convertidos, veio {geometria.geom_type}")

    elem_info: list[int] = []
    ordenadas: list[float] = []
    for poligono in poligonos:
        for indice, anel in enumerate([poligono.exterior, *poligono.interiors]):
            tipo = ETYPE_ANEL_EXTERNO if indice == 0 else ETYPE_BURACO
            elem_info += [len(ordenadas) + 1, tipo, INTERPRETACAO_RETAS]
            ordenadas += shapely.get_coordinates(anel).ravel().tolist()
    return gtype, elem_info, ordenadas


class TiposSdo:
    """Os tipos de objeto do Oracle Spatial, carregados uma vez por lote."""

    def __init__(self, con) -> None:
        self.geometria = con.gettype("MDSYS.SDO_GEOMETRY")
        self._elem_info = con.gettype("MDSYS.SDO_ELEM_INFO_ARRAY")
        self._ordenadas = con.gettype("MDSYS.SDO_ORDINATE_ARRAY")

    def converter(self, geometria: BaseGeometry, srid: int):
        gtype, elem_info, ordenadas = elementos(geometria)
        objeto = self.geometria.newobject()
        objeto.SDO_GTYPE = gtype
        objeto.SDO_SRID = srid
        objeto.SDO_ELEM_INFO = self._elem_info.newobject(elem_info)
        objeto.SDO_ORDINATES = self._ordenadas.newobject(ordenadas)
        return objeto
