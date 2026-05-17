from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, Field

from restic.routes.mixins import UploadMixin

if TYPE_CHECKING:
    import httpx


class RequestModel(BaseModel):
    first_name: str = Field(alias="firstName")
    optional_value: int | None = Field(alias="optionalValue")

    model_config = {"populate_by_name": True}


@pytest.fixture(name="upload_mixin")
def upload_mixin_fixture(client: httpx.Client, async_client: httpx.AsyncClient) -> UploadMixin:
    return UploadMixin(client, async_client)


def test_make_request_json_data_returns_none_when_model_is_none(upload_mixin: UploadMixin) -> None:
    assert upload_mixin._make_request_json_data(None) is None


def test_make_request_json_data_serializes_base_model(upload_mixin: UploadMixin) -> None:
    model = RequestModel.model_validate({"firstName": "Alice"})
    assert upload_mixin._make_request_json_data(model) == {"firstName": "Alice"}


def test_make_request_json_data_excludes_unset_values(upload_mixin: UploadMixin) -> None:
    data = {"firstName": "Bob"}
    model = RequestModel.model_validate(data)

    result_data = upload_mixin._make_request_json_data(model)
    assert result_data == data
    assert "optionalValue" not in result_data


def test_make_request_json_data_aliases_as_keys(upload_mixin: UploadMixin) -> None:
    model = RequestModel(first_name="Charlie", optional_value=42)

    result_data = upload_mixin._make_request_json_data(model)
    assert result_data == {"firstName": "Charlie", "optionalValue": 42}, result_data
