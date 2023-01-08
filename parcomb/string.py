from .parsing import Parser, Return, Success, Failure


def string(check: str) -> Parser[str]:
    def parse(data: str) -> Return:
        left, part, right = data.partition(check)

        if left == "" and part == check:
            return Success(part, right)
        else:
            return Failure(f"#string, Failed to find {check} in {data}", data)

    return Parser(parse)
