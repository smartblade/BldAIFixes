import re

import data_types
from hex_conversion import from_hex
import parser

variable_decl_regexp = re.compile(
    r'^((static|extern)\s+)?(?P<type>[^=]*[*&\s])(?P<name>[^\W\d]\S*)'
    r'(\s*=\s*\w*\s*)?$')
array_size_regexp = re.compile(r'(?P<name>.+)\[(?P<size>(0x[\dABCDEF]+)|\w+)]$')


def parse_cpp_variable_declaration(s, declared_types, constants=None):
    match = variable_decl_regexp.search(s)
    if not match:
        raise Exception("'{}' is not variable declaration.".format(s))
    field_type = match.group("type").strip()
    field_name = match.group("name")
    field_type = parser.parse_data_type(field_type, declared_types)
    field_type, field_name = _extract_array_size(
        field_type, field_name, constants)
    return field_type, field_name


def _extract_array_size(field_type, field_name, constants):
    """Arrays of several dimensions are arrays of arrays: 'm[4][2]' is an
    array of 4 arrays of 2 elements."""
    sizes = []
    while True:
        match = array_size_regexp.search(field_name)
        if not match:
            break
        sizes.insert(0, _parse_array_size(match.group("size"), constants))
        field_name = match.group("name")
    for size in reversed(sizes):
        field_type = data_types.Array(field_type, size)
    return field_type, field_name


def _parse_array_size(size_str, constants):
    if size_str.startswith("0x"):
        return from_hex(size_str)
    if size_str[0].isdigit():
        return int(size_str)
    size = constants and constants.get_value(size_str)
    if size is None:
        raise Exception("Can't parse array size: {}.".format(size_str))
    return size
