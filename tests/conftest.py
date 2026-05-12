from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Protocol

import httpx
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

    from httpx import _types as httpx_types
    from pytest_httpx import HTTPXMock


BASE_URL = httpx.URL("https://example.com/test")


class BuildRequestFn(Protocol):
    def __call__(
        self,
        method: str = "GET",
        url: httpx.URL | str = BASE_URL,
        params: httpx_types.QueryParamTypes | None = None,
        headers: httpx_types.HeaderTypes | None = None,
        cookies: httpx_types.CookieTypes | None = None,
        content: httpx_types.RequestContent | None = None,
        data: httpx_types.RequestData | None = None,
        files: httpx_types.RequestFiles | None = None,
        json: Any | None = None,
        stream: httpx_types.SyncByteStream | httpx_types.AsyncByteStream | None = None,
        extensions: httpx_types.RequestExtensions | None = None,
    ) -> httpx.Request: ...


class BuildResponseFn(Protocol):
    def __call__(
        self,
        status_code: int = 200,
        headers: httpx_types.HeaderTypes | None = None,
        content: httpx_types.ResponseContent | None = None,
        text: str | None = None,
        html: str | None = None,
        json: Any = None,
        stream: httpx_types.SyncByteStream | httpx_types.AsyncByteStream | None = None,
        request: httpx.Request | None = None,
        extensions: httpx_types.ResponseExtensions | None = None,
        history: list[httpx.Response] | None = None,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
    ) -> httpx.Response: ...


class MockResponseFn(Protocol):
    def __call__(
        self,
        method: str = "GET",
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        text: str | None = None,
        html: str | None = None,
        stream: Any = None,
        json: Any = None,
    ) -> HTTPXMock: ...


@pytest.fixture(scope="session", autouse=True)
def _setup_logging() -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


@pytest.fixture(name="build_request")
def _build_request_fixture() -> BuildRequestFn:
    def wrapper(
        method: str = "GET",
        url: httpx.URL | str = BASE_URL,
        params: httpx_types.QueryParamTypes | None = None,
        headers: httpx_types.HeaderTypes | None = None,
        cookies: httpx_types.CookieTypes | None = None,
        content: httpx_types.RequestContent | None = None,
        data: httpx_types.RequestData | None = None,
        files: httpx_types.RequestFiles | None = None,
        json: Any | None = None,
        stream: httpx_types.SyncByteStream | httpx_types.AsyncByteStream | None = None,
        extensions: httpx_types.RequestExtensions | None = None,
    ) -> httpx.Request:
        return httpx.Request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            content=content,
            data=data,
            files=files,
            json=json,
            stream=stream,
            extensions=extensions,
        )

    return wrapper


@pytest.fixture(name="build_response")
def _build_response_fixture(build_request: BuildRequestFn) -> BuildResponseFn:
    def wrapper(
        status_code: int = 200,
        headers: httpx_types.HeaderTypes | None = None,
        content: httpx_types.ResponseContent | None = None,
        text: str | None = None,
        html: str | None = None,
        json: Any = None,
        stream: httpx_types.SyncByteStream | httpx_types.AsyncByteStream | None = None,
        request: httpx.Request | None = None,
        extensions: httpx_types.ResponseExtensions | None = None,
        history: list[httpx.Response] | None = None,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
    ) -> httpx.Response:
        return httpx.Response(
            status_code=status_code,
            headers=headers,
            content=content,
            text=text,
            html=html,
            json=json,
            stream=stream,
            request=request or build_request(),
            extensions=extensions,
            history=history,
            default_encoding=default_encoding,
        )

    return wrapper


@pytest.fixture(name="mock_response")
def _mock_response_fixture(httpx_mock: HTTPXMock) -> MockResponseFn:
    def wrapper(
        method: str = "GET",
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
        text: str | None = None,
        html: str | None = None,
        stream: Any = None,
        json: Any = None,
    ) -> HTTPXMock:
        httpx_mock.add_response(
            method=method,
            status_code=status_code,
            headers=headers,
            content=content,
            text=text,
            html=html,
            stream=stream,
            json=json,
        )
        return httpx_mock

    return wrapper


@pytest.fixture(name="client")
def _client_fixture() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL)


@pytest.fixture(name="async_client")
def _async_client_fixture() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL)
