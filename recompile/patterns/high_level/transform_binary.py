import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
from expressions.operator import Operator, comparison

from .call_characteristics import get_call_characteristics
from .transform_arrptr import transform_arrptr


def transform_binary(operator, left, right, analysis, **kwargs):
    analysis.process_binary(operator, left, right)
    if _is_integer_operation(left, right):
        if operator == Operator.ADD:
            return _transform_int_sum(left, right)
        if operator == Operator.SUB:
            return _transform_int_sub(left, right)
        if operator == Operator.MUL:
            return _transform_int_mul(left, right)
        if operator == Operator.BIT_AND:
            return _transform_bit_and(left, right)
    if operator in comparison:
        return _transform_comparison(operator, left, right, **kwargs)
    return None


def _is_integer_operation(left, right):
    return left.data_type.is_any_int and right.data_type.is_any_int


def _transform_int_sum(left, right):
    result = _transform_pointer_offset(left, right)
    if result is not None:
        return result
    return _convert_constants(Operator.ADD, left, right)


def _transform_int_sub(left, right):
    return _convert_constants(Operator.SUB, left, right)


def _transform_int_mul(left, right):
    return _convert_constants(Operator.MUL, left, right)


def _transform_pointer_offset(left, right):
    if not isinstance(left.data_type, data_types.AnyInt):
        return None
    if not right.data_type.is_any_int:
        return None
    if not isinstance(right, expressions.Constant):
        return _transform_pointer_index(left, right)
    if isinstance(left, expressions.Bin) and left.operator == Operator.ADD:
        return _transform_array_pointer_offset(left.left, left.right, right)
    return _transform_const_pointer_offset(left, right)


def _transform_const_pointer_offset(left, right: expressions.Constant):
    if not isinstance(left, expressions.ReinterpretCast):
        return None
    if not isinstance(
        left.expression.data_type, (data_types.Pointer32, data_types.Reference)
    ):
        return None
    e = do_pointer_dereference(left.expression, right.value, None)
    if e is None:
        return None
    return expressions.AddressOf(e)


def _transform_pointer_index(e, index):
    if not isinstance(e, expressions.ReinterpretCast):
        return None
    e = e.expression
    if not isinstance(e.data_type, data_types.Pointer32):
        return None
    if e.data_type.pointee is None:
        ptr_to_char = data_types.Pointer32(data_types.Char())
        ptr_to_char.set_qualifiers(e.data_type.qualifiers)
        e = expressions.StaticCast(ptr_to_char, e)
    return transform_arrptr(e, 1, index, 0)


def _transform_array_pointer_offset(bin_left, bin_right, right):
    e = _transform_field_element_offset(bin_left, bin_right, right)
    if e is not None:
        return e
    e = _transform_const_pointer_offset(bin_left, right)
    if e is None:
        return None
    return transform_arrptr(e, 1, bin_right, 0)


def _transform_field_element_offset(bin_left, bin_right, right):
    """Transform '(int)p + 8 * i + offset' to address of element of field."""
    if not isinstance(bin_left, expressions.ReinterpretCast):
        return None
    ptr = bin_left.expression
    if not isinstance(ptr.data_type, data_types.Pointer32):
        return None
    if not isinstance(ptr.data_type.pointee, data_types.ClassType):
        return None
    if not isinstance(right.value, int):
        return None
    return transform_arrptr(ptr, 1, bin_right, right.value)


def _convert_constants(operator, left, right):
    left_const = _convert_constant(left, right)
    if left_const is not None:
        return expressions.Bin(operator, left_const, right)
    right_const = _convert_constant(right, left)
    if right_const is not None:
        return expressions.Bin(operator, left, right_const)
    return None


def _convert_constant(c, other):
    if not isinstance(c, (expressions.Constant, expressions.NamedConstant)):
        return None
    if (
        not data_types.are_same(c.data_type, other.data_type) and
        c.data_type.size == other.data_type.size
    ):
        return expressions.do_reinterpret(other.data_type, c)
    return None


def _transform_comparison(operator, left, right, **kwargs):
    left = _strip_cast_from_comparison_operand(left)
    right = _strip_cast_from_comparison_operand(right)
    if operator == Operator.EQ or operator == Operator.NE:
        return _transform_eq_ne(operator, left, right, **kwargs)
    return expressions.Bin(operator, left, right)


def _transform_eq_ne(operator, left, right, **kwargs):
    result = _try_cast_to_bool(operator, left, right, **kwargs)
    if result is not None:
        return result
    if (
        isinstance(left.data_type, (data_types.Float, data_types.Double)) and
        isinstance(right.data_type, (data_types.Float, data_types.Double))
    ):
        return None
    right = expressions.do_reinterpret(left.data_type, right)
    if not isinstance(right, expressions.ConstantTypes):
        left = expressions.do_reinterpret(right.data_type, left)
    return expressions.Bin(operator, left, right)


def _try_cast_to_bool(operator, left, right, declarations, **kwargs):
    if not isinstance(left, expressions.ProcedureCall):
        return None
    if not left.data_type.is_any_int:
        return None
    if not isinstance(right, expressions.Constant):
        return None
    if not right.data_type.is_any_int:
        return None
    if right.value != 0:
        return None
    characteristics = get_call_characteristics(declarations, left)
    if characteristics.ret.is_boolean:
        if operator == Operator.NE:
            return left
        elif operator == Operator.EQ:
            return expressions.LogicalNot(left)
    return None


def _strip_cast_from_comparison_operand(e):
    if not isinstance(e, expressions.StaticCast):
        return e
    target_type = e.data_type
    src_type = e.expression.data_type
    if src_type.size != target_type.size:
        return e
    if src_type.is_unsigned_int and target_type.is_unsigned_int:
        return expressions.ImplicitCast(target_type, e.expression)
    return e


def _transform_bit_and(left, right):
    if not isinstance(right, expressions.Constant):
        return None
    if right.value != 0xFF:
        return None
    src_type = data_types.UChar()
    if not isinstance(left, expressions.ReinterpretCast):
        return None
    trash_extend = left.expression
    if not isinstance(trash_extend, expressions.intermediate.TrashExtend):
        return None
    expression = trash_extend.expression
    if not expression.data_type.is_any_int:
        return None
    if expression.data_type.size != src_type.size:
        return None
    return expressions.do_static_cast(
        left.data_type,
        expressions.do_reinterpret(src_type, expression),
    )
