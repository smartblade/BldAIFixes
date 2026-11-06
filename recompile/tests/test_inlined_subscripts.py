import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.inlined_subscripts import restore_inlined_subscripts
from procedure_declaration import ProcedureDeclaration


def _stackvar(offset):
    return expressions.intermediate.Stackvar(offset, 4)


def _const(value):
    return expressions.Constant(data_types.Int32(), value)


class TestInlinedSubscripts(unittest.TestCase):
    def setUp(self):
        self.item = data_types.ClassType("Item", {0: (data_types.Int32(), "a")})
        self.array = data_types.ClassType("Array", {
            0: (data_types.Pointer32(data_types.Pointer32(self.item)),
                "elements"),
            4: (data_types.UInt32(), "size"),
        })
        self.array.add_other_method(ProcedureDeclaration(
            "operator []", CallingConvention.THISCALL, self.array,
            [(data_types.UInt32(), "index")],
            data_types.Pointer32(self.item)))
        self.append = ProcedureDeclaration(
            "Append", CallingConvention.THISCALL, self.array,
            [(data_types.Pointer32(self.item), "newElement")],
            data_types.Int32())
        self.map = expressions.Identifier(self.array, "map")
        self.elements = expressions.FieldAccess(
            expressions.AddressOf(self.map), "elements")

    def test_constant_index(self):
        element = expressions.intermediate.Access(
            expressions.intermediate.Arrptr(
                self.elements, 1,
                expressions.Bin(Operator.MUL, _const(4), _const(0)), 0),
            0, 4)
        use = instructions.Assignment(_stackvar(-8), _stackvar(-444))
        instrs = restore_inlined_subscripts([
            instructions.Assignment(_stackvar(-444), element), use])
        self.assertEqual(1, len(instrs))
        self.assertEqual("map[0]", instrs[0].src.emit_code())

    def _loop_instrs(self, element_offset):
        element = expressions.ArrayAccess(self.elements, _stackvar(-8))
        this = expressions.Bin(
            Operator.ADD,
            expressions.ReinterpretCast(data_types.AnyInt(4), _stackvar(-12)),
            _const(4))
        call = expressions.ProcedureCall(
            is_method=True, proc_decl=self.append,
            arguments=[_stackvar(-472), _stackvar(element_offset)])
        return [
            instructions.Assignment(_stackvar(element_offset), element),
            instructions.Assignment(_stackvar(-472), this),
            instructions.CodeInstruction(call),
        ]

    def test_argument_above_object_of_inlined_method(self):
        instrs = restore_inlined_subscripts(self._loop_instrs(-448))
        self.assertEqual(2, len(instrs))
        self.assertEqual(
            "map[STACKVAR(-8, 4)]",
            instrs[1].expression.arguments[1].emit_code())

    def test_argument_below_object_of_inlined_method(self):
        instrs = self._loop_instrs(-480)
        self.assertEqual(3, len(restore_inlined_subscripts(instrs)))
