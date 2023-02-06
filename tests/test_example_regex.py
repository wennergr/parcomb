# example taken from Advent of Code 2022 - day16
from typing import Tuple
from dataclasses import dataclass
from parcomb.char import any, trim, char
from parcomb.string import literal
from parcomb.number import integer
from parcomb.regex import match
from parcomb.combinator import sep_by1, product3
from parcomb.parsing import Parser

test_input = """\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
"""


@dataclass
class Valve:
    name: str
    flow_rate: int
    tunnels: list[str]


def to_dict(lst: list[Valve]) -> dict[str, Valve]:
    return dict([(x.name, x) for x in lst])


# Use regex to manage the different plural endings for the tunnel sections
def parser_1() -> Parser[dict[str, Valve]]:
    valve_expr = trim(any() + any())
    valves_expr = sep_by1(valve_expr, char(","))

    valve = product3(
        literal("Valve") << valve_expr,
        literal("has flow rate=") << integer(),
        match("; tunnels? leads? to valves?") << valves_expr,
    ).map_u(Valve)

    return sep_by1(valve, char("\n")).map(to_dict)


# Use regex to manage first valve name, flow rate, and different plural endings for the tunnel sections
def parser_2() -> Parser[dict[str, Valve]]:
    tunnel_expr = sep_by1(trim(any() + any()), char(","))

    valve = (
        match(r"Valve ([A-Z][A-Z]) has flow rate=(\d+); tunnels? leads? to valves?")
        * tunnel_expr
    ).map_u(
        lambda re, t: Valve(re[0], int(re[1]), t)
    )  # First param from regex (valve_name, flow_rate), Second is tunnels_expr

    return sep_by1(valve, char("\n")).map(to_dict)


def test_parse_1():
    resp1 = parser_1().run(test_input).get_or_raise()
    resp2 = parser_2().run(test_input).get_or_raise()

    assert resp1 == resp2

    assert len(resp1) == 10
    assert set(resp1.keys()) == {
        "AA",
        "BB",
        "CC",
        "DD",
        "EE",
        "FF",
        "GG",
        "HH",
        "II",
        "JJ",
    }

    assert resp1["EE"].flow_rate == 3
    assert resp1["II"].tunnels == ["AA", "JJ"]
