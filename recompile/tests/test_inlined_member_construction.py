import unittest

from calling_convention import CallingConvention
import data_types
import expressions
import instructions
from patterns.high_level.inlined_member_construction import \
    remove_inlined_member_construction
from procedure_declaration import ProcedureDeclaration


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
    return expressions.Constant(data_types.Double(), value)


class TestInlinedMemberConstruction(unittest.TestCase):
    def setUp(self):
        self.vector = data_types.ClassType("B_Vector", {
            0: (data_types.Double(), "x"),
            8: (data_types.Double(), "y"),
            16: (data_types.Double(), "z"),
        })
        sphere = data_types.ClassType("B_Sphere", {
            0: (self.vector, "center"),
            24: (data_types.Double(), "radius"),
        })
        self.this = expressions.Identifier(
            data_types.Pointer32(sphere), "this")
        self.sphere_ctor = ProcedureDeclaration(
            "B_Sphere", CallingConvention.THISCALL, sphere, [], None)
        self.radius = instructions.Assignment(
            expressions.FieldAccess(self.this, "radius"), _const(0.0))

    def _center(self, name):
        center = expressions.AddressOf(
            expressions.FieldAccess(self.this, "center"))
        return instructions.Assignment(
            expressions.FieldAccess(center, name), _const(0.0))

    def _remove(self, instrs):
        return remove_inlined_member_construction(_Procedure(
            _ProcInfo(self.this), self.sphere_ctor, instrs)).instructions

    def test_default_construction_is_removed(self):
        self.vector.add_constructor(ProcedureDeclaration(
            "B_Vector", CallingConvention.THISCALL, self.vector, [], None))
        instrs = [self._center(n) for n in ("x", "y", "z")] + [self.radius]
        self.assertEqual([self.radius], self._remove(instrs))

    def test_class_without_default_constructor(self):
        instrs = [self._center(n) for n in ("x", "y", "z")] + [self.radius]
        self.assertEqual(instrs, self._remove(instrs))

    def test_not_all_fields_are_assigned(self):
        self.vector.add_constructor(ProcedureDeclaration(
            "B_Vector", CallingConvention.THISCALL, self.vector, [], None))
        instrs = [self._center(n) for n in ("x", "y")] + [self.radius]
        self.assertEqual(instrs, self._remove(instrs))


class TestInlinedMemberConstructionByPointer(unittest.TestCase):
    """Field constructed by pointer: p = &this->center; p->x = 0.0; ..."""

    def setUp(self):
        self.vector = data_types.ClassType("B_Vector", {
            0: (data_types.Double(), "x"),
            8: (data_types.Double(), "y"),
            16: (data_types.Double(), "z"),
        })
        self.vector.add_constructor(ProcedureDeclaration(
            "B_Vector", CallingConvention.THISCALL, self.vector, [], None))
        tree = data_types.ClassType("B_OctTree", {
            4: (self.vector, "center"),
            28: (data_types.Double(), "halfSize"),
        })
        self.this = expressions.Identifier(
            data_types.Pointer32(tree), "this")
        self.pointer = expressions.Identifier(
            data_types.Pointer32(self.vector), "unknown_loc_04")
        self.tree_ctor = ProcedureDeclaration(
            "B_OctTree", CallingConvention.THISCALL, tree, [], None)
        self.half_size = instructions.Assignment(
            expressions.FieldAccess(self.this, "halfSize"), _const(0.0))

    def _construction(self, names=("x", "y", "z")):
        instrs = [instructions.Assignment(
            self.pointer,
            expressions.AddressOf(
                expressions.FieldAccess(self.this, "center")))]
        for name in names:
            instrs.append(instructions.Assignment(
                expressions.FieldAccess(self.pointer, name), _const(0.0)))
        return instrs

    def _remove(self, instrs):
        return remove_inlined_member_construction(_Procedure(
            _ProcInfo(self.this), self.tree_ctor, instrs)).instructions

    def test_default_construction_is_removed(self):
        instrs = self._construction() + [self.half_size]
        self.assertEqual([self.half_size], self._remove(instrs))

    def test_not_all_fields_are_assigned(self):
        instrs = self._construction(("x", "y")) + [self.half_size]
        self.assertEqual(instrs, self._remove(instrs))

    def test_pointer_is_used_after_construction(self):
        use = instructions.Assignment(
            expressions.FieldAccess(self.this, "halfSize"),
            expressions.FieldAccess(self.pointer, "x"))
        instrs = self._construction() + [use]
        self.assertEqual(instrs, self._remove(instrs))
