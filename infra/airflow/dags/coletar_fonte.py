"""
### coletar_fonte

Coleta o link de uma fonte inteiro e grava o resultado na zona bruta, como um upload.

* serviço ArcGIS ou WFS: página por página, conferindo o total; vira um zip de páginas GeoJSON
* arquivo (zip, CSV, GeoJSON): baixado de uma vez

No fim, se o conteúdo for igual ao da última coleta (mesmo hash), nada é gravado ("sem mudança").
Senão, o zip vai para `bruta/<SIGLA>/<data>/...` e nasce um `arquivo_bruto` RECEBIDO (origem
COLETA), que o `varredor_bruta` manda processar. O andamento e o resultado aparecem na tela da
fonte (`fonte.ultima_coleta_mensagem`).

**Como é disparada**
* pelo `coleta_fontes`: `{"fonte_id": 7}`
* à mão, pela interface do Airflow (*Trigger DAG w/ config*), com o mesmo `{"fonte_id": 7}`

Uma coleta por vez (`max_active_runs=1`): os serviços públicos de origem agradecem.
"""

import tempfile
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.sdk import Param, dag, get_current_context, task

from georural import bucket, coleta, config, fontes
from georural.banco import conectar


def _registrar_falha(context) -> None:
    """Chamado só quando a tarefa falha de vez: a tela da fonte mostra o motivo."""
    erro = context.get("exception") or "falha sem mensagem (veja o log da tarefa no Airflow)"
    with conectar(config.carregar()) as con:
        fontes.registrar_fim(con, int(context["params"]["fonte_id"]), f"A coleta falhou: {erro}")


@dag(
    dag_id="coletar_fonte",
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    tags=["georural", "coleta"],
    doc_md=__doc__,
    params={"fonte_id": Param(None, type=["null", "integer"], description="id em fonte")},
)
def coletar_fonte():

    @task(retries=0, execution_timeout=timedelta(hours=6), on_failure_callback=_registrar_falha)
    def coletar() -> dict:
        params = get_current_context()["params"]
        if params.get("fonte_id") is None:
            raise ValueError('Informe {"fonte_id": <id>} na configuração do disparo')
        fonte_id = int(params["fonte_id"])
        cfg = config.carregar()

        with conectar(cfg) as con, tempfile.TemporaryDirectory(prefix="coleta-") as pasta:
            fonte = fontes.buscar(con, fonte_id)
            resultado = coleta.coletar(
                fonte.url, Path(pasta), fonte.sigla,
                chaves=fontes.colunas_chave(con, fonte_id),
                metodo=fonte.metodo, cabecalhos=fonte.cabecalhos, corpo=fonte.corpo,
                progresso=lambda mensagem: fontes.registrar_andamento(con, fonte_id, mensagem),
            )

            anterior = fontes.ultimo_hash(con, fonte_id)
            if anterior and anterior[1] == resultado.hash_sha256:
                fontes.registrar_fim(con, fonte_id, f"Sem mudança desde a última coleta (arquivo {anterior[0]}): "
                                                    f"{resultado.mensagem()}")
                return {"resultado": "SEM_MUDANCA", "arquivo_bruto_id": anterior[0]}

            fontes.registrar_andamento(con, fonte_id, f"{fontes.PREFIXO_ANDAMENTO}: enviando para a zona bruta.")
            chave = fontes.chave_na_zona_bruta(cfg.oci_zona_bruta, fonte.sigla, resultado.nome)
            bucket.enviar(cfg, chave, resultado.caminho, resultado.content_type)
            arquivo_id = fontes.gravar_arquivo(con, fonte_id, chave, resultado.nome, resultado.tamanho,
                                               resultado.content_type, resultado.hash_sha256)
            fontes.registrar_fim(con, fonte_id, f"{resultado.mensagem()} Arquivo {arquivo_id} na fila do processamento.")
            return {"resultado": "RECEBIDO", "arquivo_bruto_id": arquivo_id, "total": resultado.total,
                    "coletados": resultado.coletados, "paginas": resultado.paginas, "bytes": resultado.tamanho}

    coletar()


coletar_fonte()
