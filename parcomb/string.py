from .parsing import Parser, Return, Success, Failure
from .combinator import many1
from .char import one_of
from .common import join
from string import ascii_letters, digits


def literal(check: str) -> Parser[str]:
    def parse(data: str) -> Return:
        left, part, right = data.partition(check)

        if left == "" and part == check:
            return Success(part, right)
        else:
            return Failure(f"#string, Failed to find {check} in {data}", data)

    return Parser(parse)


def word(charset: list[str]) -> Parser[str]:
    return many1(one_of(charset)).map(join)


def alphanumerics() -> Parser[str]:
    return word(list(ascii_letters + digits))


def alphas() -> Parser[str]:
    return word(list(ascii_letters))
