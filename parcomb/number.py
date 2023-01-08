from .parsing import Parser
from .char import satisfy
from .combinator import many1


def integer() -> Parser[int]:
    isdigit = satisfy(lambda c: c.isdigit(), f"#integer: Failed to parse integer")

    return many1(isdigit).map(lambda x: int("".join(x)))
