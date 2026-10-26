from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SqlEnum

from app.models.base import Base, TimestampMixin, Vinculo, utc_now_naive


class HistoricoFuncaoVinculo(TimestampMixin, Base):
    __tablename__ = "historico_funcao_vinculo"
    __table_args__ = (
        ForeignKeyConstraint(
            ["obra_id", "trabalhador_id"],
            ["trabalhador_obra.obra_id", "trabalhador_obra.trabalhador_id"],
            name="fk_historico_funcao_vinculo_vinculo_obra",
        ),
        ForeignKeyConstraint(
            ["obra_id", "funcao_anterior_id"],
            ["funcao.obra_id", "funcao.id"],
            name="fk_historico_funcao_vinculo_funcao_anterior",
        ),
        ForeignKeyConstraint(
            ["obra_id", "funcao_nova_id"],
            ["funcao.obra_id", "funcao.id"],
            name="fk_historico_funcao_vinculo_funcao_nova",
        ),
        ForeignKeyConstraint(
            ["autor_id"], ["usuario.id"], name="fk_historico_funcao_vinculo_autor"
        ),
        Index("ix_historico_funcao_vinculo_data", "obra_id", "trabalhador_id", "alterado_em"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trabalhador_id: Mapped[str] = mapped_column(String(36), nullable=False)
    funcao_anterior_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    funcao_nova_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    vinculo_anterior: Mapped[Vinculo | None] = mapped_column(
        SqlEnum(
            Vinculo,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="vinculo_anterior",
            create_constraint=True,
        ),
        nullable=True,
    )
    vinculo_novo: Mapped[Vinculo | None] = mapped_column(
        SqlEnum(
            Vinculo,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="vinculo_novo",
            create_constraint=True,
        ),
        nullable=True,
    )
    autor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    alterado_em: Mapped[datetime] = mapped_column(DateTime(), default=utc_now_naive, nullable=False)
