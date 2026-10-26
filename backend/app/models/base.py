from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(DateTime(), default=utc_now_naive, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(),
        default=utc_now_naive,
        onupdate=utc_now_naive,
        nullable=False,
    )


class SoftDeleteMixin:
    excluido_em: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    def soft_delete(self) -> None:
        self.excluido_em = utc_now_naive()


class Vinculo(StrEnum):
    CLT = "CLT"
    AVULSO = "Avulso"
    VIGIA = "Vigia"
    JOVEM_APRENDIZ = "JovemAprendiz"
    ESTAGIARIO = "Estagiario"


class StatusTrabalhador(StrEnum):
    ATIVO = "Ativo"
    AFASTADO = "Afastado"
    DESLIGADO = "Desligado"


class CodigoPresenca(StrEnum):
    PRESENTE = "P"
    FALTA = "F"
    ATESTADO = "A"
    FALTA_COMPENSADA = "FC"


class OrigemPresenca(StrEnum):
    IMPORTADA = "importada"
    MANUAL = "manual"


class TipoDia(StrEnum):
    SEMANA = "semana"
    SABADO = "sabado"
    DOMINGO_FERIADO = "domingo_feriado"


class AcaoAuditoria(StrEnum):
    CRIACAO = "criacao"
    EDICAO = "edicao"
    EXCLUSAO = "exclusao"
    REVELACAO = "revelacao"
    FECHAMENTO = "fechamento"
    REABERTURA = "reabertura"
