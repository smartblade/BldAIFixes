import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
from expressions.operator import Operator
from expressions.writer.byte_to_char import byte_to_char


def do_reinterpret(data_type, e):
    if e.data_type.size != data_type.size:
        raise Exception(
            "Can't reinterpret {}(size: {}) as {}(size: {}).".format(
                e.data_type, e.data_type.size, data_type, data_type.size))
    if data_types.are_compatible(e.data_type, data_type):
        return e
    result = _try_convert_pointers_or_references(e, e.data_type, data_type)
    if result is not None:
        return result
    if isinstance(e, expressions.Constant):
        return _reinterpret_const(data_type, e)
    if isinstance(e, expressions.ReinterpretCast):
        return _eliminate_reinterpret(data_type, e)
    result = _reinterpret_static_cast(data_type, e)
    if result is not None:
        return result
    result = _reinterpret_bin(data_type, e)
    if result is not None:
        return result
    if isinstance(e, expressions.NamedConstant):
        return _reinterpret_named_const(data_type, e)
    if isinstance(e, expressions.ConditionalOperator):
        return _reinterpret_cond_operator(data_type, e)
    return expressions.ReinterpretCast(data_type, e)


def _reinterpret_const(data_type, c):
    # Signed 32-bit integers have the same values
    if (
        isinstance(data_type, (data_types.Int32, data_types.Long32)) and
        isinstance(c.data_type, (data_types.Int32, data_types.Long32))
    ):
        return expressions.Constant(data_type, c.value)
    if (
        isinstance(data_type, (data_types.Int32, data_types.Long32)) and
        isinstance(
            c.data_type,
            (data_types.UInt32, data_types.AnyInt, data_types.Unknown32)) and
        data_type.size == c.data_type.size
    ):
        if c.value < 0x80000000:
            return expressions.Constant(data_type, c.value)
        else:
            return expressions.Constant(data_type, c.value - 0x100000000)
    if (
        data_type.is_unsigned_int and
        isinstance(
            c.data_type, (data_types.AnyInt, data_types.UnknownTypes)) and
        data_type.size == c.data_type.size
    ):
        return expressions.Constant(data_type, c.value)
    if (
        data_type.is_unsigned_int and
        c.data_type.is_unsigned_int and
        data_type.size == c.data_type.size
    ):
        return expressions.Constant(data_type, c.value)
    if (
        data_type.is_unsigned_int and
        isinstance(c.data_type, data_types.Int32) and
        data_type.size == c.data_type.size and
        c.value >= 0
    ):
        return expressions.Constant(data_type, c.value)
    if (
        isinstance(data_type, data_types.AnyInt) and
        isinstance(c.data_type, data_types.UnknownTypes) and
        data_type.size == c.data_type.size
    ):
        return expressions.Constant(data_type, c.value)
    if (
        isinstance(data_type, data_types.Pointer32) and
        isinstance(c.data_type, data_types.Unknown32) and
        c.value == 0
    ):
        return expressions.Null
    if (
        isinstance(data_type, data_types.Char) and
        isinstance(c.data_type, data_types.UnknownByte)
    ):
        assert isinstance(c.value, int)
        assert 0 <= c.value <= 255
        char = byte_to_char(c.value)
        return expressions.Constant(data_type, "'{}'".format(char))
    raise Exception(
        "Unimplemented reinterpret cast from {} to {}".format(
            c.data_type, data_type))


def _reinterpret_named_const(data_type, c):
    if (
        isinstance(
            data_type,
            (
                data_types.Int32,
                data_types.UInt32,
                data_types.Long32,
                data_types.UChar,
            )
        ) and
        isinstance(c.data_type, data_types.AnyInt) and
        data_type.size == c.data_type.size
    ):
        return expressions.ImplicitCast(data_type, c)
    raise Exception(
        "Unimplemented reinterpret cast from {} to {}".format(
            c.data_type, data_type))


def _eliminate_reinterpret(data_type, cast):
    return do_reinterpret(data_type, cast.expression)


