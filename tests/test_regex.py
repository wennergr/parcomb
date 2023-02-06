from parcomb.regex import match, match_dict
from .common import assert_failure, assert_success


def test_match():
    input1 = "tunnels B lead to valves DD, II, BB"
    input2 = "tunnel A leads to valve CC"
    input3 = "tunnelss A leads to valve CC"

    expr = match("tunnels? ([A-Z]) leads? to valves? ([A-Z][A-Z])")
    assert_success(expr.run(input1), ["B", "DD"], ", II, BB")
    assert_success(expr.run(input2), ["A", "CC"], "")
    assert_failure(expr.run(input3), input3)


def test_match_dict():
    input1 = "tunnels B lead to valves DD, II, BB"
    input2 = "tunnel A leads to valve CC"
    input3 = "tunnelss A leads to valve CC"

    expr = match_dict(
        "tunnels? (?P<source>[A-Z]) leads? to valves? (?P<first_dest>[A-Z][A-Z])"
    )
    assert_success(expr.run(input1), {"source": "B", "first_dest": "DD"}, ", II, BB")
    assert_success(expr.run(input2), {"source": "A", "first_dest": "CC"}, "")
    assert_failure(expr.run(input3), input3)
