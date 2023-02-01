from textwrap import dedent
from tests.common import assert_success
from parcomb.char import char, any, none_of
from parcomb.combinator import many, sep_by, between


def test_csv():
    csv = dedent(
        """\
    name,age,location
    John Doe,45,"United States of America, \\"USA\\""
    Sandra Wurst,55,Germany
    "Eric Strauss",25,Germany"""
    )

    expected = [
        {
            "name": "John Doe",
            "age": "45",
            "location": 'United States of America, "USA"',
        },
        {"name": "Sandra Wurst", "age": "55", "location": "Germany"},
        {"name": "Eric Strauss", "age": "25", "location": "Germany"},
    ]

    def to_entries(headers: list[str], data: list[list[str]]) -> list[dict[str, str]]:
        return [{k: v for (k, v) in zip(headers, r)} for r in data]

    def join(xs: list[str]):
        return "".join(xs)

    esc = char("\\") << any()
    q_str = many(esc | none_of(['"'])).map(join)
    cell1 = between(char('"'), q_str, char('"'))  # Cell in quotation marks
    cell2 = many(none_of([",", "\n"])).map(join)  # Cell separated by ","
    row = sep_by(cell1 | cell2, char(","))

    header = row >> char("\n")  # Header row
    rows = sep_by(row, char("\n"))  # Rest or the rows

    expr = (header * rows).map_u(to_entries)

    assert_success(expr.run(csv), expected, "")
