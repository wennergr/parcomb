import re
from .response import Return, Failure, Success
from .parsing import Parser


def match(regex: str) -> Parser[list[str]]:
    """
    Extract groups from a regex and returns them as a list of strings.

    Consumes input up until the last character red by the regex engine
    For example (input: AA test):
        match("([A-Z][A-Z])") consumes the first two character AA
        match("([A-Z][A-Z]) .*") consumes the full string
    """

    def parse(data: str) -> Return[list[str]]:
        m = re.match(regex, data)

        if not m:
            return Failure("#match: Regex did not match", data)

        return Success(list(m.groups()), data[m.end() :])

    return Parser(parse)


def match_dict(regex: str) -> Parser[dict[str, str]]:
    """
    Extract named groups from a regex and returns them as a list of strings.

    Consumes input up until the last character red by the regex engine
    For example (input: AA test):
        match("([A-Z][A-Z])") consumes the first two character AA
        match("([A-Z][A-Z]) .*") consumes the full string
    """

    def parse(data: str) -> Return[dict[str, str]]:
        m = re.match(regex, data)

        if not m:
            return Failure("#match: Regex did not match", data)

        return Success(m.groupdict(), data[m.end() :])

    return Parser(parse)
