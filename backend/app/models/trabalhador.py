from datetime import date
from uuid import uuid4

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin


class Trabalhador(SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "trabalhador"
    __table_args__ = (
        UniqueConstraint("cpf_hash", name="uq_trabalhador_cpf_hash"),
        Index("ix_trabalhador_nome", "nome"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_cifrado: Mapped[str] = mapped_column(Text, nullable=False)
    cpf_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(nullable=False)
    telefone_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
