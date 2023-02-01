from textwrap import dedent
from tests.common import assert_success, join, to_list
from parcomb.char import char, none_of, trim, one_of, any, eof
from parcomb.combinator import between, many1, end_by, const
from parcomb.parsing import future


def test_ini():
    input1 = dedent(
        """\
    ; last modified 1 April 2001 by John Doe
    [owner]
    name = John Doe
    organization = Acme Widgets Inc.
    
    [database]
    ; use IP address in case network name resolution is not working
    server = 192.0.2.62
    port = 143
    file = payroll.dat
    """
    )

    expected1 = {
        "owner": {"name": "John Doe", "organization": "Acme Widgets Inc."},
        "database": {"server": "192.0.2.62", "port": "143", "file": "payroll.dat"},
    }

    nl, eq = char("\n"), char("=")
    line_end = nl | eof()

    comment = char(";") << end_by(any(), char("\n")).map(join) >> nl

    # Key value pair expression
    key = end_by(any(), one_of(["=", "\n", " "])).map(join)
    value = end_by(any(), line_end).map(join)
    kw_pair = (key >> trim(eq)) * value

    # List of key values
    properties = future()
    properties <<= (
        (comment | nl) << properties  # Ignore empty lines and comments
        | (kw_pair >> line_end).map(to_list) + properties  # Recursively find properties
        | const([])  # Base case
    )
    properties = properties.map(dict)  # Convert [(key, value), ..] to dict(key = value)

    # Section expression ("section name": [properties])
    section_name = many1(none_of(["]"])).map(join)
    section_header = between(char("["), section_name, char("]")) >> nl
    section = section_header * properties

    # Main parser
    parser = future()
    parser <<= (
        (comment | nl) << parser  # Ignore empty lines and comments
        | section.map(to_list) + parser  # Recursively find sections
        | const([])  # Base case
    )

    # Convert [(section_name, properties), ..] to dict(section_name, properties)
    parser = parser.map(dict)

    assert_success(parser.run(input1), expected1, "")
