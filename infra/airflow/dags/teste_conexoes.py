"""
### teste_conexoes

Rode à mão depois de subir o Airflow num lugar novo (seu PC ou uma VM).
Se as duas tarefas ficarem verdes, o ambiente está pronto para processar.
"""

import pendulum
from airflow.sdk import dag, task

from georural import bucket, config
from georural.banco import conectar


@dag(
    dag_id="teste_conexoes",
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["georural", "infra"],
    doc_md=__doc__,
)
def teste_conexoes():

    @task
    def oracle() -> str:
        cfg = config.carregar()
        with conectar(cfg) as con, con.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM arquivo_bruto")
            total = cur.fetchone()[0]
        return f"Oracle OK ({cfg.db_host}:{cfg.db_porta}/{cfg.db_servico}) — {total} arquivos em arquivo_bruto"

    @task
    def object_storage() -> str:
        cfg = config.carregar()
        objetos = bucket.listar(cfg, prefixo="bruta/", limite=5)
        return f"Bucket OK ({cfg.oci_bucket}, auth={cfg.oci_autenticacao}) — exemplos: {objetos}"

    oracle()
    object_storage()


teste_conexoes()
