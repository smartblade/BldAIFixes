import data_types
import expressions
from expressions.do_pointer_dereference import do_pointer_dereference
from expressions.operator import Operator


class LocalsAnalysis:
    def __init__(self):
        self._types_by_offset = {}
        self._compared_types_by_offset = {}
        self._local_pointees_sizes = {}
        # Uses of locals in the current transformation pass by offset:
        # [number of uses, number of typed uses, start, end of accessed data]
        self._local_uses = {}
        # Extents of locals used only by typed accesses in the last pass
        self._local_extents = {}
        # Pointee types of casts of locals in the current and the last pass
        self._cur_local_types = {}
        self._local_types = {}
        # Sizes of stack accesses in instructions by offset
        self._stackvar_sizes = {}

    def process_assignment(self, dst, src):
        if not isinstance(dst, expressions.intermediate.Stackvar):
            return
        assert dst.size == src.data_type.size
        self._update_type(dst.offset, src.data_type)

    def on_transformation_finished(self):
        self._local_extents = dict(
            (offset, (offset + start, offset + end))
            for offset, (uses, typed_uses, start, end)
            in self._local_uses.items()
            if uses == typed_uses
        )
        self._local_uses = {}
        self._local_types = self._cur_local_types
        self._cur_local_types = {}

    def _process_typed_local_use(self, local, start, end):
        uses = self._local_uses.setdefault(local.offset, [0, 0, 0, 0])
        uses[1] += 1
        uses[2] = min(uses[2], start)
        uses[3] = max(uses[3], end)

    def process_access(self, expression, offset, size):
        if isinstance(expression, expressions.intermediate.Local):
            self._process_typed_local_use(expression, offset, offset + size)
            return
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
        if isinstance(expression, expressions.intermediate.Local):
            if (
                isinstance(data_type, data_types.Pointer32) and
                data_type.pointee is not None
            ):
                self._process_typed_local_use(
                    expression, 0, data_type.pointee.size)
                self._cur_local_types.setdefault(
                    expression.offset, []).append(data_type.pointee)
            return
        if not isinstance(expression, expressions.intermediate.Stackvar):
            return
        assert expression.size == data_type.size
        self._update_type(expression.offset, data_type)

    def collect_stack_accesses(self, instrs):
        """Collect stack accesses remaining in instructions."""
        self._stackvar_sizes = {}

        def on_visit(e, **kwargs):
            if isinstance(e, expressions.intermediate.Stackvar):
                self._stackvar_sizes.setdefault(e.offset, set()).add(e.size)

        for instr in instrs:
            instr.visit(on_visit)

    def process_local(self, local):
        self._local_uses.setdefault(local.offset, [0, 0, 0, 0])[0] += 1
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

    def process_memory_copy(self, arguments):
        """Process 'memcpy(dst, src, size)' accessing locals."""
        size = arguments[2]
        if not isinstance(size, expressions.Constant):
            return
        if not isinstance(size.value, int):
            return
        for argument in arguments[:2]:
            if isinstance(argument, expressions.intermediate.Local):
                self._process_typed_local_use(argument, 0, size.value)

    def _get_min_local_ptr_offset(self, ignore_extents=False):
        min_local_ptr_offset = 0
        for local, size in self._local_pointees_sizes.items():
            if size == 1:
                continue
            # Locals with known extents don't hide variables above them
            if not ignore_extents and local.offset in self._local_extents:
                continue
            if local.offset < min_local_ptr_offset:
                min_local_ptr_offset = local.offset
        return min_local_ptr_offset

    def fill_stack_variables(self, stack_vars, variable_names):
        min_local_ptr_offset = self._get_min_local_ptr_offset()
        self._fill_struct_variables(
            stack_vars, variable_names, min_local_ptr_offset)
        # Variables hidden by locals with unknown extents before
        min_any_local_ptr_offset = self._get_min_local_ptr_offset(
            ignore_extents=True)
        for offset, data_type in self._types_by_offset.items():
            if data_type is None:
                continue
            if offset in stack_vars:
                continue
            if offset >= min_local_ptr_offset:
                continue
            if self._overlaps_local(offset, data_type):
                continue
            if (
                offset >= min_any_local_ptr_offset and
                self._overlaps_stackvars(offset, data_type)
            ):
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

    def _overlaps_stackvars(self, offset, data_type):
        size = data_type.size
        for other_offset, sizes in self._stackvar_sizes.items():
            for other_size in sizes:
                if other_offset == offset and other_size == size:
                    continue
                if (
                    other_offset < offset + size and
                    offset < other_offset + other_size
                ):
                    return True
        return False

    def _fill_struct_variables(
        self, stack_vars, variable_names, min_local_ptr_offset
    ):
        """Make variables of classes of locals used as pointers to them."""
        for offset, (start, end) in self._local_extents.items():
            class_type = self._get_local_class(offset)
            if class_type is None:
                continue
            if start != offset or end != offset + class_type.size:
                continue
            if offset in stack_vars or offset >= min_local_ptr_offset:
                continue
            if not self._are_fields_accessed(offset, class_type):
                continue
            name = variable_names.get(offset)
            if name is None:
                name = "unknown_loc_{:02X}".format(-offset)
            stack_vars[offset] = expressions.Identifier(class_type, name)

    def _get_local_class(self, offset):
        types = self._local_types.get(offset, [])
        if not types or not isinstance(types[0], data_types.ClassType):
            return None
        if any(not data_types.are_same(t, types[0]) for t in types):
            return None
        return types[0]

    def _are_fields_accessed(self, offset, class_type):
        """Check that all accesses inside the variable are its fields."""
        end = offset + class_type.size
        ptr = expressions.Identifier(data_types.Pointer32(class_type), "ptr")
        accesses = [
            (other_offset, size)
            for other_offset, sizes in self._stackvar_sizes.items()
            for size in sizes
        ] + [
            (local_offset, local_end - local_offset)
            for local_offset, (local_start, local_end)
            in self._local_extents.items()
            if local_offset != offset and local_start == local_offset
        ]
        for other_offset, size in accesses:
            if other_offset + size <= offset or end <= other_offset:
                continue
            if other_offset < offset or end < other_offset + size:
                return False
            try:
                field = do_pointer_dereference(
                    ptr, other_offset - offset, size)
            except Exception:
                return False
            if field is None:
                return False
        # Locals with accesses before them can't be inside the variable
        extents = self._local_extents.items()
        for local_offset, (local_start, local_end) in extents:
            if local_offset == offset or local_start == local_offset:
                continue
            if local_start < end and offset < local_end:
                return False
        return True

    def _overlaps_local(self, offset, data_type):
        size = data_type.size if data_type is not None else 1
        return any(
            start < offset + size and offset < end
            for start, end in self._local_extents.values()
        )

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
