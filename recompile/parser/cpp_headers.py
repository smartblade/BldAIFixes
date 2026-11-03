import os
import re

import data_types
from hex_conversion import from_hex
import parser
from patterns.characteristics import ExternalCharacteristics
from procedure_declaration import ProcedureDeclaration

from .constants import Constants
from .xml_metadata import XmlMetadata

preprocessor_regexp = re.compile(
    r'^#('
    r'(include\s+["<](?P<file>.+)[">])|'
    r'(define\s+(?P<const_name>\S+)\s+(?P<const_value>.+))|'
    r'(ifndef\s+(?P<ifndef_clause>BLD_NATIVE))|'
    r'(?P<endif>endif)'
    r')'
)
comment_regexp = re.compile(r'^(?P<line>.*)//')
comment_start_regexp = re.compile(r'^(?P<line>.*)/\*(?P<tail>.*)$')
comment_end_regexp = re.compile(r'\*/(?P<line>.*)$')
class_regexp = re.compile(
    r'^(class|struct)\s+(LIB_EXP\s+)?(?P<class>\w+)(?P<semicolon>;)?'
    r'(\s*:\s*public\s*(?P<parent>\w+))?')
template_regexp = re.compile(r'^template<class\s+(?P<class>\w+)>')
typedef_regexp = re.compile(r'^\s*typedef\s+(?P<definition>[^;{}]+);\s*$')
ext_proc_regexp = re.compile(
    r'^_CRT_NONSTDC_DEPRECATE\((?P<alias>\w+)\)(?P<decl>.+);')

_standard_types = {
    "bool": data_types.ClassType("bool", {}),
    "char": data_types.Char(),
    "unsigned char": data_types.UChar(),
    "byte": data_types.make_named_type(data_types.UChar(), "byte"),
    "short": data_types.Short(),
    "unsigned short": data_types.UShort(),
    "int": data_types.Int32(),
    "long": data_types.Long32(),
    "unsigned int": data_types.UInt32(),
    "unsigned long": data_types.make_named_type(
        data_types.UInt32(), "unsigned long"),
    "size_t": data_types.SizeT(),
    "float": data_types.Float(),
    "double": data_types.Double(),
    "BitMapType": data_types.make_named_type(data_types.Int32(), "BitMapType"),
    "B_CharData": data_types.ClassType("B_CharData", {}),
    "B_CharSize": data_types.ClassType("B_CharSize", {}),
    "bld_server_info": data_types.ClassType("bld_server_info", {}),
    "EventFn": data_types.Pointer32(),
}


