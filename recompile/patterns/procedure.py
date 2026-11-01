from custom_block_transformer import transform_block
import data_types
import expressions
import instructions
from instructions.extract_vtbl_addr_from_assign import\
    extract_vtbl_addr_from_assign
from hex_conversion import to_hex


class Procedure:
    def __init__(
        self, proc_info, address, proc_decl, instrs, last_init_instr
    ):
        self._proc_info = proc_info
        self._address = address
        self._proc_decl = proc_decl
        self._instructions = tuple(instrs)
        self._last_init_instr = last_init_instr

    def copy(self, **kwargs):
        default_map = dict(
            proc_info=self._proc_info,
            address=self._address,
            proc_decl=self._proc_decl,
            instrs=self._instructions,
            last_init_instr=self._last_init_instr,
        )
        for key, value in default_map.items():
            if key not in kwargs:
                kwargs[key] = value
        return self.__class__(**kwargs)

    @property
    def proc_info(self):
        return self._proc_info

    @property
    def proc_decl(self):
        return self._proc_decl

    @property
    def address(self):
        return self._address

    @property
    def instructions(self):
        return self._instructions

    @property
    def implicit_stack_variables(self):
        stack_vars = self._proc_info.stack_variables
        if self._proc_decl is not None:
            stack_vars.update(self._proc_decl.stack_variables)
        return stack_vars

    def exclude_implicit_stack_variables(self, stack_vars):
        implicit_stack_variables = self.implicit_stack_variables
        return dict(
            (o, identifier) for o, identifier in stack_vars.items()
            if o not in implicit_stack_variables
        )

    def transform(self, transformer, **kwargs):
        new_instrs = transform_block(self._instructions, transformer, **kwargs)
        return self.copy(instrs=new_instrs)

    def emit_code(self, writer, show_address=True, is_definition=True):
        if self._proc_decl is not None:
            decl_string = self._proc_decl.get_declaration(
                is_definition=is_definition
            )
        else:
            decl_string = "p{}".format(to_hex(self._address))
        if not show_address:
            writer.write_line()
        elif self._address is not None:
            writer.write_line("// address: 0x{}".format(to_hex(self._address)))
        else:
            writer.write_line("// address: inline")
        writer.write_line(decl_string)
        init_instrs, body_instrs = self._extract_initialization_section()
        _write_initialization(writer, self._proc_info, init_instrs)
        writer.write_line("{")
        with writer.indent():
            for instr in body_instrs:
                instr.emit_code(writer)
        writer.write_line("}")

    def _extract_initialization_section(self):
        if self._last_init_instr is None:
            return [], self._instructions
        is_initialization = True
        init_instrs = []
        body_instrs = []
        for instr in self._instructions:
            if is_initialization:
                if not self._is_implicit_instr(instr):
                    init_instrs.append(instr)
                if instr == self._last_init_instr:
                    is_initialization = False
            else:
                body_instrs.append(instr)
        assert not is_initialization
        return init_instrs, body_instrs

    def _is_implicit_instr(self, instr):
        if instr == self._last_init_instr:
            vtbl_addr = extract_vtbl_addr_from_assign(self._proc_info, instr)
            if vtbl_addr is not None:
                return True
        return _is_default_constructor_call(instr)


def _is_default_constructor_call(instr):
    if not isinstance(instr, instructions.CodeInstruction):
        return False
    pc = instr.expression
    if not isinstance(pc, expressions.ProcedureCall):
        return False
    if not pc.proc_decl.is_constructor:
        return False
    if len(pc.arguments) != 1:
        return False
    return True


def _write_initialization(writer, proc_info, init_instrs):
    if len(init_instrs) == 0:
        return
    writer.write_line(":")
    with writer.indent():
        last_instr = init_instrs[-1]
        sep = ","
        for instr in init_instrs:
            pc = _make_init_call(instr, proc_info)
            if instr == last_instr:
                sep = ""
            writer.write_line("{}{}".format(pc.emit_code(), sep))


def _make_init_call(instr, proc_info):
    if isinstance(instr, instructions.Assignment):
        field_access = instr.dst
        assert isinstance(field_access, expressions.FieldAccess)
        # Fields of class types are copied only from objects of the class
        assert (
            not isinstance(field_access.data_type, data_types.ClassType) or
            data_types.are_same(field_access.data_type, instr.src.data_type)
        )
        assert proc_info.is_this_expression(field_access.expression)
        name = field_access.field_name
        return expressions.ProcedureCall(
            name=name, is_method=False, arguments=[instr.src])
    assert isinstance(instr, instructions.CodeInstruction)
    pc = instr.expression
    assert isinstance(pc, expressions.ProcedureCall)
    assert pc.is_method
    obj = pc.arguments[0]
    if proc_info.is_this_expression(obj):
        name = pc.name
    else:
        assert isinstance(obj, expressions.AddressOf)
        field_access = obj.expression
        assert isinstance(field_access, expressions.FieldAccess)
        assert isinstance(field_access.data_type, data_types.ClassType)
        assert field_access.data_type.class_name == pc.name
        assert proc_info.is_this_expression(field_access.expression)
        name = field_access.field_name
    return pc.copy(name=name, is_method=False, arguments=pc.arguments[1:])
