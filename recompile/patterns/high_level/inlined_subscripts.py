import data_types
import expressions
from expression_transformer import ExpressionTransformer
from expressions.operator import Operator
import instructions
from block_visitor import visit_block
from expressions.do_pointer_dereference import do_pointer_dereference


def restore_inlined_subscripts(instrs):
    """Restore calls of inlined 'TYPE *operator[](index) const' of arrays.

    The inlined operator returns 'elements[index]' in a temporary of the
    compiler used once:
    - a constant index is computed at run time, 'xor eax, eax' and
      'shl eax, 2' is 'elements + 4 * 0':
          t = *(elements + 4 * 0); leaf->sectors = t;
      -> leaf->sectors = map[0];
    - the temporary is an argument of an inlined method called by a pointer
      to the object in a temporary: the temporary of the argument is above
      the temporary of the object in the stack frame, a copy of an argument
      that isn't returned by an inlined function is below it:
          t = elements[i]; p = (int)node + 4; Append(p, t);
      -> p = (int)node + 4; Append(p, map[i]);
    """
    uses = _count_stackvar_uses(instrs)
    return _restore_block(instrs, uses)


def _restore_block(block, uses):
    block = [_restore_nested(instr, uses) for instr in block]
    new_block = []
    i = 0
    while i < len(block):
        new_instrs = _restore_at(block, i, uses)
        if new_instrs is not None:
            new_block.extend(new_instrs)
            i += 1 + len(new_instrs)
            continue
        new_block.append(block[i])
        i += 1
    return new_block


def _restore_nested(instr, uses):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _restore_block(else_block, uses)
        return instructions.IfInstruction(
            instr.if_clause, _restore_block(instr.if_block, uses),
            else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _restore_block(instr.block, uses))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _restore_block(instr.instructions, uses))
    return instr


def _restore_at(block, index, uses):
    """Return instructions replacing block[index:index + 1 + len(result)]."""
    assignment = block[index]
    if not isinstance(assignment, instructions.Assignment):
        return None
    temporary = assignment.dst
    if not isinstance(temporary, expressions.intermediate.Stackvar):
        return None
    if temporary.size != 4 or uses.get(temporary.offset, 0) != 2:
        return None
    if index + 1 >= len(block):
        return None
    subscript = _constant_subscript(assignment.src)
    if subscript is not None:
        use = _replace(block[index + 1], temporary, subscript)
        if use is None:
            return None
        return [use]
    subscript = _subscript(assignment.src)
    if subscript is None or index + 2 >= len(block):
        return None
    this_assignment = block[index + 1]
    if not isinstance(this_assignment, instructions.Assignment):
        return None
    this_temporary = this_assignment.dst
    if not isinstance(this_temporary, expressions.intermediate.Stackvar):
        return None
    if this_temporary.offset >= temporary.offset:
        return None
    call = block[index + 2]
    if not _is_method_call_with(call, this_temporary, temporary):
        return None
    use = _replace(call, temporary, subscript)
    if use is None:
        return None
    return [this_assignment, use]


def _is_method_call_with(instr, this_temporary, argument):
    if not isinstance(instr, instructions.CodeInstruction):
        return False
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall) or not pc.is_method:
        return False
    if len(pc.arguments) < 2:
        return False
    return (
        _is_stackvar(_strip_cast(pc.arguments[0]), this_temporary) and
        any(
            _is_stackvar(_strip_cast(a), argument)
            for a in pc.arguments[1:]
        )
    )


def _constant_subscript(e):
    """Subscript of '*(obj.elements + scale * index)' with constants."""
    if not isinstance(e, expressions.intermediate.Access):
        return None
    if e.offset != 0 or e.size != 4:
        return None
    arrptr = e.expression
    if not isinstance(arrptr, expressions.intermediate.Arrptr):
        return None
    if arrptr.scale != 1 or arrptr.offset != 0:
        return None
    product = arrptr.index
    if not isinstance(product, expressions.Bin):
        return None
    if product.operator != Operator.MUL:
        return None
    left, right = product.left, product.right
    if not (
        isinstance(left, expressions.Constant) and
        isinstance(right, expressions.Constant)
    ):
        return None
    if left.value != 4 or not isinstance(right.value, int):
        return None
    return _make_subscript(
        arrptr.base,
        expressions.Constant(data_types.UInt32(), right.value))


