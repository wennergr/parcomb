from typing import TypeVar
from .common import join
from parcomb.char import char, whitespaces, none_of
from parcomb.string import literal, alphanumerics
from parcomb.number import integer
from parcomb.combinator import between, sep_by, debug, many
from parcomb.parsing import future, Parser, Success


def test_json():
    input = """
{ "name"   : "John Smith",
  "sku"    : "20223",
  "price"  : 23,
  "shipTo" : { "name" : "Jane Smith",
               "address" : "123 Maple Street",
               "city" : "Pretendville",
               "state" : "NY",
               "zip"   : "12345" },
  "billTo" : { "name" : "John Smith",
               "address" : "123 Maple Street",
               "city" : "Pretendville",
               "state" : "NY",
               "zip"   : "12345" }
}
    """

    def trim(pa):
        return whitespaces() << pa >> whitespaces()

    begin_array = trim(char("["))
    end_array = trim(char("]"))

    begin_object = trim(char("{"))
    end_object = trim(char("}"))

    # Non-recursive JSON types
    string_value = trim(
        between(char('"'), many(none_of(["\n", '"'])).map(join), char('"'))
    )
    number_value = trim(integer())
    boolean_value = trim(
        literal("true").map(lambda _: True) | literal("false").map(lambda _: False)
    )
    null_value = trim(literal("null").map(lambda _: None))

    # Recursive JSON types (can be nested and by, for example, themself)
    array_value = future()
    object_value = future()

    # Json Parser
    value = (
        string_value
        | number_value
        | boolean_value
        | null_value
        | array_value
        | object_value
    )

    # JSON Array expression
    array_value <<= trim(between(begin_array, sep_by(value, char(",")), end_array))

    # JSON Object expression
    object_key_value_pair = (string_value >> char(":")) * value
    object_value <<= trim(
        between(begin_object, sep_by(object_key_value_pair, char(",")), end_object)
    ).map(dict)

    parser = value

    json = parser.run(input)

    if isinstance(json, Success):
        # Check some random values
        assert json.next == ""
        assert json.value["name"] == "John Smith"
        assert json.value["shipTo"]["name"] == "Jane Smith"
    else:
        assert False
