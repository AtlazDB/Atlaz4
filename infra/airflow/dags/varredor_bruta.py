"""
### varredor_bruta

A cada 2 minutos, procura arquivos que chegaram na zona bruta (status RECEBIDO) e dispara
o `processar_arquivo` para cada um.

Por que um varredor, e não o back-end disparando a DAG no upload: assim o upload não depende
do Airflow estar no ar. Se o Airflow cair, os arquivos ficam RECEBIDO e são processados quando
ele voltar. Mais para frente o back-end também pode disparar na hora, e o varredor continua
como rede de segurança.

A reserva (RECEBIDO → PROCESSANDO) acontece **antes** do disparo, num UPDATE condicional:
um arquivo nunca é disparado duas vezes, nem se o processamento anterior ainda estiver na fila.
"""

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import dag, task

from georural import config, gravacao
from georural.banco import conectar

# Quantos arquivos o varredor pega por rodada. Os disparos entram na fila do processar_arquivo,
# que roda um de cada vez.
LIMITE_POR_RODADA = 10


@dag(
    dag_id="varredor_bruta",
    schedule=timedelta(minutes=2),
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    catchup=False,
    max_active_runs=1,
    tags=["georural", "ingestao"],
    doc_md=__doc__,
)
def varredor_bruta():

    @task
    def reservar_recebidos() -> list[dict]:
        cfg = config.carregar()
        with conectar(cfg) as con:
            candidatos = gravacao.listar_recebidos(con, LIMITE_POR_RODADA)
            reservados = [arquivo_id for arquivo_id in candidatos if gravacao.reservar(con, arquivo_id)]

        agora = pendulum.now("UTC").format("YYYYMMDDHHmmss")
        return [
            {
                "trigger_run_id": f"arquivo-{arquivo_id}-{agora}",
                "conf": {"arquivo_bruto_id": arquivo_id, "reservado": True},
            }
            for arquivo_id in reservados
        ]

    # Uma tarefa de disparo por arquivo reservado; sem arquivos, ela é pulada.
    TriggerDagRunOperator.partial(
        task_id="disparar_processamento",
        trigger_dag_id="processar_arquivo",
        wait_for_completion=False,
    ).expand_kwargs(reservar_recebidos())


varredor_bruta()
