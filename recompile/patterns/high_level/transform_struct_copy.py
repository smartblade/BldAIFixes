import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
import instructions


def transform_struct_copy(expression, **kwargs):
    """Transform 'memcpy(&dst, &src, sizeof(T))' to 'dst = src'.

    Structures are copied with 'rep movsd' compiled to memcpy. The copy of
    the whole object to '*this' is not transformed: it is the code of
    'operator =' or of the copy constructor.
    """
    pc = expression
    if not isinstance(pc, expressions.ProcedureCall) or pc.name != "memcpy":
        return None
    if len(pc.arguments) != 3:
        return None
    dst_ptr, src_ptr, size = pc.arguments
    if not isinstance(size, expressions.Constant):
        return None
    dst = _dereference_struct(dst_ptr, size.value)
    src = _dereference_struct(src_ptr, size.value)
    if dst is None or src is None:
        return None
    if not data_types.are_same(dst.data_type, src.data_type):
        return None
    if not isinstance(dst, (expressions.FieldAccess, expressions.Identifier)):
        return None
    return instructions.Assignment(dst, src)


_casts = (expressions.ImplicitCast, expressions.ReinterpretCast)


def _dereference_struct(ptr, size):
    while isinstance(ptr, _casts):
        ptr = ptr.expression
    if not isinstance(ptr.data_type, (
        data_types.Pointer32, data_types.Reference
    )):
        return None
    if isinstance(ptr.data_type, data_types.Reference):
        pointee = ptr.data_type.referent
    else:
        pointee = ptr.data_type.pointee
    if (
        isinstance(pointee, data_types.ClassType) and
        pointee.size == size
    ):
        # The whole object
        return expressions.do_dereference(ptr)
    try:
        e = do_pointer_dereference(ptr, 0, size)
    except Exception:
        return None
    if e is None or not isinstance(e.data_type, data_types.ClassType):
        return None
    if e.data_type.size != size:
        return None
    return e
