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

import pandas as pd  # noqa: E402

from georural.validacao import ValidadorImovel, planejar_desempate  # noqa: E402

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


def test_cada_motivo_tem_o_codigo_da_v10():
    v = ValidadorImovel()
    casos = [
        (v.validar(1, atributos(cod=""), QUADRADO_HORARIO), "CAMPO_OBRIGATORIO_AUSENTE"),
        (v.validar(2, atributos(cod="PR-1"), QUADRADO_HORARIO), None),  # primeira ocorrência passa
        (v.validar(3, atributos(cod="PR-1"), QUADRADO_HORARIO), "CHAVE_NATURAL_DUPLICADA"),
        (v.validar(4, atributos(cod="PR-2"), None), "GEOMETRIA_NULA"),
        (v.validar(5, atributos(cod="PR-3"), Point(0, 0)), "GEOMETRIA_TIPO_INCOMPATIVEL"),
        (v.validar(6, atributos(cod="PR-4"), GRAVATA), "GEOMETRIA_INVALIDA"),
    ]
    assert [r.tipo_erro for r, _ in casos] == [codigo for _, codigo in casos]


def test_reprovado_guarda_a_geometria_como_chegou_e_o_valor_que_reprovou():
    v = ValidadorImovel()
    v.validar(1, atributos(cod="PR-1"), QUADRADO_HORARIO)
    duplicado = v.validar(2, atributos(cod="PR-1"), QUADRADO_HORARIO)
    invalida = v.validar(3, atributos(cod="PR-2"), GRAVATA)

    assert duplicado.geometria is None  # só aprovado tem a geometria pronta para o MERGE
    assert duplicado.geometria_recebida.equals(QUADRADO_HORARIO)
    assert duplicado.valor_recebido == "PR-1"
    assert invalida.geometria_recebida.equals(GRAVATA)
    assert invalida.valor_recebido is None


# ----- código repetido: desempate --------------------------------------------------------

def _validar_arquivo(linhas):
    """Simula a DAG: planeja pelo arquivo inteiro e depois valida linha a linha, na ordem.
    Cada linha: (código, situação, área, data de atualização)."""
    plano = planejar_desempate(pd.DataFrame([
        {"cod_imovel": cod, "ind_status": sit, "num_area": area, "dat_atuali": data, "dat_criaca": "01/01/2015"}
        for cod, sit, area, data in linhas
    ]))
    v = ValidadorImovel(plano)
    return [v.validar(i, atributos(cod=cod, ind_status=sit, NUM_AREA=area), QUADRADO_HORARIO)
            for i, (cod, sit, area, _) in enumerate(linhas, start=1)]


def test_plano_so_tem_os_codigos_repetidos():
    plano = planejar_desempate(pd.DataFrame([
        {"cod_imovel": "PR-1", "ind_status": "CA", "num_area": 10, "dat_atuali": "01/01/2026"},
        {"cod_imovel": "PR-2", "ind_status": "AT", "num_area": 10, "dat_atuali": "01/01/2026"},
        {"cod_imovel": "PR-1", "ind_status": "AT", "num_area": 10, "dat_atuali": "01/01/2020"},
    ]))
    assert list(plano) == ["PR-1"]
    assert plano["PR-1"].vencedora == 2


def test_ativo_vence_qualquer_situacao_mesmo_mais_antigo_e_depois_no_arquivo():
    cancelado, ativo, pendente = _validar_arquivo([
        ("PR-1", "CA", 10, "01/06/2026"), ("PR-1", "AT", 10, "01/01/2020"), ("PR-1", "PE", 12, "01/07/2026")])
    assert ativo.aprovado
    for r in (cancelado, pendente):
        assert r.descartado_automaticamente
        assert r.motivo.startswith("cod_imovel duplicado: existe versão ativa")
        assert r.tipo_erro == "CHAVE_NATURAL_DUPLICADA"
    assert "esta estava PE" in pendente.justificativa


def test_copia_identica_sai_sozinha():
    primeiro, copia = _validar_arquivo([("PR-1", "AT", 10, "01/01/2026"), ("PR-1", "AT", 10, "01/01/2026")])
    assert primeiro.aprovado
    assert copia.descartado_automaticamente and "cópia idêntica" in copia.motivo


def test_mesma_situacao_com_area_diferente_fica_para_o_operador():
    primeiro, outro = _validar_arquivo([("PR-1", "CA", 10, "01/01/2026"), ("PR-1", "CA", 99, "01/01/2025")])
    assert primeiro.aprovado
    assert not outro.aprovado and not outro.descartado_automaticamente
    assert outro.motivo == "cod_imovel duplicado"


def test_sem_ativo_vence_o_mais_recente_mesmo_vindo_depois():
    antigo, recente = _validar_arquivo([("PR-1", "PE", 10, "25/06/2025"), ("PR-1", "CA", 10, "07/08/2026")])
    assert recente.aprovado
    assert antigo.descartado_automaticamente
    assert antigo.motivo.startswith("cod_imovel duplicado: versão mais antiga")
    assert "atualizada em 25/06/2025 (PE)" in antigo.justificativa
    assert "atualizada em 07/08/2026 (CA)" in antigo.justificativa


def test_mesma_data_o_cancelado_perde_mesmo_vindo_antes():
    cancelado, pendente, outro_cancelado = _validar_arquivo([
        ("PR-1", "CA", 10, "24/08/2026"), ("PR-1", "PE", 10, "24/08/2026"), ("PR-1", "CA", 10, "24/08/2026")])
    assert pendente.aprovado
    for r in (cancelado, outro_cancelado):
        assert r.descartado_automaticamente
        assert r.motivo.startswith("cod_imovel duplicado: versão cancelada (CA) com a mesma data")
        assert "perde para a PE" in r.justificativa


def test_situacoes_diferentes_sem_cancelado_e_mesmas_datas_ficam_pendentes():
    primeiro, outro = _validar_arquivo([("PR-1", "PE", 10, "01/01/2026"), ("PR-1", "SU", 10, "01/01/2026")])
    assert primeiro.aprovado
    assert not outro.descartado_automaticamente


def test_data_ilegivel_conta_como_a_mais_antiga():
    sem_data, com_data = _validar_arquivo([("PR-1", "PE", 10, "não informada"), ("PR-1", "CA", 10, "01/01/2026")])
    assert com_data.aprovado
    assert sem_data.descartado_automaticamente
