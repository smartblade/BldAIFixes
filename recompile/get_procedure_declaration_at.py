import parser


def _has_src_declaration(declarations, addr):
    cpp_declaration = declarations.symbols.procedures.get(addr)
    return (
        cpp_declaration is not None and
        cpp_declaration.declaration is not None
    )


def get_procedure_declaration_at(declarations, addr):
    if _has_src_declaration(declarations, addr):
        cpp_declaration = declarations.symbols.procedures[addr]
        return parser.parse_cpp_function(
            cpp_declaration.class_name,
            cpp_declaration.declaration,
            declarations.declared_types,
        )
    exported_proc = declarations.exported_procedures.get(addr)
    if exported_proc is not None:
        return parser.demangle_cpp(
            exported_proc, declarations.declared_types)
    return None


def get_procedures_declarations(declarations, addresses):
    # Demangle exported names before parsing declarations from sources:
    # demangling adds undeclared types to declared types
    procedures_declarations = {}
    for addr in sorted(
        addresses, key=lambda addr: _has_src_declaration(declarations, addr)
    ):
        procedures_declarations[addr] = get_procedure_declaration_at(
            declarations, addr)
    return procedures_declarations
