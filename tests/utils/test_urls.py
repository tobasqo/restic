import pytest

from restic.exceptions import ResticInvalidUrlError
from restic.utils.urls import parse_url


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com",
        "http://example.com/",
        "https://example.com/",
        "http://example.com/path",
        "https://example.com/path",
        "http://example.com/path/",
        "https://example.com/path/",
        "http://example.com:80",
        "http://example.com:80/",
    ],
)
def test_parse_url_valid(url: str) -> None:
    assert parse_url(url) == url.rstrip("/")


@pytest.mark.parametrize(
    "url",
    [
        "example.com",
        "ftp://example.com",
        "http://",
        "https://",
        "http://example.com:abc",
        "localhost",
        "localhost:8000",
    ],
)
def test_parse_url_invalid(url: str) -> None:
    with pytest.raises(ResticInvalidUrlError):
        parse_url(url)
