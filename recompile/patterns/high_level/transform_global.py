import data_types
import parser
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference


def transform_global(address, declarations, **kwargs):
    global_var = declarations.symbols.variables.get(address)
    if global_var is not None and global_var.declaration is not None:
        var_type, var_name = parser.parse_cpp_variable_declaration(
            global_var.declaration.strip().strip(";"),
            declarations.declared_types,
        )
        _expect_not_float_constant(address, var_type, var_name, declarations)
        return expressions.AddressOf(expressions.Identifier(var_type, var_name))
    return _transform_field_of_global(address, declarations)


def _transform_field_of_global(address, declarations):
    """Address of a field of a global object at the address, e.g.
    &gbl_world_points.points.elements at 4 bytes after the object."""
    for var_address, global_var in declarations.symbols.variables.items():
        if var_address >= address or address - var_address > 0x10000:
            continue
        if global_var.declaration is None:
            continue
        try:
            var_type, var_name = parser.parse_cpp_variable_declaration(
                global_var.declaration.strip().strip(";"),
                declarations.declared_types,
            )
        except Exception:
            continue
        # Objects with simple names of classes that are not templates
        if not var_name.isidentifier():
            continue
        if not isinstance(var_type, data_types.ClassType):
            continue
        if var_type.template_param is not None:
            continue
        if address >= var_address + var_type.size:
            continue
        obj = expressions.AddressOf(expressions.Identifier(var_type, var_name))
        try:
            field = do_pointer_dereference(obj, address - var_address, None)
        except Exception:
            return None
        if field is None:
            return None
        return expressions.AddressOf(field)
    return None


def _expect_not_float_constant(address, var_type, var_name, declarations):
    # Compiler places float literals to read only data
    if not isinstance(var_type, (data_types.Float, data_types.Double)):
        return
    data = declarations.read_only_data.get_bytes(address, var_type.size)
    if data is not None:
        raise Exception(
            "Global variable {} at 0x{:08X} is read only float "
            "constant.".format(var_name, address))
