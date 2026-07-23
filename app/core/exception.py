from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse


class SuiError(Exception):
    status_code = 500
    detail = "Internal Server Error"


async def handle_sui_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    error = cast(SuiError, exc)

    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.detail},
    )
