import os
import re

from hex_conversion import to_hex
import parser

from .procedure_data import ProcedureData
from .update_headers import bind_headers
from .update_inlines import define_nearest_inline_definitions
from .writer import get_code


def update_src(
    src_path, module_name, procedures, exported_procedures,
    virtual_stubs=()
):
    """Update procedures in sources, add stubs of exported procedures and
    of virtual methods (virtual_stubs) missing in sources."""
    proc_by_addr = {}
    for procedure in procedures:
        proc_by_addr[procedure.address] = procedure
    src_files = _get_source_files(src_path)
    procedures_data = _get_procedures_data(
        src_files, module_name, exported_procedures, proc_by_addr)
    _define_files_from_adjacent_procedures(procedures_data)
    _define_nearest_src_definitions_for_files(src_files)
    _add_virtual_stubs(
        src_files, module_name, exported_procedures, procedures_data,
        virtual_stubs)
    bind_headers(src_files, procedures_data)
    define_nearest_inline_definitions(src_files, procedures_data)
    updating_procedures = _get_updating_procedures(procedures_data)
    for src_file in src_files:
        _process_file(
            src_file, module_name, updating_procedures, exported_procedures)


def _get_source_files(src_path):
    src_files = []
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.lower().endswith(".h") or file.lower().endswith(".cpp"):
                src_file_name = os.path.join(root, file)
                with open(src_file_name) as f:
                    lines = f.readlines()
                src_files.append(_FileData(src_file_name, lines))
    return src_files


def _get_procedures_data(
    src_files, module_name, exported_procedures, proc_by_addr
):
    procedures_data = {}
    for src_file in src_files:
        definitions = parser.SrcSymbols.collect_procedures(src_file.lines)
        for (cur_module, addr), definition in definitions.items():
            if cur_module != module_name:
                continue
            if addr not in proc_by_addr:
                continue
            is_exported = addr in exported_procedures
            procedures_data[addr] = ProcedureData(
                src_file, is_exported, definition, proc_by_addr[addr], False)
    for addr in proc_by_addr.keys():
        if addr in procedures_data:
            continue
        is_exported = addr in exported_procedures
        procedures_data[addr] = ProcedureData(
            None, is_exported, None, proc_by_addr[addr], False)
    sorted_addresses = sorted(procedures_data.keys())
    return dict(
        (addr, procedures_data[addr]) for addr in sorted_addresses
    )


def _define_files_from_adjacent_procedures(procedures_data):
    unset_file_addresses = []
    cur_file = None
    for addr, procedure_data in procedures_data.items():
        if addr % 16 == 0:
            unset_file_addresses = []
            cur_file = None
        if procedure_data.file is None:
            if cur_file is not None:
                procedure_data.file = cur_file
            else:
                unset_file_addresses.append(addr)
        else:
            cur_file = procedure_data.file
            for cur_file_addr in unset_file_addresses:
                if procedures_data[cur_file_addr].file is None:
                    procedures_data[cur_file_addr].file = cur_file
            unset_file_addresses = []


def _add_virtual_stubs(
    src_files, module_name, exported_procedures, procedures_data,
    virtual_stubs
):
    """Stubs of virtual methods are placed in the source file of the
    constructor of their class between the definitions of the nearest
    addresses."""
    definitions_by_file = {}
    constructor_files = {}
    for src_file in src_files:
        definitions = {}
        for (cur_module, addr), definition in (
            parser.SrcSymbols.collect_procedures(src_file.lines).items()
        ):
            if cur_module != module_name:
                continue
            definitions[addr] = definition
            class_name = _constructor_class_name(definition.declaration)
            if class_name is not None:
                constructor_files.setdefault(class_name, src_file)
        definitions_by_file[id(src_file)] = definitions
    for procedure in virtual_stubs:
        if procedure.address in procedures_data:
            continue
        src_file = constructor_files.get(
            procedure.proc_decl.method_class.class_name)
        if src_file is None:
            continue
        definitions = definitions_by_file[id(src_file)]
        prev_addrs = [a for a in definitions if a < procedure.address]
        next_addrs = [a for a in definitions if a > procedure.address]
        procedure_data = ProcedureData(
            src_file, procedure.address in exported_procedures, None,
            procedure, False)
        procedure_data.is_virtual_stub = True
        if prev_addrs:
            procedure_data.prev_src_definition = definitions[max(prev_addrs)]
        else:
            procedure_data.next_src_definition = definitions[min(next_addrs)]
        procedures_data[procedure.address] = procedure_data


