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
    r'(\s*:\s*public\s*(?P<parent>\w+(\s*<\s*\w+\s*>)?)'
    r'(?P<other_parents>(\s*,\s*public\s*\w+(\s*<\s*\w+\s*>)?)*))?')
template_regexp = re.compile(r'^template<class\s+(?P<class>\w+)>')
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
        # Parameter of template of the next class
        self._template_param = None

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
                    parent = parser.parse_data_type(
                        parent_name, self._declared_types)
                    class_type.set_parent(parent)
                    parent_size = parent.size
                    other_parents = match.group("other_parents")
                    if other_parents and not is_forward:
                        parent_size = self._add_other_parents_fields(
                            class_type, fields, _get_class_size(parent),
                            other_parents)
                if not is_forward:
                    class_type = self._declared_types[class_name]
                    class_type.template_param = self._template_param
                self._template_param = None
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

    def _add_other_parents_fields(
        self, class_type, fields, offset, other_parents
    ):
        """Add fields of other base classes of multiple inheritance."""
        for parent_name in other_parents.split(","):
            parent_name = _strip_start(parent_name.strip(), "public")
            parent_name = parent_name.strip()
            if not parent_name:
                continue
            parent = parser.parse_data_type(
                parent_name, self._declared_types)
            offset = (offset + 3) // 4 * 4
            class_type.add_other_parent(offset, parent)
            for field_offset, field in parent.get_all_fields().items():
                fields[offset + field_offset] = field
            offset += _get_class_size(parent)
        return offset

    def _parse_class_definition(
        self, class_name, definition, parent_size, fields
    ):
        offset = parent_size
        has_virtual_methods = False
        for field_definition in re.split(r'[{};]', definition):
            decl = self._parse_definition(class_name, field_definition)
            if decl is None:
                continue
            if isinstance(decl, _Constructor):
                self._declared_types[class_name].add_constructor(
                    decl.proc_decl, decl.default_values)
                continue
            if isinstance(decl, _OtherMethod):
                self._declared_types[class_name].add_other_method(
                    decl.proc_decl)
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
            constructor = self._try_parse_constructor(class_name, definition)
            if constructor is not None:
                return constructor
            return self._try_parse_other_method(class_name, definition)
        if is_static:
            return
        if definition.startswith("enum"):
            return
        if class_regexp.search(definition):
            return
        field_type, field_name = parser.parse_cpp_variable_declaration(
            definition, self._declared_types, self._constants)
        return field_type, field_name

    def _try_parse_other_method(self, class_name, definition):
        try:
            proc_decl = parser.parse_cpp_function(
                class_name, definition, self._declared_types)
        except Exception:
            return None
        return _OtherMethod(proc_decl)

    def _try_parse_constructor(self, class_name, definition):
        if not definition.startswith(class_name + "("):
            return None
        # Strip initialization list after the closing bracket of parameters
        depth = 0
        for end, c in enumerate(definition):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
        definition = definition[:end + 1]
        try:
            proc_decl = parser.parse_cpp_function(
                class_name, definition, self._declared_types)
        except Exception:
            return None
        return _Constructor(proc_decl, _get_default_values(definition))

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
        self._template_param = self._declared_types[arg_class]
        return re.sub(template_regexp, "", line).strip()

    def _try_parse_external_procedures(self, line):
        match = ext_proc_regexp.search(line)
        if not match:
            return
        alias = match.group("alias")
        declaration = match.group("decl")
        proc_decl = parser.parse_cpp_function(
            None, declaration, self._declared_types)
        self._external_procedures[alias] = proc_decl


class _OtherMethod:
    """Method which isn't virtual or static, e.g. inline method."""

    def __init__(self, proc_decl):
        self.proc_decl = proc_decl


class _Constructor:
    def __init__(self, proc_decl, default_values):
        self.proc_decl = proc_decl
        self.default_values = default_values


def _get_default_values(definition):
    """Return default values of parameters of procedure definition."""
    start = definition.find("(")
    parameters = definition[start + 1:definition.rfind(")")]
    if not parameters.strip():
        return []
    default_values = []
    for parameter in parameters.split(","):
        _, sep, value = parameter.partition("=")
        default_values.append(value.strip() if sep else None)
    return default_values


def _get_class_size(class_type):
    """Size of class including fields of parents and virtual table."""
    size = 4 if class_type.has_virtual_methods else 0
    for offset, (field_type, field_name) in (
        class_type.get_all_fields().items()
    ):
        size = max(size, offset + field_type.size)
    return size


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
        # The order of os.walk depends on the file system, later
        # declarations override earlier ones: the order of Windows
        dirs.sort(key=str.upper)
        for file in sorted(files, key=str.upper):
            if (
                file.lower().endswith(".cpp") or
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
