from pydantic import HttpUrl, ValidationError

from restic.exceptions import ResticInvalidUrlError


def parse_url(url: str) -> str:
    try:
        _ = HttpUrl(url)
    except ValidationError as exc:
        raise ResticInvalidUrlError(url) from exc
    return url.rstrip("/")
