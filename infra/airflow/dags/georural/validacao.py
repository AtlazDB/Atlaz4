"""Regras de validação do CAR — as mesmas do ValidadorImovel do back-end, com uma diferença:
geometria inválida vai para a quarentena em vez de ser corrigida em silêncio (decisão D11).

Código repetido (planejar_desempate): entra uma ocorrência só, escolhida assim:
  1. a ativa (AT) vence qualquer outra situação;
  2. sem AT, vence a mais recente (dat_atuali, depois dat_criaca);
  3. com as mesmas datas, a cancelada (CA) perde para a que não está cancelada;
  4. empate em tudo: a primeira do arquivo.
As outras vão para a quarentena já DESCARTADAS, com o critério que decidiu, quando a decisão
é segura: havia AT, era cópia idêntica (mesma situação e área), era mais antiga ou era a
cancelada no empate. Ficam pendentes para o operador só os conflitos de verdade: mesma
situação com área diferente, ou situações diferentes (nenhuma CA) sem data que desempate.

Isto é provisório: quando o pkg_qualidade (Tarefa 2) estiver pronto, a validação passa para
o Oracle e este módulo deixa de ser usado.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import pandas as pd
import shapely
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity

# Nomes das colunas no .dbf do CAR (a busca ignora maiúsculas/minúsculas)
COLUNA_COD_IMOVEL = "cod_imovel"
COLUNA_MUNICIPIO = "municipio"
COLUNA_AREA = "num_area"
COLUNA_SITUACAO = "ind_status"

COLUNA_ATUALIZACAO = "dat_atuali"  # data da última atualização do cadastro, DD/MM/AAAA
COLUNA_CRIACAO = "dat_criaca"

SITUACAO_ATIVO = "AT"
SITUACAO_CANCELADO = "CA"
FORMATO_DATA = "%d/%m/%Y"


@dataclass(frozen=True)
class Descarte:
    """Por que uma ocorrência repetida saiu sozinha: vai para a quarentena já DESCARTADA."""
    motivo: str         # começa com "cod_imovel duplicado": vira CHAVE_NATURAL_DUPLICADA
    justificativa: str  # o que o operador lê na tela


@dataclass(frozen=True)
class Desempate:
    """Como resolver um código repetido no arquivo."""
    vencedora: int  # posição da ocorrência que entra, na ordem do arquivo (1 = a primeira)
    # Posições descartadas sozinhas. As que não estão aqui ficam pendentes para o operador.
    descartes: dict[int, Descarte]


@dataclass
class Resultado:
    linha: int
    atributos: dict
    cod_imovel: str | None = None
    municipio: str | None = None
    area_ha: Decimal | None = None
    situacao: str | None = None
    geometria: BaseGeometry | None = None
    # A geometria como chegou (já em 4326), aprovada ou não: vai para a quarentena.
    geometria_recebida: BaseGeometry | None = None
    campo: str | None = None
    motivo: str | None = None
    # Repetição resolvida pelo desempate: vai para a quarentena já DESCARTADA, com a justificativa
    descartado_automaticamente: bool = False
    justificativa: str | None = None

    @property
    def aprovado(self) -> bool:
        return self.motivo is None

    @property
    def estado(self) -> str | None:
        """UF pelo prefixo do código do CAR: "PR-4113700-..." → "PR"."""
        cod = self.cod_imovel
        if cod and len(cod) > 3 and cod[2] == "-":
            return cod[:2].upper()
        return None

    @property
    def tipo_erro(self) -> str | None:
        """Código da V10 (tabela tipo_erro) pelo começo do motivo; o mesmo de-para do back-end."""
        for prefixo, codigo in _TIPOS_DE_ERRO:
            if self.motivo and self.motivo.startswith(prefixo):
                return codigo
        return None

    @property
    def valor_recebido(self) -> str | None:
        """O valor que reprovou, quando é um campo (o código); a geometria tem coluna própria."""
        return self.cod_imovel if self.campo == "cod_imovel" else None

    def payload_json(self) -> str:
        """As colunas do .dbf, sem a geometria (que pode ter milhares de pontos)."""
        return json.dumps(self.atributos, ensure_ascii=False, default=str)


@dataclass(frozen=True)
class ColunasDesempate:
    """Onde estão, no arquivo, as colunas que o desempate usa. O padrão é o shapefile do CAR; o
    caminho genérico passa as colunas que o mapeamento da fonte resolveu (no WFS do SICAR:
    status_imovel, area, dat_criacao)."""
    codigo: str = COLUNA_COD_IMOVEL
    situacao: str | None = COLUNA_SITUACAO
    area: str | None = COLUNA_AREA
    atualizacao: str | None = COLUNA_ATUALIZACAO
    criacao: str | None = COLUNA_CRIACAO

    def todas(self) -> list[str]:
        return [c for c in (self.codigo, self.situacao, self.area, self.atualizacao, self.criacao) if c]


COLUNAS_SHAPEFILE = ColunasDesempate()


def planejar_desempate(chaves, colunas: ColunasDesempate = COLUNAS_SHAPEFILE) -> dict[str, Desempate]:
    """Para cada código repetido no arquivo, qual ocorrência entra.

    `chaves` é a tabela com as colunas do desempate do arquivo inteiro, na ordem de leitura (ver
    shapefile.ler_colunas): sem geometria, cabe na memória mesmo com o PR todo. Só os códigos
    repetidos ficam no plano (no CAR do PR, uns 2.300 de 560 mil).
    """
    if colunas.codigo not in chaves:
        return {}
    codigos = chaves[colunas.codigo].map(_texto)
    repetidos = codigos.notna() & codigos.duplicated(keep=False)
    if not repetidos.any():
        return {}

    def coluna(nome, converter):
        if not nome or nome not in chaves:
            return pd.Series(None, index=codigos[repetidos].index, dtype=object)
        return converter(chaves.loc[repetidos, nome])

    tabela = pd.DataFrame({
        "codigo": codigos[repetidos],
        "situacao": coluna(colunas.situacao, lambda s: s.map(lambda v: (_texto(v) or "").upper() or None)),
        "area": coluna(colunas.area, lambda s: s.map(_numero)),
        "atualizacao": coluna(colunas.atualizacao, _datas),
        "criacao": coluna(colunas.criacao, _datas),
    })
    plano: dict[str, Desempate] = {}
    for codigo, grupo in tabela.groupby("codigo", sort=False):
        ocorrencias = [
            _Ocorrencia(posicao, linha.situacao, linha.area, linha.atualizacao, linha.criacao)
            for posicao, linha in enumerate(grupo.itertuples(index=False), start=1)
        ]
        plano[codigo] = _resolver(ocorrencias)
    return plano


@dataclass(frozen=True)
class _Ocorrencia:
    posicao: int
    situacao: str | None
    area: Decimal | None
    atualizacao: "pd.Timestamp"
    criacao: "pd.Timestamp"

    @property
    def recencia(self) -> tuple[float, float]:
        """(atualização, criação) para comparar; data ausente conta como a mais antiga."""
        return (_instante(self.atualizacao), _instante(self.criacao))


def _resolver(ocorrencias: list[_Ocorrencia]) -> Desempate:
    vencedora = min(
        ocorrencias,
        key=lambda o: (o.situacao != SITUACAO_ATIVO, -o.recencia[0], -o.recencia[1],
                       o.situacao == SITUACAO_CANCELADO, o.posicao),
    )
    descartes: dict[int, Descarte] = {}
    for o in ocorrencias:
        if o is vencedora:
            continue
        if vencedora.situacao == SITUACAO_ATIVO and o.situacao != SITUACAO_ATIVO:
            descartes[o.posicao] = Descarte(
                "cod_imovel duplicado: existe versão ativa (AT) do mesmo imóvel no arquivo",
                f"Descartado automaticamente: o mesmo código veio ativo (AT) no arquivo, e a versão "
                f"ativa foi gravada na Zona Tratada (esta estava {o.situacao or 'sem situação'}).",
            )
        elif o.situacao == vencedora.situacao:
            if o.area is not None and o.area == vencedora.area:
                descartes[o.posicao] = Descarte(
                    "cod_imovel duplicado: cópia idêntica (mesma situação e mesma área)",
                    "Descartado automaticamente: cópia de outro registro do arquivo, com a mesma "
                    "situação e a mesma área, que foi gravado na Zona Tratada.",
                )
            # Mesma situação e área diferente: conflito de verdade, fica para o operador.
        elif vencedora.recencia > o.recencia:
            descartes[o.posicao] = Descarte(
                "cod_imovel duplicado: versão mais antiga do mesmo imóvel no arquivo",
                f"Descartado automaticamente: versão {_quando(o)} ({o.situacao or 'sem situação'}); "
                f"a versão {_quando(vencedora)} ({vencedora.situacao or 'sem situação'}) "
                f"foi gravada na Zona Tratada.",
            )
        elif o.situacao == SITUACAO_CANCELADO:
            # Mesmas datas: a cancelada perde para a que não está cancelada.
            descartes[o.posicao] = Descarte(
                "cod_imovel duplicado: versão cancelada (CA) com a mesma data de uma não cancelada",
                f"Descartado automaticamente: as duas versões têm a mesma data ({_quando(o)}); "
                f"a cancelada (CA) perde para a {vencedora.situacao or 'sem situação'}, "
                f"que foi gravada na Zona Tratada.",
            )
        # Situações diferentes, nenhuma cancelada, e as mesmas datas: ninguém decide por sorte.
    return Desempate(vencedora=vencedora.posicao, descartes=descartes)


def _datas(serie):
    """DD/MM/AAAA, como o shapefile do CAR; se nada converter, ISO 8601 (o WFS do SICAR manda
    2014-05-07T20:52:55.333Z). A data vira ingênua (sem fuso) para as duas se compararem."""
    datas = pd.to_datetime(serie, format=FORMATO_DATA, errors="coerce")
    if datas.isna().all() and serie.notna().any():
        datas = pd.to_datetime(serie, format="ISO8601", errors="coerce", utc=True).dt.tz_localize(None)
    return datas


def _instante(data) -> float:
    return float(data.value) if pd.notna(data) else float("-inf")


def _quando(o: _Ocorrencia) -> str:
    if pd.notna(o.atualizacao):
        return f"atualizada em {o.atualizacao:%d/%m/%Y}"
    if pd.notna(o.criacao):
        return f"criada em {o.criacao:%d/%m/%Y}"
    return "sem data"


class ValidadorImovel:
    """Valida os imóveis de UM arquivo. Guarda os códigos já vistos para achar duplicados,
    então crie uma instância nova para cada arquivo processado.

    Com o `desempate` (planejar_desempate), cada código repetido segue o plano; sem ele, a
    primeira ocorrência entra e as seguintes vão para a quarentena, como no back-end.
    """

    def __init__(self, desempate: Mapping[str, Desempate] | None = None) -> None:
        self._codigos_vistos: set[str] = set()
        self._desempate = desempate or {}
        self._ocorrencias: dict[str, int] = {}

    def validar(self, linha: int, atributos: dict, geometria: BaseGeometry | None) -> Resultado:
        colunas = {nome.lower(): nome for nome in atributos}
        r = Resultado(
            linha=linha,
            atributos={k: _valor_json(v) for k, v in atributos.items()},
            cod_imovel=_texto(atributos.get(colunas.get(COLUNA_COD_IMOVEL, ""))),
            municipio=_texto(atributos.get(colunas.get(COLUNA_MUNICIPIO, ""))),
            area_ha=_numero(atributos.get(colunas.get(COLUNA_AREA, ""))),
            situacao=_texto(atributos.get(colunas.get(COLUNA_SITUACAO, ""))),
            geometria_recebida=geometria,
        )

        if not r.cod_imovel:
            return _reprovar(r, "cod_imovel", "cod_imovel vazio")
        regra = self._desempate.get(r.cod_imovel)
        if regra is not None:
            ocorrencia = self._ocorrencias[r.cod_imovel] = self._ocorrencias.get(r.cod_imovel, 0) + 1
            if ocorrencia != regra.vencedora:
                descarte = regra.descartes.get(ocorrencia)
                if descarte is not None:
                    r.descartado_automaticamente = True
                    r.justificativa = descarte.justificativa
                    return _reprovar(r, "cod_imovel", descarte.motivo)
                return _reprovar(r, "cod_imovel", "cod_imovel duplicado")
        # Fora do plano (ou sem plano): a primeira ocorrência passa e as seguintes vão para a
        # quarentena, como no back-end.
        elif r.cod_imovel in self._codigos_vistos:
            return _reprovar(r, "cod_imovel", "cod_imovel duplicado")
        self._codigos_vistos.add(r.cod_imovel)

        if geometria is None or geometria.is_empty:
            return _reprovar(r, "geometria", "sem geometria")
        if geometria.geom_type not in ("Polygon", "MultiPolygon"):
            return _reprovar(r, "geometria", f"geometria não é polígono ({geometria.geom_type})")
        if not geometria.is_valid:
            # Não corrige: quem decide é o operador, na quarentena.
            return _reprovar(r, "geometria", f"geometria inválida: {explain_validity(geometria)}")

        # O Oracle exige o anel externo no sentido anti-horário; o shapefile guarda horário.
        r.geometria = shapely.orient_polygons(geometria, exterior_cw=False)
        return r


_TIPOS_DE_ERRO = [
    ("cod_imovel vazio", "CAMPO_OBRIGATORIO_AUSENTE"),
    ("cod_imovel duplicado", "CHAVE_NATURAL_DUPLICADA"),
    ("sem geometria", "GEOMETRIA_NULA"),
    ("geometria não é polígono", "GEOMETRIA_TIPO_INCOMPATIVEL"),
    ("geometria inválida", "GEOMETRIA_INVALIDA"),
]


def _reprovar(r: Resultado, campo: str, motivo: str) -> Resultado:
    r.campo = campo
    r.motivo = motivo
    return r


def _vazio(valor) -> bool:
    """None, NaN, NaT e pd.NA: as formas de "vazio" que o pandas devolve."""
    try:
        return bool(pd.isna(valor))
    except (TypeError, ValueError):
        return False


def _texto(valor) -> str | None:
    if _vazio(valor):
        return None
    texto = str(valor).strip()
    return texto or None


def _numero(valor) -> Decimal | None:
    if _vazio(valor):
        return None
    try:
        return Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        return None


def _valor_json(valor):
    """Converte os tipos do pandas/numpy para algo que vira JSON."""
    if _vazio(valor):
        return None
    if hasattr(valor, "item"):  # numpy.int64, numpy.float64...
        return valor.item()
    return valor
