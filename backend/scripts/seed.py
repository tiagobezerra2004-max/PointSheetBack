from datetime import date
from decimal import Decimal
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.crypto import cpf_fingerprint, encrypt_sensitive_value
from app.core.database import engine
from app.models import (
    Atividade,
    Funcao,
    Obra,
    StatusTrabalhador,
    TaxaFuncao,
    Trabalhador,
    TrabalhadorObra,
    TrabalhadorPagamento,
    Vinculo,
)

OBRA_NOME = "Obra Frei Humberto I"
INICIO_VIGENCIA = date(2026, 1, 1)
FUNCOES = [
    ("ajudante", "Ajudante de obra", "1621.00", "11.79", "12.23"),
    ("pedreiro", "Pedreiro", "2230.00", "16.22", "16.83"),
    ("eletricista", "Eletricista", "2230.00", "16.22", "16.83"),
    ("ferreiro", "Ferreiro", "2230.00", "16.22", "16.83"),
    ("bombeiro", "Bombeiro", "2230.00", "16.22", "16.83"),
    ("encarregado", "Encarregado", "2620.00", "19.05", "19.77"),
    ("tecnico", "Técnico em edificações", "5947.99", "43.26", "44.88"),
    ("estagiario", "Estagiário", "500.00", "3.64", "3.77"),
    ("aprendiz", "Jovem aprendiz", None, "11.78", "12.23"),
    ("vigia", "Vigia", "1680.00", "12.22", "12.68"),
]
ATIVIDADES = [
    ("pista", "Pista"),
    ("pista-radier", "Pista radier"),
    ("laje", "Laje"),
    ("argamassa", "Argamassa"),
    ("ferragem", "Ferragem das casas"),
    ("descarregamento", "Descarregando caminhão"),
    ("montagem", "Montagem de casa"),
    ("vigia", "Vigia"),
    ("outros", "Outros"),
]


def stable_id(kind: str, key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"pointsheet:{kind}:{key}"))


def make_fake_cpf(index: int) -> str:
    digits = [int(character) for character in f"{900_000_000 + index:09d}"]
    for length in (9, 10):
        weight = length + 1
        remainder = (
            sum(digit * (weight - position) for position, digit in enumerate(digits[:length])) % 11
        )
        digits.append(0 if remainder < 2 else 11 - remainder)
    return "".join(map(str, digits))


def add_reference_data(session: Session, obra: Obra) -> dict[str, Funcao]:
    functions: dict[str, Funcao] = {}
    for key, name, base_salary, weekday_rate, saturday_rate in FUNCOES:
        function_id = stable_id("funcao", key)
        function = session.get(Funcao, function_id)
        if function is None:
            function = Funcao(
                id=function_id,
                obra_id=obra.id,
                nome=name,
                permite_hora_extra=True,
            )
            session.add(function)
            session.flush()
        functions[key] = function

        rate_id = stable_id("taxa-funcao", key)
        if session.get(TaxaFuncao, rate_id) is None:
            session.add(
                TaxaFuncao(
                    id=rate_id,
                    obra_id=obra.id,
                    funcao_id=function.id,
                    vigente_desde=INICIO_VIGENCIA,
                    salario_base=Decimal(base_salary) if base_salary else None,
                    divisor=Decimal("220.00") if base_salary else None,
                    multiplicador=Decimal("1.6000") if base_salary else None,
                    valor_hora_semana=Decimal(weekday_rate),
                    valor_hora_sabado=Decimal(saturday_rate),
                    valor_hora_domingo_feriado=None,
                )
            )

    for key, name in ATIVIDADES:
        activity_id = stable_id("atividade", key)
        if session.get(Atividade, activity_id) is None:
            session.add(Atividade(id=activity_id, obra_id=obra.id, nome=name, ativa=True))

    session.flush()
    return functions


def add_fake_workers(session: Session, obra: Obra, functions: dict[str, Funcao]) -> None:
    for index in range(1, 31):
        worker_id = stable_id("trabalhador", f"{index:03d}")
        worker = session.get(Trabalhador, worker_id)
        cpf = make_fake_cpf(index)
        cpf_hash = cpf_fingerprint(cpf)
        if worker is None:
            existing_worker = session.scalar(
                select(Trabalhador).where(Trabalhador.cpf_hash == cpf_hash)
            )
            if existing_worker is not None:
                worker = existing_worker
            else:
                worker = Trabalhador(
                    id=worker_id,
                    nome=(
                        "Trabalhador Fictício Similar A"
                        if index == 1
                        else "Trabalhador Fictício Similar B"
                        if index == 2
                        else f"Trabalhador Fictício {index:02d}"
                    ),
                    cpf_cifrado=encrypt_sensitive_value(cpf),
                    cpf_hash=cpf_hash,
                    data_nascimento=date(1990, 1, 1),
                    telefone_cifrado=encrypt_sensitive_value(f"+55 00 00000-{index:04d}"),
                )
                session.add(worker)
                session.flush()

        assignment_id = stable_id("trabalhador-obra", f"{obra.id}:{worker.id}")
        assignment = session.get(TrabalhadorObra, assignment_id)
        if assignment is None:
            is_avulso = index <= 10
            is_discharged = index == 30
            function_key = FUNCOES[(index - 1) % len(FUNCOES)][0]
            assignment = TrabalhadorObra(
                id=assignment_id,
                obra_id=obra.id,
                trabalhador_id=worker.id,
                id_ponto=None if is_avulso else f"PONTO-{index:05d}",
                funcao_id=functions[function_key].id,
                vinculo=Vinculo.AVULSO if is_avulso else Vinculo.CLT,
                status=StatusTrabalhador.DESLIGADO if is_discharged else StatusTrabalhador.ATIVO,
                data_admissao=date(2024, 1, 1),
                data_desligamento=date(2025, 12, 19) if is_discharged else None,
            )
            session.add(assignment)
            session.flush()

        if (
            index != 5
            and session.get(TrabalhadorPagamento, {"obra_id": obra.id, "trabalhador_id": worker.id})
            is None
        ):
            session.add(
                TrabalhadorPagamento(
                    obra_id=obra.id,
                    trabalhador_id=worker.id,
                    tipo_chave="Email",
                    chave_pix_cifrada=encrypt_sensitive_value(
                        f"trabalhador{index}@example.invalid"
                    ),
                    banco_cifrado=encrypt_sensitive_value("Banco Fictício"),
                    titular_da_chave=worker.nome,
                    chave_em_nome_de_terceiro=False,
                )
            )


def seed(database_engine: Engine = engine) -> None:
    session_factory = sessionmaker(bind=database_engine)
    with session_factory.begin() as session:
        obra_id = stable_id("obra", "frei-humberto-i")
        obra = session.get(Obra, obra_id)
        if obra is None:
            obra = Obra(id=obra_id, nome=OBRA_NOME, ativa=True)
            session.add(obra)
            session.flush()

        functions = add_reference_data(session, obra)
        add_fake_workers(session, obra, functions)


if __name__ == "__main__":
    seed()
