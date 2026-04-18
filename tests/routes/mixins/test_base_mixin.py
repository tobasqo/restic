from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from httpx._status_codes import codes

from restic.routes.mixins import BaseMixin

if TYPE_CHECKING:
    import httpx

    from tests.conftest import MockResponseFn


@pytest.fixture(name="base_mixin")
def base_mixin_fixture(client: httpx.Client, async_client: httpx.AsyncClient) -> BaseMixin:
    return BaseMixin(client, async_client)


def test_send_request_get_success(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response()

    response = base_mixin._send_request("GET", "/")
    assert response.status_code == codes.OK


def test_send_request_post_with_json(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    request_data = {"key": "value"}
    response_data = {"id": 1, "key": "value"}

    mock_response(method="POST", status_code=codes.CREATED, json=response_data)

    response = base_mixin._send_request("POST", "/", json=request_data)
    assert response.status_code == codes.CREATED
    assert response.json() == response_data


def test_send_request_with_params(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    params = {"filter": "active", "limit": 10}
    data: dict[str, Any] = {"results": []}

    mock_response(json=data)

    response = base_mixin._send_request("GET", "/", params=params)
    assert response.status_code == codes.OK
    assert response.request.url.query == b"filter=active&limit=10"
    assert response.json() == data


def test_send_request_with_custom_headers(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    headers = {"Authorization": "Bearer token123"}

    mock_response()

    response = base_mixin._send_request("GET", "/", headers=headers)
    request = response.request
    assert request.headers["Authorization"] == "Bearer token123"
    assert request.headers["Content-Type"] == "application/json"


def test_send_request_put_method(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    request_data = {"name": "updated"}
    response_data = {"id": 1, "name": "updated"}

    mock_response(method="PUT", status_code=codes.OK, json=response_data)

    response = base_mixin._send_request("PUT", "/1", json=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


def test_send_request_patch_method(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    request_data = {"status": "inactive"}
    response_data = {"id": 1, "status": "inactive"}

    mock_response(method="PATCH", status_code=codes.OK, json=response_data)

    response = base_mixin._send_request("PATCH", "/1", json=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


def test_send_request_delete_method(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="DELETE", status_code=codes.NO_CONTENT)

    response = base_mixin._send_request("DELETE", "/1")
    assert response.status_code == codes.NO_CONTENT


# ============================================================================
# Tests for _send_request - Negative scenarios (HTTP errors)
# ============================================================================


@pytest.mark.parametrize(
    "status_code",
    [
        codes.BAD_REQUEST,
        codes.UNAUTHORIZED,
        codes.FORBIDDEN,
        codes.NOT_FOUND,
        codes.CONFLICT,
    ],
)
def test_send_request_client_errors(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(status_code=status_code, json={"error": "error message"})

    response = base_mixin._send_request("GET", "/")
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "status_code",
    [
        codes.INTERNAL_SERVER_ERROR,
        codes.BAD_GATEWAY,
        codes.SERVICE_UNAVAILABLE,
    ],
)
def test_send_request_server_errors(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(
        status_code=status_code,
        json={"error": "server error"},
    )

    response = base_mixin._send_request("GET", "/")
    assert response.status_code == status_code
