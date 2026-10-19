"""Regras do CAR, sem banco e sem Airflow.

Rodar (dentro da imagem, que já tem as bibliotecas):
    docker compose -f docker-compose.local.yaml --env-file .env.local run --rm \
        -v ./tests:/opt/airflow/tests airflow bash -c "pip install -q pytest && pytest -q /opt/airflow/tests"
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
from shapely.geometry import MultiPolygon, Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dags"))

from georural.validacao import ValidadorImovel  # noqa: E402

# Quadrado no sentido horário, como o shapefile guarda
QUADRADO_HORARIO = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
# "Gravata": a borda cruza a si mesma
GRAVATA = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])


def atributos(cod="PR-4106902-ABC", **extras):
    base = {"COD_IMOVEL": cod, "municipio": "Curitiba", "NUM_AREA": 12.5, "ind_status": "AT"}
    base.update(extras)
    return base


def test_aprova_e_le_colunas_ignorando_maiusculas():
    r = ValidadorImovel().validar(1, atributos(), QUADRADO_HORARIO)
    assert r.aprovado
    assert r.cod_imovel == "PR-4106902-ABC"
    assert r.municipio == "Curitiba"
    assert r.area_ha == Decimal("12.5")
    assert r.situacao == "AT"
    assert r.estado == "PR"


def test_orienta_anel_externo_anti_horario_para_o_oracle():
    r = ValidadorImovel().validar(1, atributos(), QUADRADO_HORARIO)
    assert r.geometria.exterior.is_ccw


def test_orienta_cada_poligono_do_multipolygon():
    multi = MultiPolygon([QUADRADO_HORARIO, Polygon([(2, 0), (2, 1), (3, 1), (3, 0), (2, 0)])])
    r = ValidadorImovel().validar(1, atributos(), multi)
    assert all(p.exterior.is_ccw for p in r.geometria.geoms)


def test_cod_vazio_vai_para_quarentena():
    r = ValidadorImovel().validar(1, atributos(cod="   "), QUADRADO_HORARIO)
    assert not r.aprovado
    assert (r.campo, r.motivo) == ("cod_imovel", "cod_imovel vazio")


def test_duplicado_primeiro_passa_e_o_segundo_vai_para_quarentena():
    v = ValidadorImovel()
    assert v.validar(1, atributos(), QUADRADO_HORARIO).aprovado
    segundo = v.validar(2, atributos(), QUADRADO_HORARIO)
    assert segundo.motivo == "cod_imovel duplicado"


def test_sem_geometria():
    r = ValidadorImovel().validar(1, atributos(), None)
    assert (r.campo, r.motivo) == ("geometria", "sem geometria")


def test_geometria_que_nao_e_poligono():
    r = ValidadorImovel().validar(1, atributos(), Point(0, 0))
    assert r.motivo.startswith("geometria não é polígono")


def test_geometria_invalida_vai_para_quarentena_sem_correcao():
    r = ValidadorImovel().validar(1, atributos(), GRAVATA)
    assert not r.aprovado
    assert r.motivo.startswith("geometria inválida: Self-intersection")
    assert r.geometria is None


def test_area_com_virgula_e_area_invalida():
    assert ValidadorImovel().validar(1, atributos(NUM_AREA="8,8"), QUADRADO_HORARIO).area_ha == Decimal("8.8")
    assert ValidadorImovel().validar(1, atributos(NUM_AREA="oito"), QUADRADO_HORARIO).area_ha is None


def test_payload_vira_json_com_tipos_do_numpy_e_vazios():
    r = ValidadorImovel().validar(7, atributos(NUM_AREA=np.float64("nan"), extra=np.int64(3)), QUADRADO_HORARIO)
    payload = json.loads(r.payload_json())
    assert payload["NUM_AREA"] is None
    assert payload["extra"] == 3
