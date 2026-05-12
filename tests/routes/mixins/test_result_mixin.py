from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, ValidationError

from restic.exceptions import ResticResponseSchemaError
from restic.routes.mixins import ResultMixin

if TYPE_CHECKING:
    import httpx

    from tests.conftest import BuildResponseFn


class MockResultModel(BaseModel):
    key: str


@pytest.fixture(name="result_mixin")
def result_mixin_fixture(client: httpx.Client, async_client: httpx.AsyncClient) -> ResultMixin:
    return ResultMixin(client, async_client)


def test_handle_response(result_mixin: ResultMixin, build_response: BuildResponseFn) -> None:
    response_data = {"key": "value"}
    response = build_response(json=response_data)

    result = result_mixin._handle_response(response, MockResultModel)
    assert result.model_dump() == response_data


def test_make_result_model(result_mixin: ResultMixin) -> None:
    response_data = {"key": "value"}
    result = result_mixin._make_result_model(response_data, MockResultModel)
    assert result.model_dump() == response_data


def test_raise_response_schema_error(result_mixin: ResultMixin) -> None:
    response_data = {"unexpected": "data"}
    exc = ValidationError.from_exception_data(
        "Foobar",
        [
            {
                "type": "missing",
                "loc": ("key",),
                "input": None,
            }
        ],
    )
    with pytest.raises(ResticResponseSchemaError):
        result_mixin._raise_response_schema_error(response_data, exc, MockResultModel)
