from .parsing import Parser, Return, Success, Failure
from typing import TypeVar, Iterable, Callable, Tuple
from functools import partial
from textwrap import dedent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")


def const(a: A) -> Parser[A]:
    return Parser(lambda x: Success(a, x))


def many(pa: Parser[A]) -> Parser[list[A]]:
    def parse(result: list[A], data: str) -> Return:
        ret = pa.run(data)

        return (
            Success(result, data)
            if ret.failure()
            else parse(result + [ret.value], ret.next)
        )

    return Parser(partial(parse, []))


def many1(pa: Parser[A]) -> Parser[list[A]]:
    return pa.and_then(lambda x: many(pa).and_then(lambda xs: Parser.pure([x] + xs)))


def attempt(pa: Parser[A]) -> Parser[A]:
    def parse(data: str) -> Return:
        ret = pa.run(data)

        return Failure(ret.message, data) if ret.failure() else ret

    return Parser(parse)


def count(n: int, pa: Parser[A]) -> Parser[list[A]]:
    if n <= 0:
        return Parser.pure([])

    def parse(c: int, result: list[A], data: str) -> Return:
        if c == 0:
            return Success(result, data)

        ret = pa.run(data)
        if ret.failure():
            return ret

        return parse(c - 1, result + [ret.value], ret.next)

    return attempt(Parser(partial(parse, n, [])))


def skip_left(pa: Parser[A], pb: Parser[B]) -> Parser[B]:
    return pa.and_then(lambda _: pb)


def skip_right(pa: Parser[A], pb: Parser[B]) -> Parser[B]:
    return pa.and_then(lambda x: pb.and_then(lambda _: Parser.pure(x)))


def choice(pas: Iterable[Parser[A]]) -> Parser[A]:
    def parse(data: str) -> Return:
        for pa in pas:
            ret = pa.run(data)

            if ret.success():
                return ret

        return Failure(f"#choice: no successful parser for data {data}", data)

    return Parser(parse)


def sep_by(pa: Parser[A], sep: Parser[B]) -> Parser[list[A]]:
    return choice([sep_by1(pa, sep), Parser.pure([])])


def sep_by1(pa: Parser[A], sep: Parser[B]) -> Parser[list[A]]:
    init = pa  # Read one iteration of expr
    rest = many(sep << pa)  # Read many iteration of <sep><expr>

    return init.and_then(lambda x: rest.and_then(lambda xs: Parser.pure([x] + xs)))


def between(open: Parser[A], p: Parser[B], close: Parser[C]) -> Parser[B]:
    return open << p >> close


def combine(p1: Parser[A], p2: Parser[A]) -> Parser[A]:
    return combine_f(p1, p2, lambda a, b: a + b)


def combine_f(p1: Parser[A], p2: Parser[A], f: Callable[[A, A], A]) -> Parser[A]:
    return attempt(p1.and_then(lambda a: p2.and_then(lambda b: Parser.pure(f(a, b)))))


def end_by(pa: Parser[A], end: Parser[B]) -> Parser[list[A]]:
    def parse(result: list[A], data: str) -> Return:
        ret_pa = pa.run(data)

        if ret_pa.failure():
            return ret_pa

        # Look for end termination
        if end.run(data).success():
            return Success(result, data)

        return parse(result + [ret_pa.value], ret_pa.next)

    return attempt(Parser(partial(parse, [])))


def peek(pa: Parser[A]) -> Parser[A]:
    def parse(data: str) -> Return:
        ret = pa.run(data)

        # Reset consumption pointer
        ret.next = data

        return ret

    return Parser(parse)


def option(a: A, pa: Parser[A]) -> Parser[A]:
    return pa | Parser.pure(a)


def product(pa: Parser[A], pb: Parser[B]) -> Parser[Tuple[A, B]]:
    # Can be done without "and_then" using the applicative
    return pa.and_then(lambda a: pb.and_then(lambda b: const((a, b))))


def product3(p1: Parser[A], p2: Parser[B], p3: Parser[C]) -> Parser[Tuple[A, B, C]]:
    return product(p1, p2).and_then(lambda p: p3.and_then(lambda c: const(p + (c,))))


def product4(
    p1: Parser[A], p2: Parser[B], p3: Parser[C], p4: Parser[D]
) -> Parser[Tuple[A, B, C, D]]:
    return product3(p1, p2, p3).and_then(
        lambda p: p4.and_then(lambda d: const(p + (d,)))
    )


def product5(
    p1: Parser[A], p2: Parser[B], p3: Parser[C], p4: Parser[D], p5: Parser[E]
) -> Parser[Tuple[A, B, C, D, E]]:
    return product4(p1, p2, p3, p4).and_then(
        lambda p: p5.and_then(lambda e: const(p + (e,)))
    )


###
# Product alias
#
p = product
p3 = product3
p4 = product4
p5 = product5


###
# Debug combinators
#
def debug(
    pa: Parser[A], label: str = "Debug", logger: Callable[[str], None] = print
) -> Parser[A]:
    def wrapper(data: str) -> Return:
        format = lambda x: str(x)[:30].replace("\n", "\\n")

        buffer = "+" * 80 + "\n"
        buffer += f"""\
*** {label} ***
Input..: {format(data)}\n"""

        ret = pa.run(data)
        buffer += f"Success: {ret.success()}\n"

        if ret.success():
            # output = ret.value[:10].replace("\\", "\\\\")
            buffer += f"Value..: {format(ret.value)}\n"

        buffer += f"Next...: {format(ret.next)}\n"
        buffer += "-" * 80 + "\n"
        logger(buffer)

        return ret

    return Parser(lambda x: wrapper(x))
