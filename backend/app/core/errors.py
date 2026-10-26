import logging
from collections.abc import Sequence
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Sequence[dict[str, Any]] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": list(details or []),
            }
        },
    )


async def validation_error_handler(
    request: Request, exception: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in issue["loc"] if part != "body"),
            "message": issue["msg"],
            "code": issue["type"],
        }
        for issue in exception.errors()
    ]
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Um ou mais campos são inválidos.",
        details=details,
    )


async def http_error_handler(
    request: Request, exception: StarletteHTTPException
) -> JSONResponse:
    detail = exception.detail
    if isinstance(detail, dict):
        code = str(detail.get("code", "HTTP_ERROR"))
        message = str(detail.get("message", "A solicitação não pôde ser atendida."))
    elif isinstance(detail, str):
        code = "HTTP_ERROR"
        message = detail
    else:
        code = "HTTP_ERROR"
        message = "A solicitação não pôde ser atendida."

    return _error_response(
        status_code=exception.status_code,
        code=code,
        message=message,
        details=[],
    )


async def unexpected_error_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.error("Erro interno inesperado (%s).", type(exception).__name__)
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        message="Ocorreu um erro interno. Tente novamente.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
