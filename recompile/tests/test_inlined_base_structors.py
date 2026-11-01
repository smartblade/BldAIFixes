import unittest

import data_types
import expressions
import instructions
from patterns.high_level.inlined_base_structors import \
    remove_inlined_base_structors
from tests.builder import i32_id


class _ProcInfo:
    def __init__(self, this):
        self._this = this

    def is_this_expression(self, e):
        return e is self._this


class _ProcDecl:
    def __init__(self, method_class, is_constructor):
        self.method_class = method_class
        self.is_constructor = is_constructor
        self.is_destructor = not is_constructor


class _Procedure:
    def __init__(self, proc_info, proc_decl, instrs):
        self.proc_info = proc_info
        self.proc_decl = proc_decl
        self.instructions = instrs

    def copy(self, instrs):
        return _Procedure(self.proc_info, self.proc_decl, instrs)


class _Method:
    is_virtual = True
    is_destructor = False
    proc_name = "GetTypeID"


def _make(is_constructor, instrs_cb):
    base = data_types.ClassType("B_Base", {})
    base.add_method(_Method())
    node = data_types.ClassType("B_Node", {
        4: (data_types.Pointer32(data_types.Int32()), "items"),
    })
    node.set_parent(base)
    node.add_method(_Method())
    this = expressions.Identifier(data_types.Pointer32(node), "this")
    procedure = _Procedure(
        _ProcInfo(this), _ProcDecl(node, is_constructor), instrs_cb(this))
    return remove_inlined_base_structors(procedure).instructions


def _vtbl(this, address):
    return instructions.Assignment(
        expressions.intermediate.Access(this, 0, 4),
        expressions.intermediate.Global(address))


def _count(delta):
    return instructions.CodeInstruction(i32_id("count{}".format(delta)))


def _init_items(this):
    return instructions.Assignment(
        expressions.FieldAccess(this, "items"),
        expressions.Constant(data_types.Int32(), 0))


class TestInlinedBaseStructors(unittest.TestCase):
    def test_constructor(self):
        instrs = _make(True, lambda this: [
            _vtbl(this, 0x100), _count("++"), _init_items(this),
            _vtbl(this, 0x200), _count("body"),
        ])
        self.assertEqual(
            ["this->items = 0", "countbody"],
            [i.expression.emit_code() if hasattr(i, "expression")
             else "{} = {}".format(i.dst.emit_code(), i.src.emit_code())
             for i in instrs])

    def test_destructor(self):
        instrs = _make(False, lambda this: [
            _vtbl(this, 0x200), _count("body"),
            _vtbl(this, 0x100), _count("--"),
        ])
        self.assertEqual(2, len(instrs))
        self.assertEqual("countbody", instrs[1].expression.emit_code())
