import data_types
import expressions
from expressions.operator import Operator


class LocalsAnalysis:
    def __init__(self):
        self._types_by_offset = {}
        self._compared_types_by_offset = {}
        self._local_pointees_sizes = {}
        self._stackvar_sizes = {}

    def process_assignment(self, dst, src):
        if not isinstance(dst, expressions.intermediate.Stackvar):
            return
        assert dst.size == src.data_type.size
        self._update_type(dst.offset, src.data_type)

    def process_access(self, expression, offset, size):
        if not isinstance(expression, expressions.intermediate.Stackvar):
            return
        if expression.offset not in self._types_by_offset:
            return
        existing_type = self._types_by_offset[expression.offset]
        if existing_type is None:
            return
        if (
            not isinstance(existing_type, data_types.Pointer32) and
            not isinstance(existing_type, data_types.AnyInt) and
            not isinstance(existing_type, data_types.UnknownTypes)
        ):
            self._types_by_offset[expression.offset] = None

    def process_binary(self, operator, left, right):
        if (
            operator != Operator.LT and operator != Operator.LE and
            operator != Operator.GT and operator != Operator.GE
        ):
            return
        if not data_types.are_same(left.data_type, right.data_type):
            return
        if not isinstance(
            left.data_type, (data_types.Int32, data_types.UInt32)
        ):
            return
        self._process_comparison_operand(left)
        self._process_comparison_operand(right)

    def _process_comparison_operand(self, e):
        if not isinstance(e, expressions.ReinterpretCast):
            return
        stackvar = e.expression
        if not isinstance(stackvar, expressions.intermediate.Stackvar):
            return
        if stackvar.size != e.data_type.size:
            return
        if stackvar.offset not in self._compared_types_by_offset:
            self._compared_types_by_offset[stackvar.offset] = e.data_type
            return
        existing_type = self._compared_types_by_offset[stackvar.offset]
        if existing_type is None:
            return
        if not data_types.are_same(existing_type, e.data_type):
            self._compared_types_by_offset[stackvar.offset] = None

    def process_reinterpret(self, data_type, expression):
        if not isinstance(expression, expressions.intermediate.Stackvar):
            return
        assert expression.size == data_type.size
        self._update_type(expression.offset, data_type)

    def process_stackvar(self, offset, size):
        self._stackvar_sizes.setdefault(offset, set()).add(size)

    def process_local(self, local):
        if local not in self._local_pointees_sizes:
            self._local_pointees_sizes[local] = None

    def process_arguments(self, arguments, call_characteristics):
        for i, argument in enumerate(arguments):
            if not isinstance(argument, expressions.intermediate.Local):
                continue
            param_characteristics = call_characteristics.parameters[i]
            array_length = _get_array_length(param_characteristics, arguments)
            pointee_size = _get_pointee_size(argument.data_type, array_length)
            if pointee_size is None:
                continue
            if self._local_pointees_sizes[argument] is None:
                self._local_pointees_sizes[argument] = pointee_size
            assert self._local_pointees_sizes[argument] == pointee_size

    def _get_min_local_ptr_offset(self):
        min_local_ptr_offset = 0
        for local, size in self._local_pointees_sizes.items():
            if size == 1:
                continue
            if local.offset < min_local_ptr_offset:
                min_local_ptr_offset = local.offset
        return min_local_ptr_offset

    def fill_stack_variables(self, stack_vars, variable_names):
        min_local_ptr_offset = self._get_min_local_ptr_offset()
        for offset, data_type in self._types_by_offset.items():
            if data_type is None:
                continue
            if offset in stack_vars:
                continue
            if offset >= min_local_ptr_offset:
                continue
            assert offset < 0
            name = variable_names.get(offset)
            if name is None:
                name = "unknown_loc_{:02X}".format(-offset)
            if isinstance(data_type, data_types.AnyInt):
                data_type = self._compared_types_by_offset.get(offset)
                if data_type is None:
                    continue
            if not _is_acceptable_type(data_type):
                if not self._is_acceptable_float(offset, data_type):
                    continue
            stack_vars[offset] = expressions.Identifier(data_type, name)

    def _is_acceptable_float(self, offset, data_type):
        """Check if floating point variable doesn't overlap other data."""
        if not isinstance(data_type, (data_types.Float, data_types.Double)):
            return False
        if self._stackvar_sizes.get(offset, set()) - {data_type.size}:
            return False
        for other_offset, sizes in self._stackvar_sizes.items():
            if other_offset == offset:
                continue
            if offset < other_offset < offset + data_type.size:
                return False
            if any(other_offset < offset < other_offset + size
                   for size in sizes):
                return False
        return True

    def _update_type(self, offset, data_type):
        if offset >= 0:
            return
        if offset not in self._types_by_offset:
            self._types_by_offset[offset] = data_type
            return
        existing_type = self._types_by_offset[offset]
        if existing_type is None:
            return
        if (
            not data_types.are_same(data_type, existing_type) and
            data_types.are_compatible(data_type, existing_type)
        ):
            self._types_by_offset[offset] = data_type
        elif (
            not data_types.are_compatible(existing_type, data_type) and
            not _are_same_sized_unsigned(existing_type, data_type)
        ):
            if (
                existing_type.is_any_int and data_type.is_any_int and
                existing_type.size == data_type.size
            ):
                self._types_by_offset[offset] = data_types.AnyInt(
                    data_type.size
                )
            else:
                self._types_by_offset[offset] = None


def _is_acceptable_type(data_type):
    if isinstance(data_type, data_types.Pointer32):
        if isinstance(data_type.pointee, data_types.ClassType):
            return True
    if data_type.is_any_int and data_type.size == 4:
        return True
    if isinstance(data_type, data_types.UChar):
        return True
    return False


def _are_same_sized_unsigned(first_type, second_type):
    if first_type.size != second_type.size:
        return False
    return first_type.is_unsigned_int and second_type.is_unsigned_int


def _get_array_length(param_characteristics, arguments):
    if param_characteristics.array_length is None:
        return None
    param_index = param_characteristics.array_length.parameter
    if param_index is None:
        return None
    array_length_const = arguments[param_index]
    if not isinstance(array_length_const, expressions.Constant):
        return None
    if not array_length_const.data_type.is_any_int:
        return None
    assert isinstance(array_length_const.value, int)
    return array_length_const.value


def _get_pointee_size(parameter_type, array_length):
    if array_length is None:
        return None
    if not isinstance(parameter_type, data_types.Pointer32):
        return None
    if parameter_type.pointee is None:
        parameter_pointee_size = 1
    else:
        parameter_pointee_size = parameter_type.pointee.size
    return parameter_pointee_size * array_length
