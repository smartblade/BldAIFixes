import data_types
import expressions
import instructions


def transform_class_returns(proc_decl, instrs):
    """Restore returns of objects of classes constructed at '__result'."""
    if proc_decl is None:
        return instrs
    class_type = proc_decl.return_type
    if not isinstance(class_type, data_types.ClassType):
        return instrs
    if not instrs:
        return instrs
    result = _get_returned_result(instrs[-1])
    if result is None:
        return instrs
    body = list(instrs[:-1])
    new_body = _transform_copy_construction(result, class_type, body)
    if new_body is None:
        new_body = _transform_fields_construction(result, class_type, body)
    if new_body is None:
        return instrs
    return new_body


def _get_returned_result(instr):
    if not isinstance(instr, instructions.TemporaryRegisterDefinition):
        return None
    values = instr._values
    if list(values.keys()) != ["eax"]:
        return None
    result = values["eax"]
    if not isinstance(result, expressions.Identifier):
        return None
    if result.name != "__result":
        return None
    return result


def _transform_copy_construction(result, class_type, body):
    """'__result->C(x); local.~D(); ...' -> 'return x;' or 'return C(...);'"""
    end = len(body)
    # Locals are destroyed implicitly after the return
    while end > 0 and _is_local_destruction(body[end - 1]):
        end -= 1
    if end == 0:
        return None
    pc = _get_method_call(body[end - 1])
    if pc is None or pc.proc_decl is None:
        return None
    if not pc.proc_decl.is_constructor or not _is_result(pc.arguments[0]):
        return None
    arguments = pc.arguments[1:]
    if len(arguments) == 1 and _is_object_of(arguments[0], class_type):
        value = _strip_reference(arguments[0])
    else:
        value = expressions.ProcedureCall(
            name=class_type.class_name, is_method=False, arguments=arguments)
    return body[:end - 1] + [instructions.ReturnInstruction(value)]


def _transform_fields_construction(result, class_type, body):
    """'__result->x = a; __result->y = b;' -> 'return C(a, b);'"""
    fields = [field for offset, field in sorted(class_type.fields.items())]
    if not fields or len(body) < len(fields):
        return None
    if _find_constructor(class_type, fields) is None:
        return None
    start = len(body) - len(fields)
    values = []
    for instr, (field_type, field_name) in zip(body[start:], fields):
        if not isinstance(instr, instructions.Assignment):
            return None
        dst = instr.dst
        if not isinstance(dst, expressions.FieldAccess):
            return None
        if not _is_result(dst.expression) or dst.field_name != field_name:
            return None
        values.append(instr.src)
    value = expressions.ProcedureCall(
        name=class_type.class_name, is_method=False, arguments=values)
    return body[:start] + [instructions.ReturnInstruction(value)]


def _find_constructor(class_type, fields):
    """Find constructor with parameters of types of fields."""
    for method in class_type.constructors:
        parameters = list(method.get_parameters_ids().values())[1:]
        if len(parameters) != len(fields):
            continue
        if all(
            data_types.are_same(p.data_type, field_type)
            for p, (field_type, field_name) in zip(parameters, fields)
        ):
            return method
    return None


def _get_method_call(instr):
    if not isinstance(instr, instructions.CodeInstruction):
        return None
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return None
    return pc


def _is_local_destruction(instr):
    pc = _get_method_call(instr)
    if pc is None or pc.proc_decl is None or not pc.proc_decl.is_destructor:
        return False
    obj = pc.arguments[0]
    return (
        isinstance(obj, expressions.AddressOf) and
        isinstance(obj.expression, expressions.Identifier)
    )


def _is_object_of(e, class_type):
    data_type = e.data_type
    if isinstance(data_type, data_types.Reference):
        data_type = data_type.referent
    return data_types.are_same(data_type, class_type)


def _strip_reference(e):
    if isinstance(e, expressions.MakeReference):
        return e.expression
    return e


def _is_result(e):
    return isinstance(e, expressions.Identifier) and e.name == "__result"
