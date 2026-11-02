import re
import struct

import data_types
import expressions
from hex_conversion import to_hex
from expressions.operator import Operator
from expression_transformer import ExpressionTransformer
from patterns.apply_restriction import apply_restriction
from patterns.evaluate_expression import evaluate_expression

variable_pattern = re.compile(r"%(?P<variable>[\w\\-]*)%")

_actions = {
    "standard-proc": lambda builder, **kwargs: builder.make_standard(**kwargs),
    "validate-label": lambda builder, **kwargs: builder.validate_label(
        **kwargs),
    "prolog": lambda builder, **kwargs: builder.make_prolog(**kwargs),
    "prolog-preserved": lambda builder, **kwargs: builder.make_preserved(
        **kwargs),
    "epilog-restore": lambda builder, **kwargs: builder.make_restore(**kwargs),
    "epilog-return": lambda builder, **kwargs: builder.make_epilog(**kwargs),
    "instruction": lambda builder, **kwargs: builder.make_instruction(**kwargs),
    "validate": lambda builder, **kwargs: builder.validate(**kwargs),
    "assignment": lambda builder, **kwargs: builder.make_assignment(**kwargs),
    "fassignment": lambda builder, **kwargs: builder.make_float_assignment(
        **kwargs),
    "tmpreg": lambda builder, **kwargs: builder.update_temporary_reg(**kwargs),
    "pushfpu": lambda builder, **kwargs: builder.push_fpu(**kwargs),
    "stackarg": lambda builder, **kwargs: builder.make_arg(**kwargs),
    "call": lambda builder, **kwargs: builder.make_call(**kwargs),
    "method-call": lambda builder, **kwargs: builder.make_method_call(
        **kwargs),
    "addsp": lambda builder, **kwargs: builder.add_stack_pointer(**kwargs),
    "jump": lambda builder, **kwargs: builder.make_jump(**kwargs),
    "switch": lambda builder, **kwargs: builder.make_switch(**kwargs),
    "addrentry": lambda builder, **kwargs: builder.add_address_entry(**kwargs),
    "index32entry": lambda builder, **kwargs: builder.add_32bit_index_entry(
        **kwargs),
    "index8entry": lambda builder, **kwargs: builder.add_8bit_index_entry(
        **kwargs),
    "varlabel": lambda builder, **kwargs: builder.start_labeled_variable(
        **kwargs),
    "label": lambda builder, **kwargs: builder.start_labeled_block(**kwargs),
}


def apply_pattern(pattern, match_dict, **kwargs):
    _apply_actions(pattern, match_dict=match_dict, **kwargs)
    if pattern.restrictions is not None:
        for restriction in pattern.restrictions:
            restriction = _evaluate_expression(restriction, match_dict)
            apply_restriction(restriction)


def _apply_actions(pattern, **kwargs):
    if pattern.actions is None:
        apply_action(pattern.action, **kwargs)
        return
    for action in pattern.actions:
        apply_action(action, **kwargs)


def apply_action(action, builder, **kwargs):
    action_args = _evaluate_args(action.arguments, builder=builder, **kwargs)
    _actions[action.name](builder=builder, **action_args)


def replace_variables(expression, match_dict):
    for key, value in match_dict.items():
        expression = expression.replace("%{}%".format(key), value)
    return expression


def _evaluate_args(args, **kwargs):
    evaluated_args = {}
    for arg_name, expression in args.items():
        evaluated_args[arg_name] = _evaluate_expression(expression, **kwargs)
    return evaluated_args


def _evaluate_expression(expression, match_dict, **kwargs):
    transformer = _ExpressionTransformer(match_dict, kwargs)
    return expression.transform(transformer)


def _evaluate_reg_value(reg, builder, **kwargs):
    return builder.pop_reg_value(reg)


def _evaluate_pop_fpu(builder, **kwargs):
    return builder.pop_fpu()


def _evaluate_real64(high, low, **kwargs):
    (double, ) = struct.unpack(
        '>d',
        bytes.fromhex(to_hex(high) + to_hex(low)),
    )
    return expressions.Constant(data_types.Double(), double)


def _evaluate_expect(expression, const, **kwargs):
    if (
        isinstance(expression, expressions.Constant) and
        expression.value == const
    ):
        return expression
    raise Exception("Expected {} but was: {}".format(const, expression))


def _evaluate_any_int_conversion(expression, **kwargs):
    size = expression.data_type.size
    return expressions.do_reinterpret(data_types.AnyInt(size), expression)


def _evaluate_uint_conversion(expression, **kwargs):
    if expression.data_type.size == 1:
        return expressions.do_reinterpret(data_types.UChar(), expression)
    if expression.data_type.size == 2:
        return expressions.do_reinterpret(data_types.UShort(), expression)
    if expression.data_type.size == 4:
        return expressions.do_reinterpret(data_types.UInt32(), expression)
    raise Exception("Conversion to uint{} is not supported.".format(
        expression.data_type.size * 8))


