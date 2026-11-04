import data_types
import expressions
from expressions.operator import Operator
from expression_transformer import ExpressionTransformer
import instructions
from patterns.make_proc_decl_from_args import make_proc_decl_from_args

_unnamed_prefix = "unknown_loc_"


def fold_temporaries(procedure, declared_types):
    """Fold temporaries created by the compiler into expressions using them.

    - A temporary object used once as an argument:
      'B_Vector t(a, b, c); x = v - t;' -> 'x = v - B_Vector(a, b, c);'
    - A temporary object of returned value copied to other one:
      'B_Vector t; x = t = v - w;' -> 'x = v - w;'
    - Copies of arguments of inlined constructors:
      'double t = a; return B_Vector(t, b, c);' -> 'B_Vector(a, b, c)'
    - Objects of inlined methods:
      'B_Surface *t = a[i]; if (t->Distance(p) < 0.0)' ->
      'if (a[i]->Distance(p) < 0.0)'
    Only unnamed variables used once with initial expressions without side
    effects are folded.
    """
    global _declared_types
    _declared_types = declared_types
    uses = _count_uses(procedure.instructions)
    instrs = _fold_block(list(procedure.instructions), uses)
    return procedure.copy(instrs=instrs)


# Classes by names to recognize constructions 'B_Vector(a, b, c)'
_declared_types = {}


def _fold_block(block, uses):
    block = [_fold_nested(instr, uses) for instr in block]
    changed = True
    while changed:
        changed = False
        for i, instr in enumerate(block):
            new_block = _try_fold(block, i, uses)
            if new_block is not None:
                block = new_block
                changed = True
                break
    return block


def _try_fold(block, index, uses):
    declaration = block[index]
    if not isinstance(declaration, instructions.VariableDeclaration):
        return None
    var = declaration.identifier
    if not var.name.startswith(_unnamed_prefix) or uses.get(var.name) != 1:
        return None
    use_index = index + 1
    while (
        use_index < len(block) and _is_declaration(block[use_index]) and
        not _uses_variable(block[use_index], var)
    ):
        use_index += 1
    if use_index >= len(block):
        return None
    use = block[use_index]
    initial = declaration.initial_expression
    if initial is None:
        transformer = _ReturnedTemporaryFolder(var)
    else:
        if _has_side_effects(initial):
            return None
        if isinstance(var.data_type, data_types.ClassType):
            if _is_construction(initial, var.data_type):
                initial = _typed_construction(initial, var.data_type)
            elif not _is_const_method_call(initial):
                return None
            # Object returned by const operator is a temporary too:
            # 'B_Vector t = v - w; f(t);' -> 'f(v - w);'
            transformer = _VariableReplacer(var, initial, None)
        else:
            transformer = _VariableReplacer(var, initial, _is_construction)
    new_use = _transform_instruction(use, transformer)
    if new_use is None or not transformer.is_replaced:
        return None
    return block[:index] + block[index + 1:use_index] + [new_use] + \
        block[use_index + 1:]


def _typed_construction(construction, class_type):
    """Make construction of object with data type of the class."""
    proc_decl = make_proc_decl_from_args(construction.arguments)
    proc_decl.change_return_type(class_type)
    return construction.copy(proc_decl=proc_decl)


def _transform_instruction(instr, transformer):
    # Temporaries are used by simple instructions only
    if isinstance(instr, instructions.VariableDeclaration):
        initial = instr.initial_expression
        if initial is None:
            return None
        return instructions.VariableDeclaration(
            instr.identifier, initial.transform(transformer))
    if isinstance(instr, instructions.IfInstruction):
        # Temporary used once is used in the clause only
        return instructions.IfInstruction(
            instr.if_clause.transform(transformer), instr.if_block,
            instr.else_block)
    if not isinstance(instr, (
        instructions.Assignment, instructions.CodeInstruction,
        instructions.ReturnInstruction,
    )):
        return None
    return instr.transform(transformer)


class _VariableReplacer(ExpressionTransformer):
    """Replace variable with expression (in arguments of constructions)."""

    def __init__(self, var, expression, is_parent_allowed):
        self._var = var
        self._expression = expression
        self._is_parent_allowed = is_parent_allowed
        self.is_replaced = False

    def transform_identifier(self, identifier, **kwargs):
        if self._is_parent_allowed is not None:
            return None
        return self._replace(identifier)

    def transform_make_reference(self, expression, **kwargs):
        # Temporary object is bound to reference parameter
        if expression is self._expression:
            return expression
        return None

    def transform_procedure_call(self, copy_pc, proc_name, arguments, **kw):
        if self._is_parent_allowed is None:
            return None
        pc = copy_pc()
        # Object of inlined method is a temporary too:
        # 'B_Surface *t = a[i]; t->Distance(p);' -> 'a[i]->Distance(p);'
        is_object = (
            pc.is_method and pc.arguments and
            _is_variable(pc.arguments[0], self._var)
        )
        if not _is_construction(pc, None) and not is_object:
            return None
        new_arguments = [self._replace(arg) or arg for arg in pc.arguments]
        if not self.is_replaced:
            return None
        return pc.copy(arguments=new_arguments)

    def _replace(self, e):
        if not _is_variable(e, self._var):
            return None
        self.is_replaced = True
        return self._expression


