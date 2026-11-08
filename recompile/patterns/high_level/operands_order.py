import data_types
import expressions
from expression_transformer import ExpressionTransformer
from expressions.operator import Operator


def order_operands(procedure, stack_vars):
    """Write operands in the order of the source when the binary allows
    both orders.

    - Visual C++ 6.0 evaluates a computed operand of a floating point
      comparison before a local variable: 'v > x * 2.0' and 'x * 2.0 < v'
      are compiled the same way. A comparison of a computed value with a
      local variable or a field of a local object is written with the
      variable first, like arguments of macros 'max(maxX, p.x)'. Parameters
      and constants stay at the right.
    - A result of a conditional operator is evaluated before other operands
      of commutative operators: 'max(a, b) + c'.
    """
    local_names = set(
        var.name for offset, var in stack_vars.items() if offset < 0)
    return procedure.transform(_OperandsOrderTransformer(local_names))


_mirrored = {
    Operator.LT: Operator.GT,
    Operator.GT: Operator.LT,
    Operator.LE: Operator.GE,
    Operator.GE: Operator.LE,
}


class _OperandsOrderTransformer(ExpressionTransformer):
    def __init__(self, local_names):
        self._local_names = local_names

    def transform_binary(self, operator, left, right, **kwargs):
        if operator in _mirrored:
            if (
                _is_float(left) and _is_float(right) and
                self._is_local(right) and not self._is_local(left) and
                not isinstance(left, expressions.Constant)
            ):
                return expressions.Bin(_mirrored[operator], right, left)
            return None
        if operator in (Operator.ADD, Operator.MUL):
            if (
                isinstance(right, expressions.ConditionalOperator) and
                not isinstance(left, expressions.ConditionalOperator)
            ):
                return expressions.Bin(operator, right, left)
        return None

    def _is_local(self, e):
        while isinstance(e, expressions.FieldAccess):
            e = e.expression
            if isinstance(e, expressions.AddressOf):
                e = e.expression
            else:
                return False
        return (
            isinstance(e, expressions.Identifier) and
            e.name in self._local_names
        )


def _is_float(e):
    try:
        data_type = e.data_type
    except Exception:
        return False
    return isinstance(data_type, (data_types.Float, data_types.Double))
