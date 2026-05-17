from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, ValidationError

from restic.exceptions import ResticInvalidJsonError, ResticResponseSchemaError
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


def test_handle_response_raises_response_schema_error_for_invalid_response(
    result_mixin: ResultMixin, build_response: BuildResponseFn
) -> None:
    response = build_response(json={"unexpected": "data"})

    with pytest.raises(ResticResponseSchemaError) as exc_info:
        result_mixin._handle_response(response, MockResultModel)

    error = exc_info.value
    assert error.response_data == {"unexpected": "data"}
    assert error.expected_result_type is MockResultModel


def test_handle_response_raises_invalid_json_error_for_empty_body(
    result_mixin: ResultMixin, build_response: BuildResponseFn
) -> None:
    response = build_response(content=b"", headers={"Content-Type": "application/json"})

    with pytest.raises(ResticInvalidJsonError):
        result_mixin._handle_response(response, MockResultModel)


def test_make_result_model(result_mixin: ResultMixin) -> None:
    response_data = {"key": "value"}
    result = result_mixin._make_result_model(response_data, MockResultModel)
    assert result.model_dump() == response_data


def test_make_result_model_raises_response_schema_error(result_mixin: ResultMixin) -> None:
    response_data = {"unexpected": "data"}

    with pytest.raises(ResticResponseSchemaError) as exc_info:
        result_mixin._make_result_model(response_data, MockResultModel)

    error = exc_info.value
    assert error.response_data == response_data
    assert error.expected_result_type is MockResultModel
    assert str(error) == "Received unexpected response from server"


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


def test_raise_response_schema_error_sets_expected_type_and_message(
    result_mixin: ResultMixin,
) -> None:
    response_data = {"unexpected": "data"}
    validation_error = ValidationError.from_exception_data(
        "Validation failed",
        [
            {
                "type": "missing",
                "loc": ("key",),
                "input": None,
            }
        ],
    )

    with pytest.raises(ResticResponseSchemaError) as exc_info:
        result_mixin._raise_response_schema_error(response_data, validation_error, MockResultModel)

    error = exc_info.value
    assert error.response_data == response_data
    assert error.expected_result_type is MockResultModel
    assert str(error) == "Received unexpected response from server"
