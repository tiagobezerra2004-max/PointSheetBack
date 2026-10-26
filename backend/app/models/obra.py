from uuid import uuid4

from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Obra(TimestampMixin, Base):
    __tablename__ = "obra"
    __table_args__ = (UniqueConstraint("nome", name="uq_obra_nome"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
