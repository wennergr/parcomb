from parcomb.response import *
from pytest import raises


def test_get_or_raise():
    assert Success("a", "").get_or_raise() == "a"

    with raises(Exception) as err:
        Failure("error", "").get_or_raise()


def test_recover():
    assert Success("a", "").recover(lambda _: Success("b", "")) == Success("a", "")
    assert Failure("error", "abc").recover(lambda _: "b") == Success("b", "abc")


def test_get_or_else():
    assert Success("a", "").get_or_else("b") == "a"
    assert Failure("error", "").get_or_else("b") == "b"