def _subscript(e):
    """Subscript of 'obj.elements[index]'."""
    if not isinstance(e, expressions.ArrayAccess):
        return None
    return _make_subscript(e.array, e.index)


def _make_subscript(elements, index):
    if not isinstance(elements, expressions.FieldAccess):
        return None
    if elements.field_name != "elements":
        return None
    obj_ptr = elements.expression
    class_type = _pointee_class(obj_ptr.data_type)
    if class_type is None or not _has_subscript_operator(class_type):
        return None
    elements_type = elements.data_type
    if not isinstance(elements_type, data_types.Pointer32):
        return None
    if isinstance(obj_ptr, expressions.AddressOf):
        obj = obj_ptr.expression
    else:
        obj = expressions.Dereference(obj_ptr)
    return expressions.SubscriptOperator(obj, index, elements_type.pointee)


def _pointee_class(data_type):
    if not isinstance(data_type, data_types.Pointer32):
        return None
    pointee = data_type.pointee
    if isinstance(pointee, data_types.ClassType):
        return pointee
    return None


def _has_subscript_operator(class_type):
    """Check for operator[] of the class, of its template or parents."""
    while class_type is not None:
        for cur_class in (class_type, class_type.template):
            if cur_class is None:
                continue
            for method in cur_class.other_methods:
                if method.proc_name.replace(" ", "") == "operator[]":
                    return True
        class_type = class_type.parent
    return False


class _Replacer(ExpressionTransformer):
    def __init__(self, temporary, expression):
        self._temporary = temporary
        self._expression = expression
        self.num_replaced = 0

    def transform_stackvar(self, offset, size, **kwargs):
        if offset == self._temporary.offset and size == self._temporary.size:
            self.num_replaced += 1
            return self._expression
        return None


def _replace(instr, temporary, expression):
    if not isinstance(instr, (
        instructions.Assignment, instructions.CodeInstruction,
    )):
        return None
    replacer = _Replacer(temporary, expression)
    new_instr = instr.transform(replacer)
    if replacer.num_replaced != 1:
        return None
    return new_instr


def _strip_cast(e):
    while isinstance(e, expressions.ReinterpretCast):
        e = e.expression
    return e


def _is_stackvar(e, stackvar):
    return (
        isinstance(e, expressions.intermediate.Stackvar) and
        e.offset == stackvar.offset and e.size == stackvar.size
    )


def _count_stackvar_uses(instrs):
    uses = {}

    def on_visit(e, **kwargs):
        if isinstance(e, expressions.intermediate.Stackvar):
            uses[e.offset] = uses.get(e.offset, 0) + 1

    visit_block(instrs, on_visit)
    return uses


def restore_subscripts_of_fields(instrs):
    """Restore fields of elements returned by inlined 'TYPE &operator[]'.

    The inlined operator of array_t returns a reference to the element,
    the address is computed by the size of the element at run time:
        *(double *)(points.elements + 32 * i + 8) -> points[i].v.y
    """
    from custom_block_transformer import transform_block
    return transform_block(list(instrs), _FieldSubscriptTransformer())


class _FieldSubscriptTransformer(ExpressionTransformer):
    def transform_access(self, expression, offset, size, **kwargs):
        if offset != 0:
            return None
        if not isinstance(expression, expressions.intermediate.Arrptr):
            return None
        if expression.scale != 1:
            return None
        product = expression.index
        if not isinstance(product, expressions.Bin):
            return None
        if product.operator != Operator.MUL:
            return None
        if not isinstance(product.left, expressions.Constant):
            return None
        elements = expression.base
        if not isinstance(elements, expressions.FieldAccess):
            return None
        elements_type = elements.data_type
        if not isinstance(elements_type, data_types.Pointer32):
            return None
        element_type = elements_type.pointee
        if not isinstance(element_type, data_types.ClassType):
            return None
        if product.left.value != element_type.size:
            return None
        if element_type.size <= expression.offset:
            return None
        index = product.right
        if isinstance(index, expressions.Constant):
            index = expressions.Constant(data_types.UInt32(), index.value)
        subscript = _make_subscript(elements, index)
        if subscript is None:
            return None
        try:
            field = do_pointer_dereference(
                expressions.AddressOf(subscript), expression.offset, size)
        except Exception:
            return None
        return field
