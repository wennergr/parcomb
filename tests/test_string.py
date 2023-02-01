from tests.common import assert_success, assert_failure
from parcomb.char import char
from parcomb.string import literal, word, alphas, alphanumerics


def test_string():
    input1 = "[teststring]"
    input2 = "[test2string]"

    expr = char("[") << literal("teststring") >> char("]")

    assert_success(expr.run(input1), "teststring", "")
    assert_failure(expr.run(input2), "test2string]")


def test_word():
    input1 = "test123"

    assert_success(word(["t", "e", "s"]).run(input1), "test", "123")
    assert_failure(word(["e", "s"]).run(input1), input1)


def test_alphas():
    input1 = "test123"
    input2 = "123test123"

    assert_success(alphas().run(input1), "test", "123")
    assert_failure(alphas().run(input2), input2)


def test_alphanumerics():
    input1 = "test123!!"
    input2 = "!123test123"

    assert_success(alphanumerics().run(input1), "test123", "!!")
    assert_failure(alphanumerics().run(input2), input2)
