from __future__ import annotations
from typing import Callable, TypeVar, Generic, TypeGuard, NoReturn
from dataclasses import dataclass
from .common import assert_never, identity

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Failure:
    message: str
    next: str

    def success(self):
        return False

    def map(self, f: Callable[[A], B]) -> Failure:
        return self

    def recover(self, f: Callable[[Failure], A]) -> Success[A]:
        return recover(self, f)

    def get_or_raise(self) -> NoReturn:
        raise Exception(self.message)

    def get_or_else(self, a: A) -> A:
        return a


@dataclass
class Success(Generic[A]):
    value: A
    next: str

    def success(self):
        return True

    def map(self, f: Callable[[A], B]) -> Success[B]:
        return Success(f(self.value), self.next)

    def recover(self, f: Callable[[Failure], A]) -> Success[A]:
        return recover(self, f)

    def get_or_raise(self) -> A:
        return self.value

    def get_or_else(self, a: A) -> A:
        return self.value


Return = Success[A] | Failure


def is_success(ret: Return[A]) -> TypeGuard[Success]:
    return isinstance(ret, Success)


def is_failure(ret: Return[A]) -> TypeGuard[Failure]:
    return isinstance(ret, Failure)


def fold(
    ret: Return[A], success: Callable[[Success[A]], B], failure: Callable[[Failure], B]
) -> B:
    match ret:
        case Success(_, _):
            return success(ret)

        case Failure(_):
            return failure(ret)

        case _:  # pragma: no cover
            assert_never(ret)


def recover(ret: Return[A], f: Callable[[Failure], A]) -> Success[A]:
    def to_success(failure: Failure) -> Success[A]:
        return Success(f(failure), failure.next)

    return fold(ret, identity, to_success)
