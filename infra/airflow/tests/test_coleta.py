"""Coleta paginada contra serviços falsos: sem rede, sem banco."""

import hashlib
import json
import zipfile
from urllib.parse import parse_qsl, urlsplit

import pytest

from georural import coleta

ARCGIS = "https://geo.exemplo.gov.br/server/rest/services/focos/FeatureServer/0/query?where=1=1&outFields=*&f=geojson&outSR=4674"
WFS = ("https://geoserver.exemplo.gov.br/geoserver/sicar/wfs?service=WFS&version=2.0.0&request=GetFeature"
       "&typeNames=sicar:imoveis&outputFormat=application/json&count=10000")


def _feicao(i: int, prefixo: str = "") -> dict:
    return {"type": "Feature", "id": f"{prefixo}{i}", "properties": {"objectid": i},
            "geometry": {"type": "Point", "coordinates": [-51.0, -25.0]}}


class ServidorFalso(coleta.ClienteHttp):
    """Responde como um ArcGIS ou um GeoServer com `total` registros."""

    def __init__(self, total: int, limite: int = 2000, falha_acima: int | None = None,
                 repete_pagina: bool = False, prefixo: str = ""):
        self.total = total
        self.limite = limite
        self.falha_acima = falha_acima
        self.repete_pagina = repete_pagina
        self.prefixo = prefixo
        self.pedidos: list[dict] = []

    def texto(self, url: str) -> bytes:
        p = {k.lower(): v for k, v in parse_qsl(urlsplit(url).query)}
        self.pedidos.append(p)
        if url.split("?")[0].endswith("/FeatureServer/0"):
            return json.dumps({"maxRecordCount": self.limite, "objectIdField": "OBJECTID",
                               "advancedQueryCapabilities": {"supportsPagination": True}}).encode()
        if p.get("returncountonly") == "true":
            return json.dumps({"count": self.total}).encode()
        if p.get("resulttype") == "hits":
            return f'<wfs:FeatureCollection numberMatched="{self.total}" numberReturned="0"/>'.encode()

        inicio = int(p.get("resultoffset", p.get("startindex", 0)))
        pedido = int(p.get("resultrecordcount", p.get("count", 0)))
        if self.falha_acima and pedido > self.falha_acima:
            raise coleta._ErroDoServidor("HTTP 500")
        if self.repete_pagina and inicio > 0:
            inicio -= 1  # ordem instável: devolve um registro da página anterior
        fim = min(self.total, inicio + min(pedido, self.limite))
        return json.dumps({"type": "FeatureCollection",
                           "features": [_feicao(i, self.prefixo) for i in range(inicio, fim)]}).encode()


def _ids(caminho) -> list:
    with zipfile.ZipFile(caminho) as z:
        partes = sorted(n for n in z.namelist() if n.startswith("parte-"))
        return [f["id"] for n in partes for f in json.loads(z.read(n))["features"]]


def test_tipo_pela_url():
    assert coleta.tipo(ARCGIS) == coleta.TIPO_ARCGIS
    assert coleta.tipo(WFS) == coleta.TIPO_WFS
    assert coleta.tipo("https://x.gov.br/dados/focos.csv") == coleta.TIPO_ARQUIVO


def test_arcgis_coleta_tudo_ordenado_pelo_objectid(tmp_path):
    servidor = ServidorFalso(total=4500)

    r = coleta.coletar(ARCGIS, tmp_path, "FOCOS-IAT", cliente=servidor, pausa=0)

    assert (r.total, r.coletados, r.paginas) == (4500, 4500, 3)
    assert _ids(r.caminho) == [str(i) for i in range(4500)]
    paginas = [p for p in servidor.pedidos if "resultoffset" in p]
    assert [p["resultoffset"] for p in paginas] == ["0", "2000", "4000"]
    assert all(p["orderbyfields"] == "OBJECTID" and p["f"] == "geojson" and p["outsr"] == "4674" for p in paginas)


def test_wfs_remove_a_paginacao_do_link_e_ordena_pela_chave(tmp_path):
    servidor = ServidorFalso(total=12000, limite=10000, prefixo="imoveis.")

    r = coleta.coletar(WFS, tmp_path, "CAR-WFS", chaves=["cod_imovel"], cliente=servidor, pausa=0)

    assert r.coletados == 12000
    paginas = [p for p in servidor.pedidos if "startindex" in p]
    assert [p["startindex"] for p in paginas] == ["0", "5000", "10000"]
    assert all(p["count"] == "5000" and p["sortby"] == "cod_imovel" for p in paginas)
    hits = next(p for p in servidor.pedidos if p.get("resulttype") == "hits")
    assert "outputformat" not in hits  # o total vem no XML


def test_servidor_que_entrega_menos_que_o_pedido(tmp_path):
    servidor = ServidorFalso(total=2500, limite=1000, prefixo="x.")

    r = coleta.coletar(WFS, tmp_path, "W", cliente=servidor, pausa=0)

    assert (r.coletados, r.paginas) == (2500, 3)


def test_pagina_com_erro_500_e_dividida(tmp_path):
    servidor = ServidorFalso(total=3000, falha_acima=600)

    r = coleta.coletar(ARCGIS, tmp_path, "F", cliente=servidor, pausa=0)

    assert r.coletados == 3000
    tamanhos = [int(p["resultrecordcount"]) for p in servidor.pedidos if "resultrecordcount" in p]
    assert tamanhos[:3] == [2000, 1000, 500]


def test_falta_registro_falha_com_vieram_x_de_y(tmp_path):
    class Encolhe(ServidorFalso):
        """Diz que tem 5.000, mas só entrega 4.000 (e continua dizendo 5.000)."""
        def texto(self, url):
            if "resultOffset=4000" in url:
                return json.dumps({"type": "FeatureCollection", "features": []}).encode()
            return super().texto(url)

    with pytest.raises(coleta.ColetaFalhou, match="Vieram 4.000 de 5.000"):
        coleta.coletar(ARCGIS, tmp_path, "F", cliente=Encolhe(total=5000), pausa=0)


def test_registro_repetido_entre_paginas_falha(tmp_path):
    with pytest.raises(coleta.ColetaFalhou, match="repetidos"):
        coleta.coletar(ARCGIS, tmp_path, "F", cliente=ServidorFalso(total=4000, repete_pagina=True), pausa=0)


def test_zip_deterministico(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    a = coleta.coletar(ARCGIS, tmp_path / "a", "F", cliente=ServidorFalso(total=2100), pausa=0)
    b = coleta.coletar(ARCGIS, tmp_path / "b", "F", cliente=ServidorFalso(total=2100), pausa=0)

    assert a.hash_sha256 == b.hash_sha256
    assert a.hash_sha256 == hashlib.sha256(a.caminho.read_bytes()).hexdigest()
    with zipfile.ZipFile(a.caminho) as z:
        assert all(i.compress_type == zipfile.ZIP_DEFLATED for i in z.infolist())
        assert json.loads(z.read("coleta.json"))["total"] == 2100


def test_validar_url_recusa_rede_interna():
    for url in ("http://127.0.0.1/x", "http://169.254.169.254/latest", "http://10.0.0.5/a", "ftp://x.gov.br/a"):
        with pytest.raises(coleta.ColetaFalhou):
            coleta.validar_url(url)
