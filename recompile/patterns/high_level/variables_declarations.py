import expressions
import instructions
from expression_transformer import ExpressionTransformer


def insert_declarations(procedure, stack_vars):
    collector = _IdentifiersCollector(
        procedure.exclude_implicit_stack_variables(stack_vars),
        _first_body_instr(procedure))
    collector.collect_identifiers(procedure.instructions)
    return procedure.transform(collector)


class _IdentifiersCollector(ExpressionTransformer):
    def __init__(self, local_stack_variables, first_body_instr):
        self._first_body_instr = first_body_instr
        self._local_variables_set = _make_variables_set(local_stack_variables)
        self._offsets = dict(
            (identifier, offset)
            for offset, identifier in local_stack_variables.items()
            if offset < 0
        )
        self._cur_path = []
        self._cur_instr = None
        self._ids = {}
        self._to_be_declared_before = {}
        self._scope_indices = {}
        self._blocks = []
        self._cur_scope_index = None

    def collect_identifiers(self, instrs):
        self._collect(None, instrs)
        self._hoist_declarations()
        for identifier, (path, instr) in self._ids.items():
            ids = self._to_be_declared_before.get(instr)
            if ids is None:
                ids = []
                self._to_be_declared_before[instr] = ids
            ids.append(identifier)

    def _collect(self, parent_instr, instrs):
        self._cur_path.append((parent_instr, instrs))
        prev_scope_index = self._cur_scope_index
        # A labeled block is not a scope of C++
        if (
            self._cur_scope_index is None or
            not isinstance(parent_instr, instructions.LabeledBlock)
        ):
            self._cur_scope_index = len(self._scope_indices)
        self._scope_indices[id(instrs)] = self._cur_scope_index
        # Keep blocks alive: their ids are keys of the scope indices
        self._blocks.append(instrs)
        for instr in instrs:
            self._cur_instr = instr
            if isinstance(instr, instructions.IfInstruction):
                instr.if_clause.visit(self._on_visit)
                self._collect(instr, instr.if_block)
                if instr.else_block is not None:
                    self._collect(instr, instr.else_block)
            elif isinstance(instr, instructions.WhileInstruction):
                instr.clause.visit(self._on_visit)
                self._collect(instr, instr.block)
            elif isinstance(instr, instructions.LabeledBlock):
                self._collect(instr, instr.instructions)
            else:
                instr.visit(self._on_visit)
        self._cur_scope_index = prev_scope_index
        self._cur_path.pop()

    def _on_visit(self, e):
        if (
            isinstance(e, expressions.Identifier) and
            e in self._local_variables_set and
            not e.is_implicit
        ):
            self._update_id_path(e, self._cur_path, self._cur_instr)

    def _hoist_declarations(self):
        """Move declarations up to blocks matching the stack layout.

        Visual C++ 6.0 places variables of a procedure body first, then
        variables of nested blocks in preorder (see vc6check/stack-layout.md
        in branch claude/vc6-compare). A variable placed above a variable of
        a preceding block is declared at the start of their common block.
        """
        changed = True
        while changed:
            changed = False
            for identifier, (path, instr) in self._ids.items():
                offset = self._offsets.get(identifier)
                if offset is None:
                    continue
                scope = self._scope_index(path)
                for other, (other_path, _) in self._ids.items():
                    other_offset = self._offsets.get(other)
                    if (
                        other_offset is None or other_offset >= offset or
                        self._scope_index(other_path) >= scope
                    ):
                        continue
                    common_len = _common_prefix_length(path, other_path)
                    # Declare at the start of the block of C++
                    while (
                        common_len > 1 and
                        isinstance(
                            path[common_len - 1][0],
                            instructions.LabeledBlock)
                    ):
                        common_len -= 1
                    if common_len == 1:
                        first_instr = self._first_body_instr
                    else:
                        first_instr = path[common_len - 1][1][0]
                    if first_instr is None:
                        continue
                    self._ids[identifier] = path[:common_len], first_instr
                    changed = True
                    break
                if changed:
                    break

    def _scope_index(self, path):
        parent_instr, instrs = path[-1]
        return self._scope_indices[id(instrs)]

    def _update_id_path(self, identifier, new_path, new_instr):
        if identifier not in self._ids:
            self._ids[identifier] = tuple(new_path), new_instr
            return
        existing_path, existing_instr = self._ids[identifier]
        new_path = _find_common_path(existing_path, new_path)
        if len(new_path) < len(existing_path):
            new_instr, path = existing_path[len(new_path)]
        else:
            new_instr = existing_instr
        self._ids[identifier] = tuple(new_path), new_instr

    def pre_transform_block_instructions(self, block_instructions, **kwargs):
        chain = block_instructions.interval(0)
        instr = chain.as_instr(0)
        ids = self._to_be_declared_before.get(instr)
        if ids is None:
            return
        ass = None
        if isinstance(instr, instructions.Assignment):
            ass = instr
        new_instructions = []
        for identifier in ids:
            if ass is not None and identifier == ass.dst:
                instr = instructions.VariableDeclaration(ass.dst, ass.src)
                ass = None
            else:
                new_instructions.append(
                    instructions.VariableDeclaration(identifier, None))
        new_instructions.append(instr)
        chain.replace_instructions(new_instructions)


def _first_body_instr(procedure):
    """First instruction after initialization of fields of constructor."""
    instrs = list(procedure.instructions)
    last_init_instr = getattr(procedure, "last_init_instr", None)
    if last_init_instr is not None:
        index = next(
            i for i, instr in enumerate(instrs) if instr == last_init_instr)
        instrs = instrs[index + 1:]
    return instrs[0] if instrs else None


def _common_prefix_length(first_path, second_path):
    length = 0
    while (
        length < len(first_path) and length < len(second_path) and
        first_path[length][1] is second_path[length][1]
    ):
        length += 1
    return length


def _find_common_path(first_path, second_path):
    i = 0
    while i < len(first_path) and i < len(second_path):
        if first_path[i] != second_path[i]:
            break
        i += 1
    max_common_len = i
    if len(first_path) == max_common_len:
        return first_path
    if len(second_path) == max_common_len:
        return second_path
    return first_path[0:max_common_len]


def _make_variables_set(stack_vars):
    variables_set = set()
    for offset, identifier in stack_vars.items():
        variables_set.add(identifier)
    return variables_set
