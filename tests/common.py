from parcomb.parsing import Return
from typing import NoReturn, TypeVar, Callable

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def assert_success(obj: Return, value: A, next: str) -> NoReturn:
    assert obj.success()
    assert obj.value == value
    assert obj.next == next


def assert_failure(obj: Return, next: str) -> NoReturn:
    assert obj.failure()
    assert obj.next == next


def join(xs: list[str]) -> str:
    return "".join(xs)


def to_list(x: str) -> list[str]:
    return [x]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))
