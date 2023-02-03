from typing import NoReturn, TypeVar

A = TypeVar("A")


def join(xs: list[str]) -> str:
    return "".join(xs)


def assert_never(x: NoReturn) -> NoReturn:  # pragma: no cover
    assert False, "Unhandled type: {}".format(type(x).__name__)


def identity(a: A) -> A:
    return a
