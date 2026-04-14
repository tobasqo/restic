import logging
from typing import Any, Protocol

import httpx
import pytest
from pytest_httpx import HTTPXMock


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


BASE_URL = httpx.URL("https://example.com/test")


@pytest.fixture(scope="session", autouse=True)
def _setup_logging() -> None:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


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
