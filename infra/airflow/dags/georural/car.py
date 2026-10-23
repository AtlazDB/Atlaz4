"""Processamento do shapefile de imóveis do CAR, de ponta a ponta.

Faz o mesmo que o ProcessamentoCarServiceImpl do back-end, só que fora da aplicação:
    1. baixa o .zip da zona bruta para um disco temporário
    2. lê cada .shp em lotes (a memória depende do lote, não do arquivo)
    3. valida cada imóvel
    4. grava aprovados (MERGE em imovel_rural) e reprovados (registro_quarentena)
    5. conclui a execução e o arquivo

Versão + imóveis + quarentena + conclusão ficam numa transação só: se der erro no meio,
nada fica pela metade (nem imóvel apontando para uma versão que falhou).
"""

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from georural import bucket, gravacao, shapefile
from georural.banco import conectar
from georural.config import Config
from georural.validacao import ValidadorImovel

log = logging.getLogger(__name__)


@dataclass
class Resumo:
    arquivo_id: int
    execucao_id: int
    versao: int
    lidos: int = 0
    validos: int = 0
    invalidos: int = 0


def preparar(cfg: Config, arquivo_id: int, ja_reservado: bool, dag_run_id: str | None) -> int:
    """Confere o arquivo, garante a reserva (PROCESSANDO) e abre a execução. Devolve o id dela.

    ja_reservado=True quando quem disparou foi o varredor, que já passou o arquivo para
    PROCESSANDO. Num disparo manual a reserva acontece aqui.
    """
    with conectar(cfg) as con:
        arquivo = gravacao.buscar_arquivo(con, arquivo_id)
        if arquivo is None:
            raise ValueError(f"Arquivo {arquivo_id} não existe")
        if not arquivo.processavel:
            raise ValueError(
                f"Arquivo {arquivo_id} ({arquivo.nome_original}, fonte {arquivo.sigla_fonte}) não é um .zip do CAR"
            )
        if not ja_reservado and not gravacao.reservar(con, arquivo_id, somente_recebido=False):
            raise RuntimeError(f"Arquivo {arquivo_id} já está sendo processado")
        return gravacao.iniciar_execucao(con, arquivo_id, dag_run_id)


def processar(cfg: Config, arquivo_id: int, execucao_id: int) -> Resumo:
    """Baixa, lê, valida e grava. Se algo falhar, desfaz tudo e propaga o erro
    (quem chama registra a falha — ver registrar_falha)."""
    with conectar(cfg) as con:
        arquivo = gravacao.buscar_arquivo(con, arquivo_id)

        with tempfile.TemporaryDirectory(prefix="car-") as tmp:
            pasta = Path(tmp)
            zip_local = bucket.baixar(cfg, arquivo.chave_objeto, pasta / "arquivo.zip")
            log.info("Baixado %s (%.1f MB)", arquivo.chave_objeto, zip_local.stat().st_size / 1e6)
            shapefiles = shapefile.extrair(zip_local, pasta / "extraido")
            zip_local.unlink()  # libera o disco: daqui para frente só os .shp importam

            validador = ValidadorImovel()
            try:
                with con.cursor() as cur:
                    versao = gravacao.criar_versao(cur, execucao_id)
                    resumo = Resumo(arquivo_id=arquivo_id, execucao_id=execucao_id, versao=versao.numero)

                    for shp in shapefiles:
                        log.info("Lendo %s", shp.name)
                        for primeira_linha, lote in shapefile.ler_em_lotes(shp, cfg.tamanho_lote):
                            _gravar_lote(cur, validador, lote, primeira_linha, versao, execucao_id, resumo)
                            log.info("%s: %d lidos até agora", shp.name, resumo.lidos)

                    gravacao.concluir(cur, arquivo_id, execucao_id, versao,
                                      resumo.lidos, resumo.validos, resumo.invalidos)
                con.commit()
            except Exception:
                con.rollback()
                raise

    log.info("Arquivo %s processado: %s", arquivo_id, resumo)
    return resumo


def _gravar_lote(cur, validador, lote, primeira_linha, versao, execucao_id, resumo: Resumo) -> None:
    colunas = [c for c in lote.columns if c != lote.geometry.name]
    aprovados, reprovados = [], []

    for deslocamento, (atributos, geometria) in enumerate(
        zip(lote[colunas].to_dict("records"), lote.geometry)
    ):
        resultado = validador.validar(primeira_linha + deslocamento, atributos, geometria)
        (aprovados if resultado.aprovado else reprovados).append(resultado)

    gravacao.gravar_imoveis(cur, versao.id, aprovados)
    gravacao.gravar_quarentena(cur, execucao_id, reprovados)
    resumo.lidos += len(aprovados) + len(reprovados)
    resumo.validos += len(aprovados)
    resumo.invalidos += len(reprovados)


def registrar_falha(cfg: Config, arquivo_id: int, execucao_id: int | None, erro: BaseException | str) -> None:
    mensagem = str(erro) or type(erro).__name__
    with conectar(cfg) as con:
        gravacao.falhar(con, arquivo_id, execucao_id, mensagem)
