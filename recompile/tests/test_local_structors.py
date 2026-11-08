import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.inlined_clear import collapse_inlined_clears
from patterns.high_level.local_structors import \
    remove_inlined_local_structors
from procedure_declaration import ProcedureDeclaration
from writer import Writer


class _Procedure:
    def __init__(self, instrs):
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(instrs)


def _array():
    item = data_types.ClassType("Item", {0: (data_types.Int32(), "a")})
    array = data_types.ClassType("Array", {
        4: (data_types.Pointer32(data_types.Pointer32(item)), "elements"),
        8: (data_types.UInt32(), "size"),
        12: (data_types.Int32(), "increment"),
        16: (data_types.UInt32(), "num_alloc"),
        20: (data_types.Int32(), "deleteItems"),
    })
    array.add_method(ProcedureDeclaration(
        "~Array", CallingConvention.THISCALL, array, [], None,
        is_virtual=True))
    array.add_constructor(ProcedureDeclaration(
        "Array", CallingConvention.THISCALL, array,
        [(data_types.Int32(), "increment"),
         (data_types.Int32(), "deleteItems")], None), ["16", "true"])
    array.add_other_method(ProcedureDeclaration(
        "Clear", CallingConvention.THISCALL, array,
        [(data_types.Int32(), "deleteItems")], None))
    return array


def _const(value):
    return expressions.Constant(data_types.Int32(), value)


def _field(var, name):
    return expressions.FieldAccess(expressions.AddressOf(var), name)


def _vtable(offset):
    return instructions.Assignment(
        expressions.intermediate.Stackvar(offset, 4),
        expressions.intermediate.Global(0x005BDB7C))


def _freeing(var, temporary):
    delete = expressions.ProcedureCall(
        name="operator delete", arguments=[temporary])
    return [
        instructions.Assignment(temporary, _field(var, "elements")),
        instructions.CodeInstruction(delete),
        instructions.Assignment(_field(var, "elements"), expressions.Null),
        instructions.Assignment(_field(var, "size"), _const(0)),
        instructions.Assignment(_field(var, "num_alloc"), _const(0)),
    ]


def _goto_if(clause, label):
    return instructions.IfInstruction(clause, [instructions.Goto(label)])


def _num_alloc_is_zero(var):
    return expressions.Bin(Operator.EQ, _field(var, "num_alloc"), _const(0))


def _deleting_loop(var):
    i = expressions.Identifier(data_types.UInt32(), "i")
    clause = expressions.Bin(Operator.LT, i, _field(var, "size"))
    return instructions.ForInstruction(
        instructions.Assignment(i, _const(0)), clause,
        instructions.CodeInstruction(expressions.Increment(i)),
        [instructions.Delete(expressions.ArrayAccess(
            _field(var, "elements"), i))])


def _emit(instrs):
    writer = Writer()
    for instr in instrs:
        instr.emit_code(writer)
    return writer.get_string()


class TestLocalStructors(unittest.TestCase):
    def setUp(self):
        self.array = _array()
        self.var = expressions.Identifier(self.array, "a")
        self.stack_vars = {-60: self.var}
        self.temporary = expressions.Identifier(
            data_types.Pointer32(data_types.Int32()), "t")

    def _construction(self, increment):
        values = [
            ("elements", expressions.Null), ("size", _const(0)),
            ("increment", _const(increment)), ("num_alloc", _const(0)),
            ("deleteItems", _const(1)),
        ]
        return [
            instructions.Assignment(_field(self.var, name), value)
            for name, value in values
        ] + [_vtable(-60)]

    def test_construction_by_default_arguments(self):
        result = remove_inlined_local_structors(
            _Procedure(self._construction(16)), self.stack_vars)
        self.assertEqual(1, len(result.instructions))
        call = result.instructions[0].expression
        self.assertEqual("Array", call.name)
        self.assertEqual(1, len(call.arguments))

    def test_construction_by_other_arguments(self):
        instrs = self._construction(1)
        result = remove_inlined_local_structors(
            _Procedure(instrs), self.stack_vars)
        self.assertEqual(6, len(result.instructions))

    def test_clear(self):
        end = instructions.LabeledBlock("end", [
            instructions.ReturnInstruction(None)])
        skip = instructions.LabeledBlock(
            "skip", _freeing(self.var, self.temporary) + [end])
        instrs = [
            _goto_if(_num_alloc_is_zero(self.var), "end"),
            _goto_if(expressions.Bin(Operator.EQ, _const(0), _const(0)),
                     "skip"),
            _deleting_loop(self.var),
            skip,
        ]
        result = collapse_inlined_clears(_Procedure(instrs))
        self.assertEqual(
            "a.Clear(false);\nreturn;\n", _emit(result.instructions))

    def test_destruction(self):
        delete_items = expressions.Identifier(data_types.Int32(), "d")
        end = instructions.LabeledBlock("end", [
            instructions.ReturnInstruction(None)])
        skip = instructions.LabeledBlock(
            "skip", _freeing(self.var, self.temporary) + [end])
        instrs = [
            _vtable(-60),
            _goto_if(_num_alloc_is_zero(self.var), "end"),
            instructions.Assignment(
                delete_items, _field(self.var, "deleteItems")),
            _goto_if(_num_alloc_is_zero(self.var), "end"),
            _goto_if(expressions.Bin(Operator.EQ, delete_items, _const(0)),
                     "skip"),
            _deleting_loop(self.var),
            skip,
        ]
        result = remove_inlined_local_structors(
            _Procedure(instrs), self.stack_vars)
        self.assertEqual("return;\n", _emit(result.instructions))
