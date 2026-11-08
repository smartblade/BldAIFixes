import data_types
from expressions.operator import Operator
import expressions.writer


class AddressOf:
    def __init__(self, expression):
        assert isinstance(
            expression, (
                expressions.Identifier,
                expressions.FieldAccess,
                expressions.ArrayAccess,
                expressions.ProcedureCall,
                expressions.Bin,
                # Element returned by reference by operator[]
                expressions.SubscriptOperator,
            )
        )
        # Assignment returns lvalue
        assert (
            not isinstance(expression, expressions.Bin) or
            expression.operator == Operator.ASS
        )
        self._expression = expression

    def __repr__(self):
        return "AddrOf({})".format(self._expression)

    @property
    def expression(self):
        return self._expression

    @property
    def data_type(self):
        data_type = self._expression.data_type
        if isinstance(data_type, data_types.Reference):
            data_type = data_type.referent
        return data_types.Pointer32(data_type)

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        self._expression.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        expression = self._expression.transform(transformer, **kwargs)
        e = transformer.transform_unary(Operator.ADDR_OF, expression, **kwargs)
        if e is not None:
            return e
        if expression == self._expression:
            return self
        return self.__class__(expression)

    def emit_code(self):
        return expressions.writer.write_unary(
            Operator.ADDR_OF,
            self._expression,
        )
