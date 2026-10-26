from uuid import uuid4

from sqlalchemy import Boolean, ForeignKeyConstraint, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Atividade(TimestampMixin, Base):
    __tablename__ = "atividade"
    __table_args__ = (
        UniqueConstraint("obra_id", "nome", name="uq_atividade_obra_nome"),
        ForeignKeyConstraint(["obra_id"], ["obra.id"], name="fk_atividade_obra_id_obra"),
        Index("ix_atividade_obra_ativa", "obra_id", "ativa"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
