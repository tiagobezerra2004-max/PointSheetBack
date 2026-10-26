from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Atestado(TimestampMixin, Base):
    __tablename__ = "atestado"
    __table_args__ = (
        UniqueConstraint("obra_id", "id", name="uq_atestado_obra_id"),
        CheckConstraint("tamanho_bytes BETWEEN 1 AND 2097152", name="ck_atestado_tamanho"),
        CheckConstraint(
            "mime_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="ck_atestado_mime_type",
        ),
        ForeignKeyConstraint(
            ["obra_id", "presenca_id"],
            ["presenca.obra_id", "presenca.id"],
            name="fk_atestado_presenca_obra",
        ),
        Index("ix_atestado_obra_presenca", "obra_id", "presenca_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    presenca_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(40), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    referencia_privada: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
