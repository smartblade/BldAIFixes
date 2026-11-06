import unittest

from calling_convention import CallingConvention
import data_types
import expressions
from patterns.high_level.transform_procedure_call import (
    _merge_split_arguments, _resolve_virtual_call)
from patterns.make_proc_decl_from_args import make_proc_decl_from_args
from procedure_declaration import ProcedureDeclaration


def _method(class_type, name, parameters=(), is_virtual=True):
    return ProcedureDeclaration(
        name, CallingConvention.THISCALL, class_type, list(parameters), None,
        is_virtual=is_virtual)


def _classes():
    base = data_types.ClassType("B_Base", {})
    base.add_method(_method(base, "GetTypeID"))
    base.add_method(_method(base, "~B_Base"))
    base.add_method(_method(base, "Collect", [(data_types.Double(), "size")]))
    derived = data_types.ClassType("B_Derived", {})
    derived.set_parent(base)
    derived.add_method(_method(derived, "~B_Derived"))
    derived.add_method(_method(derived, "GetTypeID"))
    derived.add_method(_method(derived, "Extra"))
    return base, derived


def _virtual_call(class_type, offset, arguments):
    obj = expressions.Identifier(data_types.Pointer32(class_type), "obj")
    vtbl = expressions.intermediate.Access(obj, 0, 4)
    callee = expressions.intermediate.Access(vtbl, offset, 4)
    arguments = [obj] + arguments
    return expressions.ProcedureCall(
        callee=callee, is_method=True, arguments=arguments,
        proc_decl=make_proc_decl_from_args(arguments, is_method=True))


def _stackvar(offset):
    return expressions.intermediate.Stackvar(offset, 4)


class TestVirtualCalls(unittest.TestCase):
    def test_virtual_methods_order(self):
        base, derived = _classes()
        self.assertEqual(
            ["GetTypeID", "~B_Derived", "Collect", "Extra"],
            [method.proc_name for method in derived.virtual_methods])
        self.assertEqual(
            ["GetTypeID", "~B_Base", "Collect"],
            [method.proc_name for method in base.virtual_methods])

    def test_resolve_virtual_call(self):
        base, derived = _classes()
        pc, method = _resolve_virtual_call(
            _virtual_call(base, 8, [_stackvar(-8), _stackvar(-4)]))
        self.assertEqual("Collect", method.proc_name)
        self.assertIsNone(pc.callee_expression)

    def test_destructor_is_not_resolved(self):
        base, derived = _classes()
        pc, method = _resolve_virtual_call(
            _virtual_call(base, 4, [_stackvar(-4)]))
        self.assertIsNone(method)

    def test_merge_split_double_argument(self):
        base, derived = _classes()
        method = base.virtual_methods[2]
        obj = expressions.Identifier(data_types.Pointer32(base), "obj")
        arguments = _merge_split_arguments(
            [obj, _stackvar(-8), _stackvar(-4)], method)
        self.assertEqual(
            ["obj", "STACKVAR(-8, 8)"], [a.emit_code() for a in arguments])

    def test_merge_split_double_constant(self):
        base, derived = _classes()
        method = base.virtual_methods[2]
        obj = expressions.Identifier(data_types.Pointer32(base), "obj")
        # Halves of 0.5 pushed as 'push 0; push 3FE00000h'
        arguments = _merge_split_arguments([
            obj,
            expressions.Constant(data_types.Int32(), 0),
            expressions.Constant(data_types.Int32(), 0x3FE00000),
        ], method)
        self.assertEqual(
            ["obj", "0.5"], [a.emit_code() for a in arguments])
