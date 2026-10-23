"""Conexão com o Oracle (python-oracledb em modo thin: não precisa de Instant Client)."""

import re
from contextlib import contextmanager

import oracledb

from georural.config import Config

# Nome de schema vai direto no SQL (ALTER SESSION não aceita bind), então só letras,
# números e _ — nada que permita injetar comando.
_IDENTIFICADOR = re.compile(r"^[A-Za-z][A-Za-z0-9_$#]{0,127}$")


@contextmanager
def conectar(cfg: Config):
    """Abre uma conexão e fecha ao sair do with. Nada é confirmado sem commit() explícito."""
    con = oracledb.connect(
        user=cfg.db_usuario,
        password=cfg.db_senha,
        dsn=f"{cfg.db_host}:{cfg.db_porta}/{cfg.db_servico}",
    )
    try:
        if cfg.db_schema:
            if not _IDENTIFICADOR.match(cfg.db_schema):
                raise RuntimeError(f"GEORURAL_DB_SCHEMA inválido: {cfg.db_schema!r}")
            # Na VM o Airflow conecta com um usuário próprio (sem DDL) e trabalha nas tabelas
            # do dono da aplicação; assim o SQL não precisa do prefixo do schema.
            with con.cursor() as cur:
                cur.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {cfg.db_schema}")
        yield con
    finally:
        con.close()
