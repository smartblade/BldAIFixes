class ProcedureData:
    def __init__(
        self, file, is_exported, src_definition, procedure, is_declaration
    ):
        self._file = None
        self.file = file
        self.is_exported = is_exported
        self.src_definition = src_definition
        self.is_declaration = is_declaration
        self.is_inline = False
        # Stub of a virtual method missing in sources
        self.is_virtual_stub = False
        self.procedure = procedure
        self.prev_src_definition = None
        self.next_src_definition = None

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        assert self._file is None
        if file is None:
            return
        self._file = file
        file.add_procedure(self)

    @property
    def start_line(self):
        if self.src_definition is not None:
            if self.is_declaration:
                return self.src_definition.start_line
            return self.src_definition.definition_start_line
        return self.end_line + 1

    @property
    def end_line(self):
        if self.src_definition is not None:
            if self.is_declaration:
                return self.src_definition.end_line
            return self.src_definition.definition_end_line
        if self.prev_src_definition is not None:
            if self.is_declaration:
                return self.prev_src_definition.end_line
            if hasattr(self.prev_src_definition, "end_line"):
                return self.prev_src_definition.end_line
            if self.prev_src_definition.definition_end_line is None:
                return self.prev_src_definition.definition_start_line
            return self.prev_src_definition.definition_end_line + 1
        assert self.next_src_definition is not None
        if self.is_declaration:
            return self.next_src_definition.start_line - 1
        return self.next_src_definition.metadata_start_line - 2

    def get_class_name(self):
        proc_decl = self.procedure.proc_decl
        if proc_decl is None:
            return None
        if proc_decl.method_class is None:
            return None
        return proc_decl.method_class.class_name
