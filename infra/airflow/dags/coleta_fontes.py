"""
### coleta_fontes

A cada 2 minutos, procura fontes por link com pedido de coleta (o "Executar" da tela marca
`fonte.coleta_solicitada_em`) e dispara o `coletar_fonte` para cada uma.

Mesmo desenho do `varredor_bruta`: a reserva (tirar o pedido da fila) é um UPDATE condicional
feito **antes** do disparo, então um pedido nunca é coletado duas vezes. Se o Airflow estiver
fora do ar, os pedidos esperam na fila.
"""

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import dag, task

from georural import config, fontes
from georural.banco import conectar

LIMITE_POR_RODADA = 10


@dag(
    dag_id="coleta_fontes",
    schedule=timedelta(minutes=2),
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    tags=["georural", "coleta"],
    doc_md=__doc__,
)
def coleta_fontes():

    @task
    def reservar_pedidos() -> list[dict]:
        cfg = config.carregar()
        with conectar(cfg) as con:
            candidatas = fontes.listar_pedidos(con, LIMITE_POR_RODADA)
            reservadas = [fonte_id for fonte_id in candidatas if fontes.reservar(con, fonte_id)]

        agora = pendulum.now("UTC").format("YYYYMMDDHHmmss")
        return [
            {"trigger_run_id": f"fonte-{fonte_id}-{agora}", "conf": {"fonte_id": fonte_id}}
            for fonte_id in reservadas
        ]

    TriggerDagRunOperator.partial(
        task_id="disparar_coleta",
        trigger_dag_id="coletar_fonte",
        wait_for_completion=False,
    ).expand_kwargs(reservar_pedidos())


coleta_fontes()