def _reinterpret_bin(data_type, b):
    if not isinstance(b, expressions.Bin):
        return None
    if data_types.are_compatible(b.data_type, data_type):
        return b
    if not data_type.is_any_int:
        return None
    if not b.left.data_type.is_any_int:
        return None
    if not b.right.data_type.is_any_int:
        return None
    if (
        b.operator != Operator.ADD and
        b.operator != Operator.SUB and
        b.operator != Operator.MUL
    ):
        return None
    left = b.left
    right = b.right
    if isinstance(right, (expressions.Constant, expressions.NamedConstant)):
        left = do_reinterpret(data_type, left)
        return expressions.Bin(b.operator, left, right)
    if isinstance(left, (expressions.Constant, expressions.NamedConstant)):
        right = do_reinterpret(data_type, right)
        return expressions.Bin(b.operator, left, right)
    if isinstance(left, expressions.Bin):
        left = _reinterpret_bin(data_type, left)
        if left is None:
            return None
    if isinstance(right, expressions.Bin):
        right = _reinterpret_bin(data_type, right)
        if right is None:
            return None
    if (
        isinstance(left, (expressions.Bin, expressions.ReinterpretCast)) and
        isinstance(right, (expressions.Bin, expressions.ReinterpretCast)) or
        data_types.are_compatible(left.data_type, data_type) or
        data_types.are_compatible(right.data_type, data_type)
    ):
        left = do_reinterpret(data_type, left)
        right = do_reinterpret(data_type, right)
        return expressions.Bin(b.operator, left, right)
    return None


def _reinterpret_static_cast(data_type, cast):
    if not isinstance(cast, expressions.StaticCast):
        return None
    if (
        not cast.expression.data_type.is_any_int and
        not isinstance(cast.expression.data_type, data_types.Bool)
    ):
        return None
    if cast.expression.data_type.size > cast.data_type.size:
        return None
    if (
        isinstance(data_type, (data_types.Int32, data_types.UInt32)) and
        cast.data_type.is_any_int and data_type.size == cast.data_type.size
    ):
        return expressions.do_static_cast(data_type, cast.expression)
    return None


def _reinterpret_cond_operator(data_type, cond):
    return expressions.ConditionalOperator(
        cond.if_clause,
        do_reinterpret(data_type, cond.then_expression),
        do_reinterpret(data_type, cond.else_expression),
    )


def _try_convert_pointers_or_references(e, src_type, target_type):
    ptr_or_ref = (data_types.Pointer32, data_types.Reference)
    if not isinstance(src_type, ptr_or_ref):
        return None
    if not isinstance(target_type, ptr_or_ref):
        return None
    if isinstance(src_type, data_types.Pointer32):
        src_type_pointee = src_type.pointee
    else:
        src_type_pointee = src_type.referent
        e = expressions.AddressOf(e)
    if isinstance(target_type, data_types.Pointer32):
        target_type_pointee = target_type.pointee
    else:
        target_type_pointee = target_type.referent
    converted = _convert_pointees(e, src_type_pointee, target_type_pointee)
    if isinstance(target_type, data_types.Reference):
        converted = expressions.do_dereference(converted)
        if not isinstance(converted.data_type, data_types.Reference):
            converted = expressions.do_reference(converted)
    return converted


def _convert_pointees(e, src_type, target_type):
    if (
        data_types.are_compatible(
            data_types.Pointer32(src_type),
            data_types.Pointer32(target_type),
        )
    ):
        return e
    if src_type is None:
        return expressions.ReinterpretCast(data_types.Pointer32(target_type), e)
    if (
        src_type.is_any_int and
        target_type.is_any_int
    ):
        return expressions.ReinterpretCast(data_types.Pointer32(target_type), e)
    if (
        isinstance(src_type, data_types.ClassType) and
        isinstance(target_type, data_types.ClassType)
    ):
        return expressions.ReinterpretCast(data_types.Pointer32(target_type), e)
    if src_type.size > target_type.size:
        dereference = do_pointer_dereference(e, 0, target_type.size)
        if dereference is not None:
            return do_reinterpret(
                data_types.Pointer32(target_type),
                expressions.AddressOf(dereference))
    raise Exception("Can't convert {} to {}".format(src_type, target_type))
