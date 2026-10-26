from datetime import date
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SqlEnum

from app.models.base import Base, CodigoPresenca, OrigemPresenca, TimestampMixin


class Presenca(TimestampMixin, Base):
    __tablename__ = "presenca"
    __table_args__ = (
        UniqueConstraint(
            "obra_id", "trabalhador_id", "data", name="uq_presenca_obra_trabalhador_data"
        ),
        UniqueConstraint("obra_id", "id", name="uq_presenca_obra_id"),
        ForeignKeyConstraint(
            ["obra_id", "trabalhador_id"],
            ["trabalhador_obra.obra_id", "trabalhador_obra.trabalhador_id"],
            name="fk_presenca_trabalhador_obra",
        ),
        CheckConstraint(
            "(codigo = 'A' AND atestado_necessario = 1) OR "
            "(codigo <> 'A' AND atestado_necessario = 0)",
            name="ck_presenca_atestado_requerido",
        ),
        Index("ix_presenca_obra_data", "obra_id", "data"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trabalhador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    codigo: Mapped[CodigoPresenca] = mapped_column(
        SqlEnum(
            CodigoPresenca,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=2,
            name="codigo_presenca",
            create_constraint=True,
        ),
        nullable=False,
    )
    origem: Mapped[OrigemPresenca] = mapped_column(
        SqlEnum(
            OrigemPresenca,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=10,
            name="origem_presenca",
            create_constraint=True,
        ),
        nullable=False,
    )
    editada_manualmente: Mapped[bool] = mapped_column(default=False, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    atestado_necessario: Mapped[bool] = mapped_column(default=False, nullable=False)
