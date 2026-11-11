import re

import data_types
import parser
from procedure_declaration import ProcedureDeclaration

from .procedure_data import ProcedureData

id_regexp = re.compile(r'\w+')
stripping_ids_regexp = re.compile(r'(extern|LIB_EXP|CALLBACK|PASCAL|WINAPI)\s*')


def bind_headers(src_files, procedures_data):
    header_decls_data = _get_header_declarations(src_files)
    _bind_definitions_with_declarations(procedures_data, header_decls_data)


def _get_header_declarations(src_files):
    header_decls_data = {}
    for src_file in src_files:
        declarations = parser.collect_declarations_from_headers(src_file.lines)
        for header_decl in declarations:
            proc_id = _get_procedure_id(
                header_decl.declaration, header_decl.class_name)
            header_decls_data[proc_id] = _HeaderDeclarationData(
                src_file, header_decl)
    return header_decls_data


def _bind_definitions_with_declarations(procedures_data, header_decls_data):
    class_states = {}
    for procedure_data in procedures_data.values():
        if (
            procedure_data.src_definition is not None and
            procedure_data.src_definition.class_name is not None
        ):
            continue
        if procedure_data.file is None:
            continue
        # Virtual methods of stubs are declared in headers already
        if procedure_data.is_virtual_stub:
            continue
        class_name = procedure_data.get_class_name()
        if class_name not in class_states:
            class_states[class_name] = _ClassDeclarationState()
        class_state = class_states[class_name]
        header_decl_data = _get_header_decl_for_proc(
            procedure_data, header_decls_data)
        if header_decl_data is None:
            if class_state.prev_header_decl_data is not None:
                procedure_decl_data = ProcedureData(
                    class_state.prev_header_decl_data.file,
                    procedure_data.is_exported,
                    None, procedure_data.procedure, True)
                procedure_decl_data.prev_src_definition = \
                    class_state.prev_header_decl_data.header_decl
            else:
                class_state.first_undefined_decls.append(procedure_data)
        else:
            for undefined_proc in class_state.first_undefined_decls:
                procedure_decl_data = ProcedureData(
                    header_decl_data.file, undefined_proc.is_exported,
                    None, undefined_proc.procedure, True)
                procedure_decl_data.next_src_definition = \
                    header_decl_data.header_decl
                procedure_decl_data.is_declaration = True
            class_state.first_undefined_decls = []
            class_state.prev_header_decl_data = header_decl_data
            procedure_decl_data = ProcedureData(
                header_decl_data.file, procedure_data.is_exported,
                header_decl_data.header_decl, procedure_data.procedure, True)


def _get_header_decl_for_proc(procedure_data, header_decls_data):
    if procedure_data.src_definition is None:
        return None
    declaration = procedure_data.src_definition.declaration
    if declaration is None:
        return None
    proc_id = _get_procedure_id(declaration, None)
    return header_decls_data.get(proc_id)


def _get_procedure_id(declaration, class_name):
    for cpp_id in id_regexp.findall(declaration):
        _dummy_declared_types[cpp_id] = data_types.ClassType(cpp_id, {})
    if class_name is not None:
        _dummy_declared_types[class_name] = data_types.ClassType(class_name, {})
    declaration = stripping_ids_regexp.sub("", declaration)
    proc_decl = parser.parse_cpp_function(
        class_name, declaration, _dummy_declared_types)
    proc_decl = _make_reduced_proc_decl(proc_decl)
    return proc_decl.get_declaration(is_definition=True)


def _make_reduced_proc_decl(proc_decl):
    parameters = []
    param_ids = list(proc_decl.get_parameters_ids().values())
    if proc_decl.is_instance_method:
        param_ids = param_ids[1:]
    for param_id in param_ids:
        if param_id.data_type is None:
            continue
        parameters.append((param_id.data_type, None))
    return ProcedureDeclaration(
        proc_decl.proc_name, proc_decl.convention, proc_decl.method_class,
        parameters, None)


class _HeaderDeclarationData:
    def __init__(self, file, header_decl):
        self.file = file
        self.header_decl = header_decl


class _ClassDeclarationState:
    def __init__(self):
        self.prev_header_decl_data = None
        self.first_undefined_decls = []


_dummy_declared_types = {
    "unsigned char": data_types.ClassType("unsigned char", {}),
    "unsigned short": data_types.ClassType("unsigned short", {}),
    "unsigned int": data_types.ClassType("unsigned int", {}),
    "unsigned long": data_types.ClassType("unsigned long", {}),
}
