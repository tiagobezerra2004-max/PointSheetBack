from sqlalchemy import CheckConstraint, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TrabalhadorPagamento(TimestampMixin, Base):
    __tablename__ = "trabalhador_pagamento"
    __table_args__ = (
        CheckConstraint(
            "tipo_chave IN ('CPF', 'Telefone', 'Email', 'Aleatoria')",
            name="ck_trabalhador_pagamento_tipo_chave",
        ),
        ForeignKeyConstraint(
            ["obra_id", "trabalhador_id"],
            ["trabalhador_obra.obra_id", "trabalhador_obra.trabalhador_id"],
            name="fk_trabalhador_pagamento_vinculo_obra",
            ondelete="CASCADE",
        ),
    )

    obra_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trabalhador_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tipo_chave: Mapped[str] = mapped_column(String(20), nullable=False)
    chave_pix_cifrada: Mapped[str] = mapped_column(String(512), nullable=False)
    banco_cifrado: Mapped[str] = mapped_column(String(512), nullable=False)
    titular_da_chave: Mapped[str] = mapped_column(String(200), nullable=False)
    chave_em_nome_de_terceiro: Mapped[bool] = mapped_column(nullable=False)