class _ReturnedTemporaryFolder(ExpressionTransformer):
    """Replace 'x = t = f()' with 'x = f()' for returned object 't'."""

    def __init__(self, var):
        self._var = var
        self.is_replaced = False

    def transform_binary(self, operator, left, right, **kwargs):
        if operator != Operator.ASS:
            return None
        if isinstance(left, expressions.MakeReference):
            left = left.expression
        if not _is_variable(left, self._var):
            return None
        if not isinstance(right, expressions.ProcedureCall):
            return None
        self.is_replaced = True
        return right


def _is_construction(e, class_type):
    """Check for construction of an object: 'B_Vector(a, b, c)'."""
    if not isinstance(e, expressions.ProcedureCall) or e.is_method:
        return False
    if class_type is None:
        return isinstance(
            _declared_types.get(e.name), data_types.ClassType)
    return e.name == class_type.class_name


def _is_const_method_call(e):
    """Check for call of const method, e.g. 'operator -' of B_Vector."""
    return (
        isinstance(e, expressions.ProcedureCall) and
        e.proc_decl is not None and e.proc_decl.is_const
    )


def _is_variable(e, var):
    return isinstance(e, expressions.Identifier) and e.name == var.name


def _is_declaration(instr):
    return (
        isinstance(instr, instructions.VariableDeclaration) and
        instr.initial_expression is None
    ) or (
        isinstance(instr, instructions.VariableDeclaration) and
        instr.identifier.name.startswith(_unnamed_prefix)
    )


def _uses_variable(instr, var):
    return _count_uses([instr]).get(var.name, 0) > 0


def _count_uses(instrs):
    uses = {}

    def on_visit(e, **kwargs):
        if isinstance(e, expressions.Identifier):
            uses[e.name] = uses.get(e.name, 0) + 1

    _visit_block(instrs, on_visit)
    return uses


def _visit_block(instrs, on_visit):
    for instr in instrs:
        if isinstance(instr, instructions.IfInstruction):
            instr.if_clause.visit(on_visit)
            _visit_block(instr.if_block, on_visit)
            _visit_block(instr.else_block or [], on_visit)
        elif isinstance(instr, instructions.WhileInstruction):
            instr.clause.visit(on_visit)
            _visit_block(instr.block, on_visit)
        elif isinstance(instr, instructions.LabeledBlock):
            _visit_block(instr.instructions, on_visit)
        else:
            instr.visit(on_visit)


_increments = tuple(
    getattr(expressions, name)
    for name in ("Increment", "Decrement", "PreIncrement", "PreDecrement")
    if hasattr(expressions, name)
)


def _has_side_effects(e):
    found = []

    def on_visit(sub_e, **kwargs):
        if isinstance(sub_e, _increments):
            found.append(sub_e)
        elif isinstance(sub_e, expressions.Bin) and sub_e.operator in (
            Operator.ASS, Operator.ADD_ASS, Operator.SUB_ASS
        ):
            found.append(sub_e)
        elif isinstance(sub_e, expressions.ProcedureCall) and not (
            _is_construction(sub_e, None) or _is_const_method_call(sub_e)
        ):
            found.append(sub_e)

    e.visit(on_visit)
    return bool(found)


def _fold_nested(instr, uses):
    if isinstance(instr, instructions.IfInstruction):
        else_block = instr.else_block
        if else_block is not None:
            else_block = _fold_block(else_block, uses)
        return instructions.IfInstruction(
            instr.if_clause, _fold_block(instr.if_block, uses), else_block)
    if isinstance(instr, instructions.WhileInstruction):
        return instructions.WhileInstruction(
            instr.clause, _fold_block(instr.block, uses))
    if isinstance(instr, instructions.LabeledBlock):
        return instructions.LabeledBlock(
            instr.label, _fold_block(instr.instructions, uses))
    if isinstance(instr, instructions.Switch):
        for label, block in instr.blocks_dict.items():
            instr.blocks_dict[label] = _fold_block(block, uses)
        return instr
    block = getattr(instr, "block", None)
    if isinstance(block, list) and hasattr(instr, "copy"):
        return instr.copy(block=_fold_block(block, uses))
    return instr