def _constructor_class_name(declaration):
    """Class of a constructor 'C::C(...)' defined outside of its class."""
    if declaration is None:
        return None
    match = re.search(r"\b(\w+)::(\w+)\s*\(", declaration)
    if match is None or match.group(1) != match.group(2):
        return None
    return match.group(1)


def _get_updating_procedures(procedures_data):
    updating_procedures = {}
    for addr, procedure_data in procedures_data.items():
        if addr in _excluded_addresses:
            continue
        src_definition = procedure_data.src_definition
        if src_definition is not None:
            if not src_definition.is_implemented:
                continue
            if src_definition.declaration is None:
                continue
        else:
            if (
                not procedure_data.is_exported and
                not procedure_data.is_virtual_stub
            ):
                continue
            if procedure_data.file is None:
                continue
        updating_procedures[addr] = procedure_data
    return updating_procedures


def _define_nearest_src_definitions_for_files(src_files):
    for src_file in src_files:
        procedures = sorted(
            src_file.procedures,
            key=lambda p: p.procedure.address,
        )
        _define_nearest_src_definitions(procedures)


def _define_nearest_src_definitions(procedures_data):
    prev_src_definition = None
    prev_addr = None
    first_undefined_procs = []
    for proc_data in procedures_data:
        if proc_data.src_definition is None:
            if prev_src_definition is not None:
                proc_data.prev_src_definition = prev_src_definition
            else:
                first_undefined_procs.append(proc_data)
            continue
        for undefined_proc in first_undefined_procs:
            undefined_proc.next_src_definition = proc_data.src_definition
        first_undefined_procs = []
        if prev_src_definition is not None:
            if (
                proc_data.src_definition.definition_start_line <=
                prev_src_definition.definition_start_line
            ):
                raise Exception(
                    "Procedure 0x{} should be before 0x{}".format(
                        to_hex(prev_addr), to_hex(proc_data.procedure.address))
                )
        prev_src_definition = proc_data.src_definition
        prev_addr = proc_data.procedure.address


def _process_file(
    src_file, module_name, updating_procedures, exported_procedures
):
    procedures = [
        proc_data for proc_data in src_file.procedures
        if proc_data.procedure.address in updating_procedures
    ]
    if len(procedures) == 0:
        return
    procedures = sorted(
        procedures,
        key=lambda p: p.end_line,
    )
    cur_proc_data = procedures.pop()
    lines = list(src_file.lines)
    while len(lines) <= cur_proc_data.start_line:
        lines.append("")
    new_lines = []
    for line_index, line in reversed(list(enumerate(lines))):
        if (
            cur_proc_data is None or
            line_index > cur_proc_data.end_line
        ):
            new_lines.append(line)
        while (
            cur_proc_data is not None and line_index == cur_proc_data.start_line
        ):
            procedure_code = get_code(
                cur_proc_data, module_name, exported_procedures, line_index,
                lines)
            new_lines.append(procedure_code)
            if len(procedures) > 0:
                cur_proc_data = procedures.pop()
            else:
                cur_proc_data = None
    assert cur_proc_data is None
    new_lines = list(reversed(new_lines))
    _strip_last_empty_lines(new_lines)
    with open(src_file.file_name, "wt") as f:
        for line in new_lines:
            f.write(line)


def _strip_last_empty_lines(lines):
    while len(lines[-1].strip()) == 0:
        lines.pop()


class _FileData:
    def __init__(self, file_name, lines):
        self.file_name = file_name
        self.lines = lines
        self._procedures = []

    @property
    def procedures(self):
        return self._procedures

    def add_procedure(self, proc):
        self._procedures.append(proc)


_excluded_addresses = {
    0x100022D0, 0x10002550, 0x10002580, 0x100025C0, 0x100030E0, 0x10003300,
    0x10003337, 0x100033A4, 0x10003410, 0x100039BA,
    0x100066E0, 0x10006720, 0x10029BE0,
    0x1002A590,
}
