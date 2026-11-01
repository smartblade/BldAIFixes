import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from expressions.operator import Operator
import instructions
from patterns.high_level.member_array_construction import \
    remove_member_array_construction
from procedure_declaration import ProcedureDeclaration
from tests.builder import i32_id


class _ProcInfo:
    def __init__(self, this):
        self._this = this

    def is_this_expression(self, e):
        return e is self._this


class _Procedure:
    def __init__(self, proc_info, proc_decl, instrs):
        self.proc_info = proc_info
        self.proc_decl = proc_decl
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(self.proc_info, self.proc_decl, instrs)


def _const(value):
    return expressions.Constant(data_types.Int32(), value)


class TestMemberArrayConstruction(unittest.TestCase):
    def test_construction_is_removed(self):
        item = data_types.ClassType("B_Item", {
            0: (data_types.Int32(), "a"),
            4: (data_types.Int32(), "b"),
        })
        cache = data_types.ClassType("B_Cache", {
            0: (data_types.Int32(), "count"),
            4: (data_types.Array(item, 16), "items"),
        })
        this = expressions.Identifier(data_types.Pointer32(cache), "this")
        cache_ctor = ProcedureDeclaration(
            "B_Cache", CallingConvention.THISCALL, cache, [], None)
        item_ctor = ProcedureDeclaration(
            "B_Item", CallingConvention.THISCALL, item, [], None)
        ptr = expressions.intermediate.Stackvar(-4, 4)
        size = expressions.intermediate.Stackvar(-8, 4)
        count = i32_id("n")
        init = instructions.Assignment(
            expressions.FieldAccess(this, "count"), _const(0))
        instrs = [
            init,
            instructions.Assignment(count, _const(16)),
            instructions.Assignment(size, _const(8)),
            instructions.Assignment(ptr, expressions.AddressOf(
                expressions.FieldAccess(this, "items"))),
            instructions.WhileInstruction(
                expressions.Bin(Operator.GE, count, _const(0)), [
                    instructions.CodeInstruction(expressions.ProcedureCall(
                        name="B_Item", arguments=[ptr], is_method=True,
                        proc_decl=item_ctor)),
                    instructions.Assignment(ptr, size),
                ]),
        ]
        procedure = remove_member_array_construction(
            _Procedure(_ProcInfo(this), cache_ctor, instrs))
        self.assertEqual([init], procedure.instructions)
