from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, Field

from restic.exceptions import ResticHttpError, ResticResponseSchemaError
from restic.routes.mixins import ListMixin

if TYPE_CHECKING:
    import httpx

    from tests.conftest import BuildResponseFn


class QueryParamsModel(BaseModel):
    display_name: str = Field(alias="displayName")
    optional_value: int | None = None

    model_config = {"populate_by_name": True}


class ListResponseModel(BaseModel):
    items: list[int]


@pytest.fixture(name="list_mixin")
def list_mixin_fixture(client: httpx.Client, async_client: httpx.AsyncClient) -> ListMixin:
    return ListMixin(client, async_client)


def test_validate_list_result_model(list_mixin: ListMixin) -> None:
    response_data = {"items": [1, 2, 3]}
    result = list_mixin._validate_list_result_model(response_data, ListResponseModel)
    assert result.model_dump() == response_data


def test_handle_list_response(list_mixin: ListMixin, build_response: BuildResponseFn) -> None:
    response_data = {"items": [1, 2, 3]}
    response = build_response(json=response_data)

    result = list_mixin._handle_list_response(response, ListResponseModel)
    assert result.model_dump() == response_data


def test_handle_list_response_raises_restic_http_error(
    list_mixin: ListMixin, build_response: BuildResponseFn
) -> None:
    status_code = 400
    response = build_response(status_code=status_code, json={"error": "Bad Request"})

    with pytest.raises(ResticHttpError) as exc_info:
        list_mixin._handle_list_response(response, ListResponseModel)

    error = exc_info.value
    assert error.status_code == status_code
    assert error.response is response


def test_handle_list_response_raises_response_schema_error_for_invalid_response(
    list_mixin: ListMixin, build_response: BuildResponseFn
) -> None:
    response_data = {"unexpected": "data"}
    response = build_response(json=response_data)

    with pytest.raises(ResticResponseSchemaError) as exc_info:
        list_mixin._handle_list_response(response, ListResponseModel)

    error = exc_info.value
    assert error.response_data == response_data
    assert error.expected_result_type is ListResponseModel


def test_make_list_result_model(list_mixin: ListMixin) -> None:
    response_data = {"items": [1, 2, 3]}
    result = list_mixin._make_list_result_model(response_data, ListResponseModel)
    assert result.model_dump() == response_data


def test_make_list_result_model_raises_response_schema_error(list_mixin: ListMixin) -> None:
    response_data = {"unexpected": "data"}

    with pytest.raises(ResticResponseSchemaError) as exc_info:
        list_mixin._make_list_result_model(response_data, ListResponseModel)

    error = exc_info.value
    assert error.response_data == response_data
    assert error.expected_result_type is ListResponseModel


def test_make_query_params_returns_empty_dict_when_params_is_none(list_mixin: ListMixin) -> None:
    assert list_mixin._make_query_params(None) == {}


def test_make_query_params_serializes_base_model(list_mixin: ListMixin) -> None:
    params_dict = {"displayName": "value"}
    params = QueryParamsModel.model_validate(params_dict)

    assert list_mixin._make_query_params(params) == params_dict
