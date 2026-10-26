import re
from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKeyConstraint, Index, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SqlEnum

from app.models.base import AcaoAuditoria, Base, utc_now_naive


class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = (
        ForeignKeyConstraint(["obra_id"], ["obra.id"], name="fk_auditoria_obra_id_obra"),
        ForeignKeyConstraint(["ator_id"], ["usuario.id"], name="fk_auditoria_ator_id_usuario"),
        Index("ix_auditoria_entidade", "obra_id", "entidade", "entidade_id", "criado_em"),
        Index("ix_auditoria_ator", "ator_id", "criado_em"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    obra_id: Mapped[str] = mapped_column(String(36), nullable=False)
    ator_id: Mapped[str] = mapped_column(String(36), nullable=False)
    entidade: Mapped[str] = mapped_column(String(50), nullable=False)
    entidade_id: Mapped[str] = mapped_column(String(36), nullable=False)
    acao: Mapped[AcaoAuditoria] = mapped_column(
        SqlEnum(
            AcaoAuditoria,
            values_callable=lambda values: [item.value for item in values],
            native_enum=False,
            length=20,
            name="acao_auditoria",
            create_constraint=True,
        ),
        nullable=False,
    )
    campo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_anterior: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    valor_novo: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(), default=utc_now_naive, nullable=False)


_SENSITIVE_FIELD_PARTS = ("cpf", "pix", "telefone", "banco", "titular")
_CPF_PATTERN = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
_PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?55[ .-]?)?(?:\(?\d{2}\)?[ .-]?)?9?\d{4}[ .-]?\d{4}(?!\w)"
)


def _redact_json(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if any(part in str(key).casefold().replace("_", "") for part in _SENSITIVE_FIELD_PARTS)
            else _redact_json(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_json(item) for item in value]
    if isinstance(value, str):
        return _PHONE_PATTERN.sub("[REDACTED]", _CPF_PATTERN.sub("[REDACTED]", value))
    return value


@event.listens_for(Auditoria, "before_insert")
@event.listens_for(Auditoria, "before_update")
def redact_sensitive_audit_values(mapper, connection, target: Auditoria) -> None:
    field_name = (target.campo or "").casefold().replace("_", "")
    if any(part in field_name for part in _SENSITIVE_FIELD_PARTS):
        target.valor_anterior = "[REDACTED]" if target.valor_anterior is not None else None
        target.valor_novo = "[REDACTED]" if target.valor_novo is not None else None
        target.motivo = "[REDACTED]" if target.motivo is not None else None
    else:
        target.valor_anterior = _redact_json(target.valor_anterior)
        target.valor_novo = _redact_json(target.valor_novo)
        target.motivo = _redact_json(target.motivo)
