from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.crypto import (
    cpf_fingerprint,
    decrypt_sensitive_value,
    encrypt_sensitive_value,
)
from app.models import (
    Atividade,
    Auditoria,
    CodigoPresenca,
    Funcao,
    Obra,
    OrigemPresenca,
    Presenca,
    StatusTrabalhador,
    TaxaFuncao,
    Trabalhador,
    TrabalhadorObra,
    TrabalhadorPagamento,
    Usuario,
    Vinculo,
)
from scripts.seed import seed


def add_worker(db_session, *, obra: Obra, cpf: str, point_id: str | None = None):
    worker = Trabalhador(
        nome="Trabalhador Fictício de Teste",
        cpf_cifrado=encrypt_sensitive_value(cpf),
        cpf_hash=cpf_fingerprint(cpf),
        data_nascimento=date(1990, 1, 1),
    )
    function = Funcao(obra_id=obra.id, nome=f"Função {cpf}")
    db_session.add_all([worker, function])
    db_session.flush()
    assignment = TrabalhadorObra(
        obra_id=obra.id,
        trabalhador_id=worker.id,
        id_ponto=point_id,
        funcao_id=function.id,
        vinculo=Vinculo.CLT,
        status=StatusTrabalhador.ATIVO,
        data_admissao=date(2024, 1, 1),
    )
    db_session.add(assignment)
    db_session.flush()
    return worker, assignment


def test_presence_is_unique_per_worker_and_date(db_session) -> None:
    obra = Obra(nome="Obra de teste")
    db_session.add(obra)
    db_session.flush()
    _, assignment = add_worker(db_session, obra=obra, cpf="52998224725")
    presence = Presenca(
        obra_id=obra.id,
        trabalhador_id=assignment.trabalhador_id,
        data=date(2026, 10, 22),
        codigo=CodigoPresenca.PRESENTE,
        origem=OrigemPresenca.MANUAL,
        editada_manualmente=True,
    )
    db_session.add(presence)
    db_session.commit()
    db_session.add(
        Presenca(
            obra_id=obra.id,
            trabalhador_id=assignment.trabalhador_id,
            data=date(2026, 10, 22),
            codigo=CodigoPresenca.FALTA,
            origem=OrigemPresenca.MANUAL,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_point_identifier_is_unique_per_project(db_session) -> None:
    first_work = Obra(nome="Primeira obra")
    second_work = Obra(nome="Segunda obra")
    db_session.add_all([first_work, second_work])
    db_session.flush()
    _, first_assignment = add_worker(
        db_session, obra=first_work, cpf="52998224725", point_id="PONTO-0001"
    )
    _, second_assignment = add_worker(
        db_session, obra=second_work, cpf="16899535009", point_id="PONTO-0001"
    )
    assert first_assignment.id_ponto == second_assignment.id_ponto
    db_session.commit()

    with pytest.raises(IntegrityError):
        add_worker(db_session, obra=first_work, cpf="11144477735", point_id="PONTO-0001")
        db_session.commit()


def test_duplicate_cpf_is_blocked_by_fingerprint(db_session) -> None:
    work = Obra(nome="Obra de CPF")
    db_session.add(work)
    db_session.flush()
    add_worker(db_session, obra=work, cpf="529.982.247-25")
    db_session.commit()

    duplicate = Trabalhador(
        nome="Outro Trabalhador Fictício",
        cpf_cifrado=encrypt_sensitive_value("52998224725"),
        cpf_hash=cpf_fingerprint("52998224725"),
        data_nascimento=date(1990, 1, 1),
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_soft_delete_keeps_worker_row(db_session) -> None:
    worker = Trabalhador(
        nome="Trabalhador Fictício Removido",
        cpf_cifrado=encrypt_sensitive_value("00000000000"),
        cpf_hash=cpf_fingerprint("00000000000"),
        data_nascimento=date(1990, 1, 1),
    )
    db_session.add(worker)
    db_session.commit()
    worker.soft_delete()
    db_session.commit()

    assert worker.excluido_em is not None
    assert db_session.get(Trabalhador, worker.id) is worker


def test_cpf_encryption_round_trip() -> None:
    cpf = "529.982.247-25"

    encrypted = encrypt_sensitive_value(cpf)

    assert encrypted != cpf
    assert decrypt_sensitive_value(encrypted) == cpf


def test_audit_redacts_sensitive_field_values(db_session) -> None:
    work = Obra(nome="Obra de auditoria")
    user = Usuario(email="admin@example.invalid", nome="Usuário Fictício")
    db_session.add_all([work, user])
    db_session.flush()
    audit = Auditoria(
        obra_id=work.id,
        ator_id=user.id,
        entidade="trabalhador",
        entidade_id="trabalhador-ficticio",
        acao="edicao",
        campo="cpf",
        valor_anterior="529.982.247-25",
        valor_novo="111.444.777-35",
        motivo="Atualização com chave PIX fictícia",
    )
    db_session.add(audit)
    db_session.flush()

    assert audit.valor_anterior == "[REDACTED]"
    assert audit.valor_novo == "[REDACTED]"
    assert audit.motivo == "[REDACTED]"


def test_audit_redacts_sensitive_nested_values(db_session) -> None:
    work = Obra(nome="Obra de auditoria aninhada")
    user = Usuario(email="admin-nested@example.invalid", nome="Usuário Fictício")
    db_session.add_all([work, user])
    db_session.flush()
    audit = Auditoria(
        obra_id=work.id,
        ator_id=user.id,
        entidade="trabalhador",
        entidade_id="trabalhador-ficticio",
        acao="edicao",
        campo="pagamento",
        valor_anterior={
            "chave_pix": "chave-ficticia",
            "banco": "Banco Fictício",
            "titular_da_chave": "Titular Fictício",
            "observacao": "Contato fictício +55 (11) 98765-4321",
        },
        valor_novo={"telefone": "+55 00 00000-0000"},
        motivo="Atualizou dados cadastrais",
    )
    db_session.add(audit)
    db_session.flush()

    assert audit.valor_anterior == {
        "chave_pix": "[REDACTED]",
        "banco": "[REDACTED]",
        "titular_da_chave": "[REDACTED]",
        "observacao": "Contato fictício [REDACTED]",
    }
    assert audit.valor_novo == {"telefone": "[REDACTED]"}
    assert audit.motivo == "Atualizou dados cadastrais"


def test_seed_is_idempotent_and_contains_only_synthetic_workers(db_engine) -> None:
    from sqlalchemy import func, select
    from sqlalchemy.orm import Session

    seed(db_engine)
    seed(db_engine)

    with Session(db_engine) as session:
        assert session.scalar(select(func.count()).select_from(Trabalhador)) == 30
        assert session.scalar(select(func.count()).select_from(Atividade)) == 9
        assert session.scalar(select(func.count()).select_from(TaxaFuncao)) == 10
        assert (
            session.scalar(
                select(func.count())
                .select_from(TrabalhadorObra)
                .where(TrabalhadorObra.status == StatusTrabalhador.DESLIGADO)
            )
            == 1
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(TrabalhadorObra)
                .where(TrabalhadorObra.id_ponto.is_(None))
            )
            == 10
        )
        assert session.scalar(select(func.count()).select_from(TrabalhadorPagamento)) == 29
        similar_names = session.scalars(
            select(Trabalhador.nome).where(Trabalhador.nome.like("%Similar%"))
        ).all()
        assert len(similar_names) == 2
