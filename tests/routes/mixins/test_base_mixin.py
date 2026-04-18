from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
import pytest
from httpx._status_codes import codes

from restic.exceptions import ResticHttpError, ResticInvalidJsonError
from restic.routes.mixins import BaseMixin

if TYPE_CHECKING:
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

    mock_response(method="PUT", json=response_data)

    response = base_mixin._send_request("PUT", "/1", json=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


def test_send_request_patch_method(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    request_data = {"status": "inactive"}
    response_data = {"id": 1, "status": "inactive"}

    mock_response(method="PATCH", json=response_data)

    response = base_mixin._send_request("PATCH", "/1", json=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


def test_send_request_delete_method(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="DELETE", status_code=codes.NO_CONTENT)

    response = base_mixin._send_request("DELETE", "/1")
    assert response.status_code == codes.NO_CONTENT


# ============================================================================
# Tests for additional parameters in request methods
# ============================================================================


def test_send_request_with_content(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    content = b"raw data"

    mock_response(content=content)

    response = base_mixin._send_request("POST", "/", content=content)
    assert response.status_code == codes.OK


def test_send_request_with_data(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    request_data = {"key": "value"}
    response_data = {"received": True}

    mock_response(json=response_data)

    response = base_mixin._send_request("POST", "/", data=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


def test_send_request_with_files(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    files = {"file": ("filename.txt", b"file content")}

    mock_response(json={"uploaded": True})

    response = base_mixin._send_request("POST", "/", files=files)
    assert response.status_code == codes.OK
    assert response.json() == {"uploaded": True}


def test_send_request_with_follow_redirects(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(status_code=codes.FOUND, headers={"Location": "/redirect"})

    response = base_mixin._send_request("GET", "/", follow_redirects=False)
    assert response.status_code == codes.FOUND


def test_send_request_with_kwargs(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response()

    response = base_mixin._send_request("GET", "/", timeout=10.0)
    assert response.status_code == codes.OK


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
    mock_response(status_code=status_code, json={"error": "server error"})

    response = base_mixin._send_request("GET", "/")
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "status_code",
    [
        codes.MOVED_PERMANENTLY,
        codes.FOUND,
        codes.SEE_OTHER,
    ],
)
def test_check_api_error_redirects(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(status_code=status_code, json={"redirect": True})

    response = base_mixin._send_request("GET", "/", follow_redirects=False)
    # Should not raise since follow_redirects=False
    base_mixin._check_api_error(response)


@pytest.mark.parametrize(
    "status_code",
    [
        codes.CONTINUE,
        codes.SWITCHING_PROTOCOLS,
        codes.PROCESSING,
    ],
)
def test_check_api_error_informational(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(status_code=status_code, json={"info": True})

    response = base_mixin._send_request("GET", "/")
    # Should not raise for 1xx codes
    base_mixin._check_api_error(response)


def test_check_api_error_includes_response_text(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    error_text = "Detailed server error message"

    mock_response(status_code=codes.INTERNAL_SERVER_ERROR, content=error_text.encode())

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticHttpError) as exc_info:
        base_mixin._check_api_error(response)

    assert error_text in str(exc_info.value)


# ============================================================================
# Tests for _stream_request
# ============================================================================


def test_stream_request_get_success(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(content=b"streaming data")

    with base_mixin._stream_request("GET", "/stream") as response:
        assert response.status_code == codes.OK
        assert response.read() == b"streaming data"


def test_stream_request_with_headers(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(content=b"streaming data")

    with base_mixin._stream_request("GET", "/stream", headers={"Accept": "text/plain"}) as response:
        assert response.status_code == codes.OK
        assert response.request.headers.get("Accept") == "text/plain"


def test_stream_request_post(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="POST", status_code=codes.ACCEPTED, content=b"accepted")

    with base_mixin._stream_request("POST", "/stream", json={"data": "value"}) as response:
        assert response.status_code == codes.ACCEPTED


def test_stream_request_put(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="PUT", content=b"updated")

    with base_mixin._stream_request("PUT", "/stream", json={"update": True}) as response:
        assert response.status_code == codes.OK


def test_stream_request_patch(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="PATCH", content=b"patched")

    with base_mixin._stream_request("PATCH", "/stream", json={"patch": True}) as response:
        assert response.status_code == codes.OK


def test_stream_request_delete(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(method="DELETE", status_code=codes.NO_CONTENT, content=b"")

    with base_mixin._stream_request("DELETE", "/stream") as response:
        assert response.status_code == codes.NO_CONTENT


def test_stream_request_with_content(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    content = b"streaming content"

    mock_response(method="POST")

    with base_mixin._stream_request("POST", "/stream", content=content) as response:
        assert response.status_code == codes.OK


def test_stream_request_with_data(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    data = {"stream": "data"}

    mock_response(method="POST")

    with base_mixin._stream_request("POST", "/stream", data=data) as response:
        assert response.status_code == codes.OK


def test_stream_request_with_files(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    files = {"upload": ("file.txt", b"content")}

    mock_response(method="POST")

    with base_mixin._stream_request("POST", "/stream", files=files) as response:
        assert response.status_code == codes.OK


def test_stream_request_with_params(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    params = {"type": "stream"}

    mock_response()

    with base_mixin._stream_request("GET", "/stream", params=params) as response:
        assert response.status_code == codes.OK


def test_stream_request_with_json(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    json_data = {"stream": True}

    mock_response(method="POST")

    with base_mixin._stream_request("POST", "/stream", json=json_data) as response:
        assert response.status_code == codes.OK


# ============================================================================
# Tests for _async_send_request
# ============================================================================


@pytest.mark.asyncio
async def test_async_send_request_get_success(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    data = {"message": "success"}

    mock_response(json=data)

    response = await base_mixin._async_send_request("GET", "/")
    assert response.status_code == codes.OK
    assert response.json() == data


@pytest.mark.asyncio
async def test_async_send_request_post_with_json(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    request_data = {"key": "value"}
    response_data = {"id": 1, "key": "value"}

    mock_response(method="POST", status_code=codes.CREATED, json=response_data)

    response = await base_mixin._async_send_request("POST", "/", json=request_data)
    assert response.status_code == codes.CREATED
    assert response.json() == response_data


@pytest.mark.asyncio
async def test_async_send_request_with_params(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    params = {"page": 1}
    mock_response(json={"data": []})

    response = await base_mixin._async_send_request("GET", "/", params=params)
    assert response.status_code == codes.OK
    assert response.request.url.query == b"page=1"


@pytest.mark.asyncio
async def test_async_send_request_with_custom_headers(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(json={})

    response = await base_mixin._async_send_request("GET", "/", headers={"X-Custom": "value"})
    assert response.request.headers["X-Custom"] == "value"
    assert response.status_code == codes.OK
    assert response.json() == {}


@pytest.mark.asyncio
async def test_async_send_request_with_content(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    content = b"async raw data"

    mock_response(content=content)

    response = await base_mixin._async_send_request("POST", "/", content=content)
    assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_send_request_with_data(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    request_data = {"async": "data"}
    response_data = {"received": True}

    mock_response(json=response_data)

    response = await base_mixin._async_send_request("POST", "/", data=request_data)
    assert response.status_code == codes.OK
    assert response.json() == response_data


@pytest.mark.asyncio
async def test_async_send_request_with_files(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    files = {"async_file": ("async.txt", b"async content")}
    response_data = {"uploaded": True}

    mock_response(json=response_data)

    response = await base_mixin._async_send_request("POST", "/", files=files)
    assert response.status_code == codes.OK
    assert response.json() == response_data


@pytest.mark.asyncio
async def test_async_send_request_with_follow_redirects(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(status_code=codes.FOUND, headers={"Location": "/async_redirect"})

    response = await base_mixin._async_send_request("GET", "/", follow_redirects=False)
    assert response.status_code == codes.FOUND


@pytest.mark.asyncio
async def test_async_send_request_with_kwargs(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response()

    response = await base_mixin._async_send_request("GET", "/", timeout=5.0)
    assert response.status_code == codes.OK


# ============================================================================
# Tests for _async_stream_request
# ============================================================================


@pytest.mark.asyncio
async def test_async_stream_request_get_success(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(content=b"streaming data")

    async with base_mixin._async_stream_request("GET", "/stream") as response:
        assert response.status_code == codes.OK
        content = await response.aread()
        assert content == b"streaming data"


@pytest.mark.asyncio
async def test_async_stream_request_post(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(method="POST", status_code=codes.ACCEPTED, content=b"accepted")

    async with base_mixin._async_stream_request(
        "POST", "/stream", json={"data": "test"}
    ) as response:
        assert response.status_code == codes.ACCEPTED
        assert await response.aread() == b"accepted"


@pytest.mark.asyncio
async def test_async_stream_request_put(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(method="PUT", content=b"async updated")

    async with base_mixin._async_stream_request(
        "PUT", "/stream", json={"update": True}
    ) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_patch(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(method="PATCH", content=b"async patched")

    async with base_mixin._async_stream_request(
        "PATCH", "/stream", json={"patch": True}
    ) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_delete(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(method="DELETE", status_code=codes.NO_CONTENT, content=b"")

    async with base_mixin._async_stream_request("DELETE", "/stream") as response:
        assert response.status_code == codes.NO_CONTENT


@pytest.mark.asyncio
async def test_async_stream_request_with_content(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    content = b"async streaming content"

    mock_response(method="POST")

    async with base_mixin._async_stream_request("POST", "/stream", content=content) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_with_data(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    data = {"async_stream": "data"}

    mock_response(method="POST")

    async with base_mixin._async_stream_request("POST", "/stream", data=data) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_with_files(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    files = {"async_upload": ("async_file.txt", b"async content")}

    mock_response(method="POST")

    async with base_mixin._async_stream_request("POST", "/stream", files=files) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_with_params(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    params = {"async_type": "stream"}

    mock_response()

    async with base_mixin._async_stream_request("GET", "/stream", params=params) as response:
        assert response.status_code == codes.OK


@pytest.mark.asyncio
async def test_async_stream_request_with_json(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    json_data = {"async_stream": True}

    mock_response(method="POST")

    async with base_mixin._async_stream_request("POST", "/stream", json=json_data) as response:
        assert response.status_code == codes.OK


# ============================================================================
# Tests for _get_default_headers
# ============================================================================


def test_get_default_headers_returns_correct_headers(base_mixin: BaseMixin) -> None:
    headers = base_mixin._get_default_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"


def test_get_default_headers_returns_headers_object(base_mixin: BaseMixin) -> None:
    headers = base_mixin._get_default_headers()
    assert isinstance(headers, httpx.Headers)


# ============================================================================
# Tests for _check_api_error
# ============================================================================


def test_check_api_error_no_error(base_mixin: BaseMixin, mock_response: MockResponseFn) -> None:
    mock_response(json={})

    response = base_mixin._send_request("GET", "/")
    # Should not raise
    base_mixin._check_api_error(response)


@pytest.mark.parametrize(
    "status_code",
    [codes.BAD_REQUEST, codes.UNAUTHORIZED, codes.FORBIDDEN, codes.NOT_FOUND],
)
def test_check_api_error_client_error_raises(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(status_code=status_code, json={"error": "error"})

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticHttpError):
        base_mixin._check_api_error(response)


@pytest.mark.parametrize(
    "status_code",
    [codes.INTERNAL_SERVER_ERROR, codes.BAD_GATEWAY, codes.SERVICE_UNAVAILABLE],
)
def test_check_api_error_server_error_raises(
    base_mixin: BaseMixin, mock_response: MockResponseFn, status_code: int
) -> None:
    mock_response(status_code=status_code, json={"error": "server error"})

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticHttpError):
        base_mixin._check_api_error(response)


def test_check_api_error_includes_status_code(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(status_code=codes.NOT_FOUND, json={"error": "not found"})

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticHttpError) as exc_info:
        base_mixin._check_api_error(response)

    assert exc_info.value.status_code.value == codes.NOT_FOUND


# ============================================================================
# Tests for _get_data_from_response
# ============================================================================


def test_get_data_from_response_valid_json(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    expected_data = {"key": "value", "nested": {"inner": 123}}

    mock_response(json=expected_data)

    response = base_mixin._send_request("GET", "/")
    data = base_mixin._get_data_from_response(response)
    assert data == expected_data


def test_get_data_from_response_empty_json_object(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(json={})

    response = base_mixin._send_request("GET", "/")
    data = base_mixin._get_data_from_response(response)
    assert data == {}


def test_get_data_from_response_json_array(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    expected_data = [1, 2, 3, {"key": "value"}]

    mock_response(json=expected_data)

    response = base_mixin._send_request("GET", "/")
    data = base_mixin._get_data_from_response(response)
    assert data == expected_data


def test_get_data_from_response_invalid_json_raises(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(content=b"not valid json {")

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticInvalidJsonError):
        base_mixin._get_data_from_response(response)


def test_get_data_from_response_invalid_json_error_message(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    invalid_content = "invalid json content"

    mock_response(content=invalid_content.encode())

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticInvalidJsonError) as exc_info:
        base_mixin._get_data_from_response(response)

    assert str(exc_info.value) == invalid_content


def test_get_data_from_response_null_json(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(content=b"null")

    response = base_mixin._send_request("GET", "/")
    data = base_mixin._get_data_from_response(response)
    assert data is None


def test_get_data_from_response_non_json_content_type(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    # Response with JSON content but non-JSON content-type
    json_data = {"data": "value"}

    mock_response(content=str(json_data).encode(), headers={"Content-Type": "text/plain"})

    response = base_mixin._send_request("GET", "/")
    # Should still parse if it's valid JSON, regardless of content-type
    data = base_mixin._get_data_from_response(response)
    assert data == json_data


def test_get_data_from_response_empty_response_body(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(content=b"")

    response = base_mixin._send_request("GET", "/")
    with pytest.raises(ResticInvalidJsonError):
        base_mixin._get_data_from_response(response)


def test_get_data_from_response_large_complex_json(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    large_data: dict[str, Any] = {"level1": {}}
    current = large_data["level1"]
    for i in range(10):
        current[f"nested_{i}"] = {"data": list(range(100)), "more": {}}
        current = current[f"nested_{i}"]["more"]
    current["end"] = "final"

    mock_response(json=large_data)

    response = base_mixin._send_request("GET", "/")
    data = base_mixin._get_data_from_response(response)
    assert data == large_data


# ============================================================================
# Tests for header merging behavior
# ============================================================================


def test_custom_headers_override_defaults(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    mock_response(json={})

    response = base_mixin._send_request("GET", "/", headers={"Content-Type": "text/plain"})

    assert response.request.headers["Content-Type"] == "text/plain"


def test_multiple_custom_headers_merged(
    base_mixin: BaseMixin, mock_response: MockResponseFn
) -> None:
    custom_headers = {"Authorization": "Bearer token", "X-Custom": "value"}

    mock_response(json={})

    response = base_mixin._send_request("GET", "/", headers=custom_headers)

    assert response.request.headers["Authorization"] == "Bearer token"
    assert response.request.headers["X-Custom"] == "value"
    assert response.request.headers["Content-Type"] == "application/json"
