import logging

import pytest


@pytest.fixture(scope="session", autouse=True)
def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)8s] %(name)s - %(message)s",
    )
