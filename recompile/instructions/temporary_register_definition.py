import data_types
import expressions


class TemporaryRegisterDefinition:
    def __init__(self):
        self._reg_values = {}
        self._fpu_stack = []

    def __repr__(self):
        return "REGDEF({})".format(
            ", ".join(
                "{}={}".format(name, repr(value))
                for (name, value) in self._values.items())
        )

    @property
    def _values(self):
        values = dict(self._reg_values)
        values.update(
            ("ST({})".format(i), value)
            for i, value in enumerate(reversed(self._fpu_stack))
        )
        return values

    def define_reg_value(self, reg, value):
        if reg in self._reg_values:
            raise Exception("Redeclaration of {}".format(reg))
        self._reg_values[reg] = value

    def pop_reg_value(self, reg):
        if reg == "fpu":
            return self.pop_fpu()
        value = self._try_pop_aliased_reg(reg)
        if value is not None:
            return value
        return self._reg_values.pop(reg)

    def push_fpu(self, value):
        self._fpu_stack.append(value)

    def pop_fpu(self):
        return self._fpu_stack.pop()

    def has_fpu_values(self):
        return bool(self._fpu_stack)

    def is_empty(self):
        return not self._reg_values and not self._fpu_stack

    def _try_pop_aliased_reg(self, reg):
        if reg in self._reg_values:
            return None
        reg32 = _32_bit_alias(reg)
        if reg32 is not None and reg32 in self._reg_values:
            return expressions.do_static_cast(
                data_types.AnyInt(_reg_size(reg)),
                expressions.do_reinterpret(
                    data_types.AnyInt(_reg_size(reg32)),
                    self._reg_values.pop(reg32)
                ),
            )
        return None

    def visit(self, on_expression_visited, **kwargs):
        on_expression_visited(self, **kwargs)
        for value in self._values.values():
            value.visit(on_expression_visited, **kwargs)

    def transform(self, transformer, **kwargs):
        regdef = TemporaryRegisterDefinition()
        for reg, value in self._reg_values.items():
            regdef.define_reg_value(
                reg, value.transform(transformer, **kwargs))
        for value in self._fpu_stack:
            regdef.push_fpu(value.transform(transformer, **kwargs))
        return regdef

    def emit_code(self, writer):
        code = "REGDEF({})".format(
            ", ".join(
                "{}={}".format(name, value.emit_code())
                for (name, value) in self._values.items())
        )
        writer.write_line(code)


def _32_bit_alias(reg):
    if reg.endswith("l"):
        return "e{}x".format(reg[:-1])
    if reg.endswith("x"):
        return "e{}".format(reg)
    return None


def _reg_size(reg):
    if reg.endswith("l"):
        return 1
    if len(reg) == 2 and reg.endswith("x"):
        return 2
    if reg.startswith("e") and reg.endswith("x"):
        return 4
    raise Exception("Can't define size for {}".format(reg))
