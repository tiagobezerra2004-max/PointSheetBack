from uuid import uuid4

from sqlalchemy import Boolean, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Funcao(TimestampMixin, Base):
    __tablename__ = "funcao"
    __table_args__ = (
        UniqueConstraint("obra_id", "id", name="uq_funcao_obra_id"),
        UniqueConstraint("obra_id", "nome", name="uq_funcao_obra_nome"),
        ForeignKeyConstraint(["obra_id"], ["obra.id"], name="fk_funcao_obra_id_obra"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    permite_hora_extra: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
