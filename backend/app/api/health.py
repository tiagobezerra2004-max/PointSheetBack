from fastapi import APIRouter, HTTPException, status

from app.core.database import DatabaseUnavailable, check_database_connection

router = APIRouter(tags=["Saúde"])


@router.get("/health", summary="Verifica a disponibilidade da API e do banco")
def health_check() -> dict[str, str]:
    try:
        check_database_connection()
    except DatabaseUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "DATABASE_UNAVAILABLE",
                "message": "O banco de dados está indisponível.",
            },
        ) from error

    return {"status": "ok"}
