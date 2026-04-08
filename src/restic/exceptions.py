from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from httpx import Response
    from pydantic import BaseModel

    from restic.status_codes import HttpStatusCode


class ResticError(Exception):
    pass


class ResticInvalidUrlError(ResticError):
    pass


class ResticInvalidJsonError(ResticError):
    pass


class ResticResponseSchemaError(ResticError):
    def __init__(
        self,
        message: str,
        response_data: Any,
        expected_result_type: type[BaseModel],
    ) -> None:
        super().__init__(message)
        self.response_data = response_data
        self.expected_result_type = expected_result_type


class ResticHttpError(ResticError):
    def __init__(self, status_code: HttpStatusCode, response: Response) -> None:
        super().__init__(status_code)
        self.status_code = status_code
        self.response = response
