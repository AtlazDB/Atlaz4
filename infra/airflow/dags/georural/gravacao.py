"""Toda a escrita do processamento no Oracle, em SQL direto — o mesmo SQL do GravadorImoveis
do back-end. Usa as tabelas como estão hoje (Flyway V1 a V7).

Quando o pkg_tratada (Tarefa 1) existir, a gravação dos imóveis passa a chamar o pacote.
"""

from dataclasses import dataclass

import oracledb

from georural import sdo
from georural.validacao import Resultado

CONJUNTO_IMOVEIS = "imoveis_rurais"

SQL_MERGE_IMOVEL = """
    MERGE INTO imovel_rural d
    USING (SELECT :cod_imovel cod_imovel, :municipio municipio, :estado estado, :area_ha area_ha,
                  :situacao situacao, :geometria geometria,
                  :dataset_versao_id dataset_versao_id FROM dual) s
    ON (d.cod_imovel = s.cod_imovel)
    WHEN MATCHED THEN UPDATE SET d.municipio = s.municipio, d.estado = s.estado,
         d.area_ha = s.area_ha, d.situacao = s.situacao, d.geometria = s.geometria,
         d.dataset_versao_id = s.dataset_versao_id
    WHEN NOT MATCHED THEN INSERT (cod_imovel, municipio, estado, area_ha, situacao,
         geometria, dataset_versao_id)
         VALUES (s.cod_imovel, s.municipio, s.estado, s.area_ha, s.situacao,
                 s.geometria, s.dataset_versao_id)
"""

SQL_QUARENTENA = """
    INSERT INTO registro_quarentena (execucao_id, numero_linha, campo, motivo, payload)
    VALUES (:execucao_id, :numero_linha, :campo, :motivo, :payload)
"""


@dataclass(frozen=True)
class Arquivo:
    id: int
    chave_objeto: str
    nome_original: str
    status: str
    sigla_fonte: str

    @property
    def processavel(self) -> bool:
        """Por enquanto só o shapefile de imóveis do CAR (.zip), como no back-end."""
        return self.sigla_fonte.upper() == "CAR" and self.nome_original.lower().endswith(".zip")


@dataclass(frozen=True)
class Versao:
    id: int
    numero: int


# ------------------------------------------------------------------ arquivo e reserva

def buscar_arquivo(con, arquivo_id: int) -> Arquivo | None:
    with con.cursor() as cur:
        cur.execute(
            """
            SELECT a.id, a.chave_objeto, a.nome_original, a.status, f.sigla
              FROM arquivo_bruto a JOIN fonte f ON f.id = a.fonte_id
             WHERE a.id = :id
            """,
            id=arquivo_id,
        )
        linha = cur.fetchone()
    return Arquivo(*linha) if linha else None


def listar_recebidos(con, limite: int) -> list[int]:
    """Arquivos do CAR (.zip) que chegaram na zona bruta e ainda não foram processados."""
    with con.cursor() as cur:
        cur.execute(
            """
            SELECT a.id
              FROM arquivo_bruto a JOIN fonte f ON f.id = a.fonte_id
             WHERE a.status = 'RECEBIDO'
               AND UPPER(f.sigla) = 'CAR'
               AND LOWER(a.nome_original) LIKE '%.zip'
             ORDER BY a.recebido_em
             FETCH FIRST :limite ROWS ONLY
            """,
            limite=limite,
        )
        return [linha[0] for linha in cur.fetchall()]


def reservar(con, arquivo_id: int, somente_recebido: bool = True) -> bool:
    """Passa o arquivo para PROCESSANDO. Devolve False se outro processo pegou antes.

    O UPDATE condicional é o que impede dois processamentos do mesmo arquivo: só um consegue
    mudar o status. Com somente_recebido=False aceita reprocessar um arquivo já processado
    ou rejeitado (disparo manual), mas nunca um que esteja PROCESSANDO.
    """
    condicao = "status = 'RECEBIDO'" if somente_recebido else "status <> 'PROCESSANDO'"
    with con.cursor() as cur:
        cur.execute(
            f"UPDATE arquivo_bruto SET status = 'PROCESSANDO', processado_em = NULL "
            f"WHERE id = :id AND {condicao}",
            id=arquivo_id,
        )
        reservado = cur.rowcount == 1
    con.commit()
    return reservado


# ------------------------------------------------------------------ execução e versão

