"""Configuração do pipeline, lida de variáveis de ambiente.

No seu computador elas vêm do .env.local; na VM, do .env ao lado do compose.
Nenhuma senha fica no código.
"""

import os
from dataclasses import dataclass

# Instance Principal só existe dentro de uma VM da OCI; no PC usa a chave da API.
AUTENTICACOES_OCI = ("config", "instance_principal")


@dataclass(frozen=True)
class Config:
    db_host: str
    db_porta: int
    db_servico: str
    db_usuario: str
    db_senha: str
    # Schema dono das tabelas. Vazio quando o usuário conectado já é o dono (caso do PC).
    db_schema: str | None
    oci_autenticacao: str
    oci_config: str
    oci_namespace: str
    oci_bucket: str
    # Quantos registros do shapefile são lidos e gravados por vez. É isso que limita a
    # memória: o arquivo nunca é carregado inteiro.
    tamanho_lote: int
    # Prefixo da zona bruta no bucket, o mesmo oci.zona-bruta do back-end.
    oci_zona_bruta: str = "bruta"


def _obrigatoria(nome: str) -> str:
    valor = os.environ.get(nome, "").strip()
    if not valor:
        raise RuntimeError(f"Variável de ambiente {nome} não definida (veja o .env.local.example)")
    return valor


def carregar() -> Config:
    autenticacao = os.environ.get("GEORURAL_OCI_AUTH", "config").strip()
    if autenticacao not in AUTENTICACOES_OCI:
        raise RuntimeError(f"GEORURAL_OCI_AUTH deve ser um de {AUTENTICACOES_OCI}, veio '{autenticacao}'")

    return Config(
        db_host=os.environ.get("GEORURAL_DB_HOST", "host.docker.internal"),
        db_porta=int(os.environ.get("GEORURAL_DB_PORTA", "1521")),
        db_servico=os.environ.get("GEORURAL_DB_SERVICO", "FREEPDB1"),
        db_usuario=_obrigatoria("GEORURAL_DB_USUARIO"),
        db_senha=_obrigatoria("GEORURAL_DB_SENHA"),
        db_schema=os.environ.get("GEORURAL_DB_SCHEMA", "").strip() or None,
        oci_autenticacao=autenticacao,
        oci_config=os.environ.get("OCI_CONFIG_FILE", os.path.expanduser("~/.oci/config")),
        oci_namespace=_obrigatoria("GEORURAL_OCI_NAMESPACE"),
        oci_bucket=_obrigatoria("GEORURAL_OCI_BUCKET"),
        tamanho_lote=int(os.environ.get("GEORURAL_TAMANHO_LOTE", "5000")),
        oci_zona_bruta=os.environ.get("GEORURAL_OCI_ZONA_BRUTA", "bruta").strip() or "bruta",
    )
