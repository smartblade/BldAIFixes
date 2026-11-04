from calling_convention import CallingConvention
import data_types
import expressions
import instructions
import patterns.high_level as high_level
from patterns.procedure import Procedure
from procedure_declaration import ProcedureDeclaration

from .bind_stack_variables import bind_stack_variables


class ProceduresDict:
    def __init__(self):
        self._classes = {}
        # Procedures already converted to high level code
        self._high_level_procedures = set()

    def add_destructor(self, destructor_class, this_offset, instrs):
        method_name = "~{}".format(destructor_class.class_name)
        self.add_method(destructor_class, this_offset, instrs, method_name, [])

    def add_method(
        self, method_class, this_offset, instrs, method_name, arguments
    ):
        proc_dict = self._classes.get(method_class.class_name)
        if proc_dict is None:
            proc_dict = {}
            self._classes[method_class.class_name] = proc_dict
        parameters = []
        for argument in arguments:
            data_type = data_types.UInt32()
            assert argument.size == data_type.size
            parameters.append((data_type, argument.name))
        proc_decl = ProcedureDeclaration(
            method_name, CallingConvention.THISCALL, method_class,
            parameters, None)
        instrs = bind_stack_variables(instrs, proc_decl, arguments)
        proc_info = _make_procedure_info(
            method_class, this_offset, proc_decl.stack_delta)
        assert method_name not in proc_dict
        proc_dict[method_name] = Procedure(
            proc_info, None, proc_decl, instrs, None)

    def add_high_level_procedure(self, method_class, procedure):
        proc_dict = self._classes.setdefault(method_class.class_name, {})
        method_name = procedure.proc_decl.proc_name
        assert method_name not in proc_dict
        proc_dict[method_name] = procedure
        self._high_level_procedures.add(id(procedure))

    def make_high_level_code(self, declarations):
        for class_methods in self._classes.values():
            for name, procedure in class_methods.items():
                if id(procedure) in self._high_level_procedures:
                    continue
                class_methods[name] = high_level.make_high_level_code(
                    procedure, declarations, None)

    def write_procedures(self, writer):
        for class_name, class_methods in self._classes.items():
            writer.write_line()
            writer.write_line("class {}".format(class_name))
            writer.write_line("{")
            with writer.indent():
                is_first = True
                for procedure in class_methods.values():
                    if not is_first:
                        writer.write_line()
                    is_first = False
                    procedure.emit_code(writer, is_definition=False)
            writer.write_line("};")


def _make_procedure_info(method_class, this_offset, stack_delta):
    proc_info = instructions.ProcedureInfo(method_class, None)
    proc_info.define_this_offset(
        expressions.intermediate.Stackvar(this_offset, 4))
    proc_info.set_stack_delta(stack_delta)
    proc_info.pop_reg_value("ecx")
    return proc_info