def iniciar_execucao(con, arquivo_id: int, dag_run_id: str | None) -> int:
    """Abre a execução fora da transação principal: se o resto falhar, ela continua no banco
    para receber FALHOU."""
    with con.cursor() as cur:
        id_var = cur.var(oracledb.DB_TYPE_NUMBER)
        cur.execute(
            """
            INSERT INTO execucao (arquivo_bruto_id, tipo, status, dag_run_id)
            VALUES (:arquivo_id, 'VALIDACAO', 'EM_ANDAMENTO', :dag_run_id)
            RETURNING id INTO :id_saida
            """,
            arquivo_id=arquivo_id,
            dag_run_id=(dag_run_id or "")[:120] or None,
            id_saida=id_var,
        )
        execucao_id = int(id_var.getvalue()[0])
    con.commit()
    return execucao_id


def criar_versao(cur, execucao_id: int) -> Versao:
    """Próxima versão do conjunto na zona TRATADA. Roda dentro da transação principal."""
    cur.execute(
        "SELECT NVL(MAX(versao), 0) + 1 FROM dataset_versao WHERE conjunto = :conjunto",
        conjunto=CONJUNTO_IMOVEIS,
    )
    numero = int(cur.fetchone()[0])
    id_var = cur.var(oracledb.DB_TYPE_NUMBER)
    cur.execute(
        """
        INSERT INTO dataset_versao (conjunto, versao, execucao_id, zona)
        VALUES (:conjunto, :versao, :execucao_id, 'TRATADA')
        RETURNING id INTO :id_saida
        """,
        conjunto=CONJUNTO_IMOVEIS,
        versao=numero,
        execucao_id=execucao_id,
        id_saida=id_var,
    )
    return Versao(id=int(id_var.getvalue()[0]), numero=numero)


# ------------------------------------------------------------------ lotes

def gravar_imoveis(cur, dataset_versao_id: int, aprovados: list[Resultado]) -> None:
    """Grava um lote de aprovados, com a geometria já montada como SDO_GEOMETRY (ver sdo.py)."""
    if not aprovados:
        return
    tipos = sdo.TiposSdo(cur.connection)
    cur.setinputsizes(geometria=tipos.geometria)
    cur.executemany(
        SQL_MERGE_IMOVEL,
        [
            {
                "cod_imovel": r.cod_imovel,
                "municipio": r.municipio,
                "estado": r.estado,
                "area_ha": r.area_ha,
                "situacao": r.situacao,
                "geometria": tipos.converter(r.geometria, sdo.SRID_BANCO),
                "dataset_versao_id": dataset_versao_id,
            }
            for r in aprovados
        ],
    )


def gravar_quarentena(cur, execucao_id: int, reprovados: list[Resultado]) -> None:
    if not reprovados:
        return
    cur.setinputsizes(payload=oracledb.DB_TYPE_CLOB)
    cur.executemany(
        SQL_QUARENTENA,
        [
            {
                "execucao_id": execucao_id,
                "numero_linha": r.linha,
                "campo": r.campo,
                "motivo": r.motivo[:400],
                "payload": r.payload_json(),
            }
            for r in reprovados
        ],
    )


# ------------------------------------------------------------------ fim

def concluir(cur, arquivo_id: int, execucao_id: int, versao: Versao,
             lidos: int, validos: int, invalidos: int) -> None:
    cur.execute(
        """
        UPDATE execucao SET status = 'CONCLUIDA', finalizada_em = SYSTIMESTAMP,
               registros_lidos = :lidos, registros_validos = :validos, registros_invalidos = :invalidos
         WHERE id = :id
        """,
        lidos=lidos, validos=validos, invalidos=invalidos, id=execucao_id,
    )
    cur.execute("UPDATE dataset_versao SET registros = :n WHERE id = :id", n=validos, id=versao.id)
    cur.execute(
        "UPDATE arquivo_bruto SET status = 'PROCESSADO', processado_em = SYSTIMESTAMP WHERE id = :id",
        id=arquivo_id,
    )


def falhar(con, arquivo_id: int, execucao_id: int | None, mensagem: str) -> None:
    """Registra a falha numa transação própria (a principal já foi desfeita)."""
    with con.cursor() as cur:
        if execucao_id is not None:
            cur.execute(
                """
                UPDATE execucao SET status = 'FALHOU', finalizada_em = SYSTIMESTAMP, mensagem_erro = :msg
                 WHERE id = :id
                """,
                msg=(mensagem or "")[:4000], id=execucao_id,
            )
        cur.execute(
            "UPDATE arquivo_bruto SET status = 'REJEITADO', processado_em = SYSTIMESTAMP WHERE id = :id",
            id=arquivo_id,
        )
    con.commit()
