"""Acesso ao Object Storage da OCI (o GeoDataLake).

Duas formas de autenticar, escolhidas por GEORURAL_OCI_AUTH:
    config              chave da API em ~/.oci/config (o seu computador, igual ao back-end)
    instance_principal  a própria VM se identifica na OCI, sem chave em disco
"""

import configparser
import os
from pathlib import Path

import oci

from georural.config import Config

TAMANHO_BLOCO = 1024 * 1024  # 1 MB por vez: o download nunca fica inteiro na memória


def cliente(cfg: Config) -> oci.object_storage.ObjectStorageClient:
    if cfg.oci_autenticacao == "instance_principal":
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return oci.object_storage.ObjectStorageClient(config={}, signer=signer)

    config = _ler_config(cfg.oci_config)
    config["key_file"] = _caminho_da_chave(config.get("key_file"), cfg.oci_config)
    oci.config.validate_config(config)
    return oci.object_storage.ObjectStorageClient(config)


def _ler_config(arquivo: str, perfil: str = "DEFAULT") -> dict:
    """Lê o ~/.oci/config sem a validação do SDK, que recusaria o caminho de chave do Windows
    antes de dar tempo de corrigi-lo (oci.config.from_file valida ao ler)."""
    leitor = configparser.ConfigParser(interpolation=None)
    if not leitor.read(arquivo):
        raise FileNotFoundError(f"Config da OCI não encontrado: {arquivo}")
    if perfil != "DEFAULT" and not leitor.has_section(perfil):
        raise KeyError(f"Perfil {perfil} não existe em {arquivo}")
    return dict(leitor[perfil])


def _caminho_da_chave(key_file: str | None, arquivo_config: str) -> str | None:
    """A chave criada no Windows fica registrada como C:\\Users\\...\\chave.pem, caminho que não
    existe dentro do container. Nesse caso procura o arquivo pelo nome, ao lado do config."""
    if not key_file or os.path.exists(os.path.expanduser(key_file)):
        return key_file
    nome = key_file.replace("\\", "/").split("/")[-1]
    alternativo = Path(arquivo_config).parent / nome
    return str(alternativo) if alternativo.exists() else key_file


def listar(cfg: Config, prefixo: str, limite: int = 10) -> list[str]:
    resposta = cliente(cfg).list_objects(cfg.oci_namespace, cfg.oci_bucket, prefix=prefixo, limit=limite)
    return [obj.name for obj in resposta.data.objects]


def enviar(cfg: Config, chave_objeto: str, origem: Path, content_type: str) -> None:
    """Grava um arquivo do disco no bucket, em streaming (o zip do CAR tem centenas de MB)."""
    with open(origem, "rb") as arquivo:
        cliente(cfg).put_object(cfg.oci_namespace, cfg.oci_bucket, chave_objeto, arquivo,
                                content_length=origem.stat().st_size, content_type=content_type)


def baixar(cfg: Config, chave_objeto: str, destino: Path) -> Path:
    """Baixa um objeto em blocos direto para o disco."""
    try:
        resposta = cliente(cfg).get_object(cfg.oci_namespace, cfg.oci_bucket, chave_objeto)
    except oci.exceptions.ServiceError as e:
        # A mensagem vai para execucao.mensagem_erro e aparece na tela: melhor uma frase clara
        # do que o dicionário cru do SDK.
        motivo = "o arquivo não existe no bucket" if e.status == 404 else f"erro {e.status} ({e.code})"
        raise RuntimeError(f"Não foi possível baixar '{chave_objeto}' da zona bruta: {motivo}") from e
    with open(destino, "wb") as arquivo:
        for bloco in resposta.data.raw.stream(TAMANHO_BLOCO, decode_content=False):
            arquivo.write(bloco)
    return destino
