from custom_block_transformer import transform_block
from block_visitor import visit_block


class WhileInstruction:
    def __init__(self, clause, block):
        self._clause = clause
        self._block = block

    def __repr__(self):
        return "WhileInstruction({})".format(self._block)

    @property
    def clause(self):
        return self._clause

    @property
    def block(self):
        return self._block

    def visit(self, on_expression_visited, **kwargs):
        self._clause.visit(on_expression_visited, **kwargs)
        visit_block(self._block, on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        clause = self._clause.transform(transformer, **kwargs)
        block = transform_block(self._block, transformer, **kwargs)
        instr = transformer.transform_while(clause, block, **kwargs)
        if instr is not None:
            return instr
        return self.__class__(clause, block)

    def emit_code(self, writer):
        clause = self._clause.emit_code()
        writer.write_line("while ({})".format(clause))
        writer.write_line("{")
        with writer.indent():
            for instr in self._block:
                instr.emit_code(writer)
        writer.write_line("}")
