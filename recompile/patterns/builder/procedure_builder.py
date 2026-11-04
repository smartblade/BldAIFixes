from calling_convention import CallingConvention
import data_types
import expressions
from hex_conversion import from_hex
import instructions
from patterns.procedure import Procedure
from procedure_declaration import ProcedureDeclaration

from .block_builder import BlockBuilder
from .ensure_tmp_reg_def import ensure_tmp_reg_def
from .make_float_assignment import make_float_assignment
from .switch_builder import SwitchBuilder


class ProcedureBuilder:
    def __init__(self, proc_decl, proc_addr, standard_inlines):
        self._instructions = []
        self._current_block = BlockBuilder(self._instructions)
        self._switch_builder = SwitchBuilder()
        self._proc_decl = proc_decl
        if self._proc_decl is not None:
            self._method_class = self._proc_decl.method_class
        else:
            self._method_class = None
        self._proc_addr = proc_addr
        self._standard_inlines = standard_inlines

    def make_standard(self, name):
        self.make_prolog(allocated=expressions.Constant(data_types.UInt32, 0))
        self.make_call(name=name)

    def validate_label(self, name, address=None):
        name = name.emit_code()
        if address is None:
            address = self._proc_addr
        else:
            address = from_hex(address.emit_code())
        if name not in self._standard_inlines:
            self._standard_inlines[name] = address
        if self._standard_inlines[name] != address:
            raise Exception(
                "Expected address of {} is {} but was: {}".format(
                    name, self._standard_inlines[name], address))

    def make_prolog(self, allocated):
        self._add_instruction(
            instructions.ProcedureInfo(
                self._method_class, from_hex(allocated.emit_code())))

    def make_preserved(self, reg):
        if isinstance(self._last_instruction, instructions.ProcedureInfo):
            self._last_instruction.preserve(reg.emit_code())
            return
        raise Exception(
            "Unexpected instruction type {}".format(
                type(self._last_instruction)))

    def make_restore(self, restore):
        self._add_instruction(instructions.CodeInstruction(restore))

    def make_epilog(self, size):
        self._pop_restore_instructions()
        stack_delta = from_hex(size.emit_code())
        self._expect_first_procedure_info().set_stack_delta(stack_delta)
        self._add_instruction(instructions.ReturnInstruction(None))

    def make_instruction(self, expression):
        self._add_instruction(instructions.CodeInstruction(expression))

    @staticmethod
    def validate(expect):
        assert isinstance(expect, expressions.Constant)

    def make_assignment(self, dst, src):
        if isinstance(self._last_instruction, instructions.ProcedureInfo):
            if self._last_instruction.is_this_expression(src):
                self._last_instruction.define_this_offset(dst)
                return
        self._add_instruction(instructions.Assignment(dst, src))

    def make_float_assignment(self, dst, src):
        make_float_assignment(self._current_block, dst, src)

    def make_jump(self, address, condition=None):
        hex_addr = address.emit_code()
        assert hex_addr.startswith("0x")
        label = "l{}".format(hex_addr[2:])
        goto = instructions.Goto(label)
        if condition is None:
            self._add_instruction(goto)
            return
        self._add_instruction(instructions.IfInstruction(condition, [goto]))

    def make_switch(self, index, addresses, indices=None):
        hex_addr_addresses = addresses.emit_code()
        assert hex_addr_addresses.startswith("0x")
        hex_addr_indices = None
        if indices is not None:
            hex_addr_indices = indices.emit_code()
            assert hex_addr_indices.startswith("0x")
        switch = self._switch_builder.make_switch(
            index, hex_addr_addresses, hex_addr_indices)
        self._add_instruction(switch)

    def add_address_entry(self, address):
        self._switch_builder.add_address_entry(address.emit_code())

    def add_32bit_index_entry(self, index32):
        self._switch_builder.add_32bit_index_entry(index32)

    def add_8bit_index_entry(self, index8):
        self._switch_builder.add_8bit_index_entry(index8)

    def start_labeled_variable(self, address):
        hex_addr = address.emit_code()
        assert hex_addr.startswith("0x")
        self._switch_builder.start_table(hex_addr)

    def make_arg(self, arg):
        self._add_instruction(instructions.CodeInstruction(arg))

    def make_call(self, address=None, name=None, expression=None):
        assert address is not None or name is not None or expression is not None
        pc_args = {}
        if address is not None:
            pc_args["callee_addr"] = from_hex(address.emit_code())
        if name is not None:
            pc_args["name"] = name.emit_code()
        if expression is not None:
            pc_args["callee"] = expression
        procedure_call = expressions.ProcedureCall(**pc_args)
        self._add_instruction(instructions.CodeInstruction(procedure_call))

    def make_method_call(self, name, object, argument):
        """Make call of method inlined by compiler with unused result."""
        procedure_call = expressions.ProcedureCall(
            name=name.emit_code(), is_method=True,
            arguments=[object, argument])
        self._add_instruction(instructions.CodeInstruction(procedure_call))

    def make_fpu_method_call(self, name, object, argument):
        """Push result of floating point method inlined by compiler."""
        name = name.emit_code()
        proc_decl = ProcedureDeclaration(
            name, CallingConvention.THISCALL, None,
            [(data_types.Pointer32(), "point")], data_types.Double(),
            is_const=True)
        procedure_call = expressions.ProcedureCall(
            name=name, is_method=True, arguments=[object, argument],
            proc_decl=proc_decl)
        self.push_fpu(procedure_call)

    def add_stack_pointer(self, offset):
        self._current_block.merge_args_into_cdecl_procedure_call(
            from_hex(offset.emit_code()))

    def update_temporary_reg(self, dst, src):
        reg = dst.emit_code()
        tmp_def = ensure_tmp_reg_def(self._current_block)
        tmp_def.define_reg_value(reg, src)

    def push_fpu(self, src):
        tmp_def = ensure_tmp_reg_def(self._current_block)
        tmp_def.push_fpu(src)

    def pop_reg_value(self, reg):
        return self._current_block.pop_reg_value(reg)

    def pop_fpu(self):
        return self._current_block.pop_reg_value("fpu")

    def start_labeled_block(self, address):
        hex_addr = address.emit_code()
        assert hex_addr.startswith("0x")
        label = "l{}".format(hex_addr[2:])
        instrs = []
        self._add_instruction(instructions.LabeledBlock(label, instrs))
        self._current_block = BlockBuilder(instrs)

    def _try_pop_restore_instruction(self, reg):
        pc = self._current_block.try_pop_procedure_call("RESTORE", 1)
        if pc is None:
            return False
        if pc.arguments[0].emit_code() != reg:
            raise Exception(
                "Expected restore of {} but was: {}.".format(
                    reg, pc.arguments[0].emit_code()))
        return True

    def _pop_restore_instructions(self):
        proc_info = self._expect_first_procedure_info()
        if (
            proc_info.is_stack_pointer_trashed and
            not self._try_pop_restore_instruction("esp")
        ):
            raise Exception("Changed stack pointer was not restored.")
        for preserved_reg in proc_info.preserved_regs:
            if not self._try_pop_restore_instruction(preserved_reg):
                raise Exception("{} was not restored.", preserved_reg)

    @property
    def _last_instruction(self):
        return self._current_block.last_instruction

    def _add_instruction(self, instruction):
        self._current_block.add_instruction(instruction)

    def _expect_first_procedure_info(self):
        first_instruction = self._instructions[0]
        if not isinstance(first_instruction, instructions.ProcedureInfo):
            raise Exception(
                "Unexpected first instruction type {}".format(
                    type(first_instruction)))
        return first_instruction

    def build_procedure(self):
        return Procedure(
            self._expect_first_procedure_info(),
            self._proc_addr,
            self._proc_decl,
            self._instructions,
            None,
        )
