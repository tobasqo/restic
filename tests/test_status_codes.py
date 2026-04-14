import pytest
from httpx._status_codes import codes

from restic.status_codes import HttpStatusCode


@pytest.mark.parametrize(
    ("value", "phrase"),
    [(code.value, code.phrase) for code in codes],  # type: ignore[attr-defined]
)
def test_from_value(value: int, phrase: str) -> None:
    code = HttpStatusCode.from_value(value)
    assert code.value == value
    assert code.phrase == phrase


def test_from_value_unknown() -> None:
    value = 999
    code = HttpStatusCode.from_value(value)
    assert code.value == value
    assert code.phrase == "Unknown error"


def test_str() -> None:
    value = 200
    phrase = "OK"
    code = HttpStatusCode(value, phrase)
    assert str(code) == f"{value} - {phrase}"


def test_repr() -> None:
    value = 404
    phrase = "Not Found"
    code = HttpStatusCode(value, phrase)
    assert repr(code) == f"{value} - {phrase}"


def test_eq() -> None:
    code1 = HttpStatusCode(200, "OK")
    code2 = HttpStatusCode(200, "OK")
    code3 = HttpStatusCode(404, "Not Found")
    assert code1 == code2
    assert code1 != code3


def test_eq_int() -> None:
    value = 200
    code = HttpStatusCode(value, "OK")
    assert code == value


def test_lt() -> None:
    code1 = HttpStatusCode(200, "OK")
    code2 = HttpStatusCode(404, "Not Found")
    assert code1 < code2


def test_lt_int() -> None:
    code = HttpStatusCode(200, "OK")
    assert code < code.value + 1


def test_le() -> None:
    code1 = HttpStatusCode(200, "OK")
    code2 = HttpStatusCode(200, "OK")
    code3 = HttpStatusCode(404, "Not Found")
    assert code1 <= code2
    assert code1 <= code3


def test_le_int() -> None:
    code = HttpStatusCode(200, "OK")
    assert code <= code.value
    assert code <= code.value + 1


def test_gt() -> None:
    code1 = HttpStatusCode(404, "Not Found")
    code2 = HttpStatusCode(200, "OK")
    assert code1 > code2


def test_gt_int() -> None:
    code = HttpStatusCode(200, "OK")
    assert code > code.value - 1


def test_ge() -> None:
    code1 = HttpStatusCode(404, "Not Found")
    code2 = HttpStatusCode(404, "Not Found")
    code3 = HttpStatusCode(200, "OK")
    assert code1 >= code2
    assert code1 >= code3


def test_ge_int() -> None:
    code = HttpStatusCode(200, "OK")
    assert code >= code.value
    assert code >= code.value - 1


def test_hash() -> None:
    code1 = HttpStatusCode(200, "OK")
    code2 = HttpStatusCode(200, "OK")
    code3 = HttpStatusCode(404, "Not Found")
    assert hash(code1) == hash(code2)
    assert hash(code1) != hash(code3)
