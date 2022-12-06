# pylint: disable=missing-module-docstring,missing-function-docstring,unused-argument
from typing import Optional

from pytest import Config


def pytest_make_parametrize_id(config: Config, val: object, argname: str) -> Optional[str]:
    return f"{argname}:{val}" if isinstance(val, (int, bool)) else None
