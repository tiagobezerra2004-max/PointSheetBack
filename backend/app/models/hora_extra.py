from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SqlEnum

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, TipoDia


class HoraExtra(SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "hora_extra"
    __table_args__ = (
        CheckConstraint(
            "horas >= 0.5 AND horas <= 12 AND MOD(horas * 2, 1) = 0",
            name="ck_hora_extra_horas_intervalos",
        ),
        CheckConstraint(
            "taxa_aplicada >= 0 AND valor_calculado >= 0",
            name="ck_hora_extra_valores_nao_negativos",
        ),
        ForeignKeyConstraint(
            ["obra_id", "trabalhador_id"],
            ["trabalhador_obra.obra_id", "trabalhador_obra.trabalhador_id"],
            name="fk_hora_extra_trabalhador_obra",
        ),
        ForeignKeyConstraint(
            ["obra_id", "atividade_id"],
            ["atividade.obra_id", "atividade.id"],
            name="fk_hora_extra_atividade_obra",
        ),
        ForeignKeyConstraint(
            ["obra_id", "taxa_funcao_id"],
            ["taxa_funcao.obra_id", "taxa_funcao.id"],
            name="fk_hora_extra_taxa_funcao_obra",
        ),
        Index("ix_hora_extra_obra_data", "obra_id", "data"),
        Index("ix_hora_extra_trabalhador_data", "obra_id", "trabalhador_id", "data"),
        Index("ix_hora_extra_atividade_data", "obra_id", "atividade_id", "data"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trabalhador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    atividade_id: Mapped[str] = mapped_column(String(36), nullable=False)
    taxa_funcao_id: Mapped[str] = mapped_column(String(36), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    horas: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    tipo_dia: Mapped[TipoDia] = mapped_column(
        SqlEnum(
            TipoDia,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="tipo_dia_hora_extra",
            create_constraint=True,
        ),
        nullable=False,
    )
    taxa_aplicada: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_calculado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