def _evaluate_int_conversion(expression, **kwargs):
    if expression.data_type.size == 1:
        return expressions.do_reinterpret(data_types.Char(), expression)
    if expression.data_type.size == 2:
        return expressions.do_reinterpret(data_types.Short(), expression)
    if expression.data_type.size == 4:
        return expressions.do_reinterpret(data_types.Int32(), expression)
    raise Exception("Conversion to int{} is not supported.".format(
        expression.data_type.size * 8))


def _evaluate_float_conversion(expression, **kwargs):
    if expression.data_type.size == 4:
        return expressions.do_reinterpret(data_types.Float(), expression)
    if expression.data_type.size == 8:
        return expressions.do_reinterpret(data_types.Double(), expression)
    raise Exception("Conversion to real{} is not supported.".format(
        expression.data_type.size * 8))


def _evaluate_procedure_call(copy_pc, name, external_procedures, **kwargs):
    if name in external_procedures:
        assert copy_pc().proc_decl is None
        return copy_pc(proc_decl=external_procedures[name])
    return None


class _ExpressionTransformer(ExpressionTransformer):
    def __init__(self, match_dict, arguments):
        self._match_dict = match_dict
        self._arguments = arguments

    def transform_expression(self, expression, match_dict):
        transformer = _ExpressionTransformer(match_dict, self._arguments)
        return expression.transform(transformer)

    def transform_cast(self, data_type, expression, **kwargs):
        if isinstance(expression, expressions.BracketsExpression):
            expression = expression.expression
        return expressions.do_static_cast(data_type, expression)

    def transform_binary(self, operator, left, right, **kwargs):
        if (
            operator == Operator.ADD and
            isinstance(right, expressions.Constant) and
            isinstance(right.data_type, data_types.Int32) and
            right.value < 0
        ):
            right = expressions.Constant(right.data_type, -right.value)
            return expressions.Bin(Operator.SUB, left, right)
        return None

    def transform_procedure_call(self, copy_pc, proc_name, arguments):
        return _evaluate_procedure_call(copy_pc, proc_name, **self._arguments)

    def transform_access_pattern(self, expression, offset, size, **kwargs):
        assert isinstance(offset, expressions.Constant)
        assert isinstance(offset.value, int)
        assert isinstance(size, expressions.Constant)
        assert isinstance(size.value, int)
        return expressions.intermediate.Access(
            expression, offset.value, size.value)

    def transform_arrptr_pattern(self, base, scale, index, offset):
        assert isinstance(scale, expressions.Constant)
        assert isinstance(scale.value, int)
        assert isinstance(offset, expressions.Constant)
        assert isinstance(offset.value, int)
        return expressions.intermediate.Arrptr(
            base, scale.value, index, offset.value)

    def transform_eval(self, expression):
        return evaluate_expression(expression, **self._arguments)

    def transform_expect(self, actual, expected):
        assert isinstance(expected, expressions.Constant)
        return _evaluate_expect(actual, expected.value)

    def transform_i(self, expression, **kwargs):
        return _evaluate_any_int_conversion(expression)

    def transform_local_pattern(self, expression, **kwargs):
        offset = expression.transform(self)
        assert isinstance(offset, expressions.Constant)
        return expressions.intermediate.Local(offset.value)

    def transform_f(self, expression, **kwargs):
        return _evaluate_float_conversion(expression)

    def transform_global_pattern(self, var_name, **kwargs):
        address = self._int_variable_value(var_name)
        return expressions.intermediate.Global(address)

    def transform_extern_variable_pattern(self, var_name):
        name = self._str_variable_value(var_name)
        return expressions.AddressOf(expressions.Identifier(None, name))

    def transform_pattern_text(self, text):
        return expressions.UnparsedToken(
            re.sub(variable_pattern, self._replace_variable, text)
        )

    def transform_pattern_variable(self, var_name):
        value = self._match_dict[var_name]
        if not isinstance(value, str):
            return value.make_expression(self)
        return expressions.UnparsedToken(value)

    def transform_pop_fpu(self):
        return _evaluate_pop_fpu(**self._arguments)

    def transform_real64_pattern(self, high_var_name, low_var_name, **kwargs):
        high = self._int_variable_value(high_var_name)
        low = self._int_variable_value(low_var_name)
        return _evaluate_real64(high, low)

    def transform_register_pattern(self, pattern):
        reg = pattern.transform(self).emit_code()
        return _evaluate_reg_value(reg, **self._arguments)

    def transform_register_value(self, reg):
        return _evaluate_reg_value(reg, **self._arguments)

    def transform_s(self, expression):
        return _evaluate_int_conversion(expression)

    def transform_stackvar_pattern(self, offset, size):
        assert isinstance(offset, expressions.Constant)
        assert isinstance(offset.value, int)
        assert isinstance(size, expressions.Constant)
        assert isinstance(size.value, int)
        return expressions.intermediate.Stackvar(offset.value, size.value)

    def transform_u(self, expression):
        return _evaluate_uint_conversion(expression)

    def _replace_variable(self, matchobj):
        var_name = matchobj.group("variable")
        return str(self._match_dict[var_name])

    def _str_variable_value(self, var_name):
        return str(self._match_dict[var_name])

    def _int_variable_value(self, var_name):
        return int(self._match_dict[var_name])
