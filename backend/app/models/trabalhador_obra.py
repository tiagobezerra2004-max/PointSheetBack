from datetime import date
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SqlEnum

from app.models.base import Base, StatusTrabalhador, TimestampMixin, Vinculo


class TrabalhadorObra(TimestampMixin, Base):
    __tablename__ = "trabalhador_obra"
    __table_args__ = (
        UniqueConstraint("obra_id", "id", name="uq_trabalhador_obra_obra_id"),
        UniqueConstraint("obra_id", "trabalhador_id", name="uq_trabalhador_obra_pessoa"),
        UniqueConstraint("obra_id", "id_ponto", name="uq_trabalhador_obra_id_ponto"),
        CheckConstraint(
            "data_desligamento IS NULL OR data_desligamento >= data_admissao",
            name="ck_trabalhador_obra_datas_coerentes",
        ),
        CheckConstraint(
            "status <> 'Desligado' OR data_desligamento IS NOT NULL",
            name="ck_trabalhador_obra_desligamento_obrigatorio",
        ),
        ForeignKeyConstraint(
            ["obra_id", "funcao_id"],
            ["funcao.obra_id", "funcao.id"],
            name="fk_trabalhador_obra_funcao_obra",
        ),
        ForeignKeyConstraint(
            ["trabalhador_id"],
            ["trabalhador.id"],
            name="fk_trabalhador_obra_trabalhador",
        ),
        Index("ix_trabalhador_obra_status", "obra_id", "status"),
        Index("ix_trabalhador_obra_funcao", "obra_id", "funcao_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trabalhador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    id_ponto: Mapped[str | None] = mapped_column(String(80), nullable=True)
    funcao_id: Mapped[str] = mapped_column(String(36), nullable=False)
    vinculo: Mapped[Vinculo] = mapped_column(
        SqlEnum(
            Vinculo,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="vinculo",
            create_constraint=True,
        ),
        nullable=False,
    )
    status: Mapped[StatusTrabalhador] = mapped_column(
        SqlEnum(
            StatusTrabalhador,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="status_trabalhador",
            create_constraint=True,
        ),
        nullable=False,
    )
    data_admissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_desligamento: Mapped[date | None] = mapped_column(Date, nullable=True)