class HeaderState:
    def __init__(
        self, file_name, header_states, declared_types, incomplete_types,
        external_procedures,
    ):
        self._file_name = file_name
        self._header_states = header_states
        self._declared_types = declared_types
        self._incomplete_types = incomplete_types
        self._external_procedures = external_procedures
        self._constants = Constants()
        self._visited = False

    @property
    def constants(self):
        return self._constants

    def update_declarations(self, header_state):
        if isinstance(header_state, XmlMetadata):
            return
        assert isinstance(header_state, HeaderState)
        self._constants.update(header_state._constants)

    def parse(self):
        if self._visited:
            return
        self._visited = True
        with open(self._file_name) as f:
            lines = f.readlines()
        is_comment = False
        is_native_placeholders = False
        class_name = None
        parent_size = 0
        fields = None
        definition_chars = []
        brackets_depth = 0
        for line in lines:
            line, is_comment = _strip_comments(line, is_comment)
            new_native_status = self._try_parse_preprocessor_directive(line)
            if new_native_status is not None:
                is_native_placeholders = new_native_status
                continue
            if is_native_placeholders:
                continue
            line = self._try_parse_template(line)
            self._try_parse_external_procedures(line)
            if brackets_depth == 0 and self._try_parse_typedef(line):
                continue
            match = class_regexp.search(line)
            if match and brackets_depth == 0:
                class_name = match.group("class")
                parent_name = match.group("parent")
                is_forward = bool(match.group("semicolon"))
                if class_name in self._incomplete_types:
                    fields = self._incomplete_types[class_name]
                    if fields and not is_forward:
                        raise Exception(
                            "Redeclared type: {}".format(class_name))
                else:
                    fields = {}
                    self._incomplete_types[class_name] = fields
                    self._declared_types[class_name] = data_types.ClassType(
                        class_name, fields)
                parent_size = 0
                if parent_name is not None:
                    class_type = self._declared_types[class_name]
                    parent = self._declared_types[parent_name]
                    class_type.set_parent(parent)
                    parent_size = parent.size
                if is_forward:
                    fields = None
                definition_chars = []
            for c in line:
                if c == "{":
                    brackets_depth += 1
                elif c == "}":
                    brackets_depth -= 1
                    if brackets_depth == 0 and fields is not None:
                        definition = "".join(definition_chars)
                        self._parse_class_definition(
                            class_name, definition, parent_size, fields)
                        fields = None
                if fields is not None and brackets_depth == 1:
                    definition_chars.append(c)

    def _parse_class_definition(
        self, class_name, definition, parent_size, fields
    ):
        offset = parent_size
        has_virtual_methods = False
        for field_definition in re.split(r'[{};]', definition):
            decl = self._parse_definition(class_name, field_definition)
            if decl is None:
                continue
            if isinstance(decl, ProcedureDeclaration):
                # Add space for vtable if necessary
                if (
                    offset == 0 and
                    not has_virtual_methods
                    and decl.is_virtual
                ):
                    offset += 4
                    has_virtual_methods = True
                self._declared_types[class_name].add_method(decl)
                continue
            field_type, field_name = decl
            fields[offset] = field_type, field_name
            offset += field_type.size

    def _parse_definition(self, class_name, definition):
        definition = _strip_start(definition.strip(), "public:")
        definition = _strip_start(definition.strip(), "protected:")
        definition = _strip_start(definition.strip(), "private:")
        definition = definition.strip()
        if not definition:
            return
        is_static = definition.startswith("static")
        is_virtual = definition.startswith("virtual")
        if definition.find("(") >= 0:
            if is_static or is_virtual:
                return parser.parse_cpp_function(
                    class_name, definition, self._declared_types)
            return
        if is_static:
            return
        if definition.startswith("enum"):
            return
        if class_regexp.search(definition):
            return
        field_type, field_name = parser.parse_cpp_variable_declaration(
            definition, self._declared_types, self._constants)
        return field_type, field_name

    def _try_parse_preprocessor_directive(self, line):
        match = preprocessor_regexp.search(line)
        if not match:
            return
        include_file = match.group("file")
        if include_file is not None:
            self._parse_include_file(include_file)
            return
        if match.group("ifndef_clause"):
            is_native_placeholders = True
            return is_native_placeholders
        if match.group("endif"):
            is_native_placeholders = False
            return is_native_placeholders
        const_name = match.group("const_name")
        const_value = match.group("const_value")
        self._parse_define(const_name, const_value)

    def _parse_define(self, const_name, const_value):
        const_value = const_value.strip()
        if const_value.startswith("0x"):
            # Ignore 'long' or ''long long' constants
            if const_value.endswith("L"):
                return
            self._constants.add(const_name, from_hex(const_value))
        elif const_value.isdigit():
            self._constants.add(const_name, int(const_value))

    def _parse_include_file(self, include_file):
        included_header_state = self._header_states.get(include_file)
        if included_header_state is not None:
            included_header_state.parse()
            self.update_declarations(included_header_state)

    def _try_parse_template(self, line):
        match = template_regexp.search(line)
        if not match:
            return line
        arg_class = match.group("class")
        self._declared_types[arg_class] = data_types.ClassType(arg_class, {})
        return re.sub(template_regexp, "", line).strip()

    def _try_parse_typedef(self, line):
        """Parse single line type definitions: 'typedef unsigned int T;'."""
        match = typedef_regexp.search(line)
        if not match:
            return False
        definition = match.group("definition").strip()
        try:
            data_type, name = parser.parse_cpp_variable_declaration(
                definition, self._declared_types, self._constants)
        except Exception:
            # Types which can't be parsed, e.g. pointers to functions
            return True
        self._declared_types[name] = data_types.make_named_type(
            data_type, name)
        return True

    def _try_parse_external_procedures(self, line):
        match = ext_proc_regexp.search(line)
        if not match:
            return
        alias = match.group("alias")
        declaration = match.group("decl")
        proc_decl = parser.parse_cpp_function(
            None, declaration, self._declared_types)
        self._external_procedures[alias] = proc_decl


def _strip_start(definition, start):
    if definition.startswith(start):
        definition = definition[len(start):]
    return definition


def _strip_comments(line, is_comment):
    match = comment_regexp.search(line)
    if match:
        line = match.group("line")
    match = comment_start_regexp.search(line)
    if match:
        line = match.group("line")
        is_comment = True
        tail, is_comment = _strip_comments(match.group("tail"), is_comment)
        return line + tail, is_comment
    if is_comment:
        match = comment_end_regexp.search(line)
        if match:
            line = match.group("line")
            is_comment = False
        else:
            line = ""
    return line, is_comment


def _collect_cpp_declarations(
    src_path, header_states, files_declarations, declared_types,
    incomplete_types, external_procedures
):
    for (root, dirs, files) in os.walk(src_path):
        for file in files:
            if (
                file.lower().endswith(".cpp") or
                file.lower().endswith(".c") or
                file.lower().endswith(".h") or
                file.lower().endswith(".xml")
            ):
                file_name = os.path.join(root, file)
                head, dir_name1 = os.path.split(root)
                head, dir_name2 = os.path.split(head)
                declarations = [
                    declared_types, incomplete_types, external_procedures]
                if file.lower().endswith(".xml"):
                    metadata_state_class = XmlMetadata
                else:
                    metadata_state_class = HeaderState
                header_state = metadata_state_class(
                    file_name, header_states, *declarations)
                header_states[file] = header_state
                header_states["{}/{}".format(dir_name1, file)] = header_state
                header_states[
                    "{}/{}/{}".format(
                        dir_name2, dir_name1, file)] = header_state
                if not file_name.lower().endswith(".xml"):
                    files_declarations[file_name] = header_state


def parse_cpp_header(src_path):
    header_states = {}
    files_declarations = {}
    declared_types = _standard_types
    incomplete_types = {}
    external_procedures = {}
    extern_definitions_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "externdefs")
    _collect_cpp_declarations(
        extern_definitions_path, header_states, files_declarations,
        declared_types, incomplete_types, external_procedures)
    _collect_cpp_declarations(
        src_path, header_states, files_declarations, declared_types,
        incomplete_types, external_procedures)
    for file_declaration in files_declarations.values():
        file_declaration.parse()
    characteristics_file = os.path.join(
        extern_definitions_path, "characteristics.json")
    characteristics = ExternalCharacteristics.read(characteristics_file)
    return (
        files_declarations, declared_types, external_procedures, characteristics
    )
