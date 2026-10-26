from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKeyConstraint,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TaxaFuncao(TimestampMixin, Base):
    __tablename__ = "taxa_funcao"
    __table_args__ = (
        UniqueConstraint("obra_id", "id", name="uq_taxa_funcao_obra_id"),
        UniqueConstraint(
            "obra_id", "funcao_id", "vigente_desde", name="uq_taxa_funcao_inicio_vigencia"
        ),
        CheckConstraint(
            "vigente_ate IS NULL OR vigente_ate >= vigente_desde",
            name="ck_taxa_funcao_vigencia_valida",
        ),
        CheckConstraint(
            "salario_base IS NULL OR salario_base >= 0",
            name="ck_taxa_funcao_salario_base_nao_negativo",
        ),
        CheckConstraint(
            "valor_hora_semana >= 0 AND valor_hora_sabado >= 0",
            name="ck_taxa_funcao_taxas_obrigatorias_nao_negativas",
        ),
        CheckConstraint(
            "valor_hora_domingo_feriado IS NULL OR valor_hora_domingo_feriado >= 0",
            name="ck_taxa_funcao_taxa_domingo_nao_negativa",
        ),
        ForeignKeyConstraint(
            ["obra_id", "funcao_id"],
            ["funcao.obra_id", "funcao.id"],
            name="fk_taxa_funcao_funcao_obra",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    funcao_id: Mapped[str] = mapped_column(String(36), nullable=False)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigente_ate: Mapped[date | None] = mapped_column(Date, nullable=True)
    salario_base: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    divisor: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    multiplicador: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    valor_hora_semana: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_hora_sabado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_hora_domingo_feriado: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
