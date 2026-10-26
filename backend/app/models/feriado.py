from datetime import date
from uuid import uuid4

from sqlalchemy import Date, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Feriado(TimestampMixin, Base):
    __tablename__ = "feriado"
    __table_args__ = (
        UniqueConstraint("obra_id", "data", name="uq_feriado_obra_data"),
        ForeignKeyConstraint(["obra_id"], ["obra.id"], name="fk_feriado_obra_id_obra"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str] = mapped_column(String(160), nullable=False)
