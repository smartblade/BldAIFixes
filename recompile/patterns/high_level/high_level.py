from custom_block_transformer import transform_block
from expression_transformer import ExpressionTransformer
from patterns.high_level.analysis import Analysis
import patterns.high_level.goto_eliminator as goto_eliminator
import patterns.high_level.inline_functions as inline_functions
from patterns.validate_procedure_declaration import \
    validate_procedure_declaration

from .apply_parameters_names import apply_parameters_names
from .call_arguments_matcher import CallArgumentsMatcher
from .fields_destroying import discover_fields_destroying
from .fields_initialization import discover_fields_initialization
from .inlined_base_structors import remove_inlined_base_structors
from .member_array_construction import remove_member_array_construction
from .transform_class_returns import transform_class_returns
from .transform_access import transform_access
from .transform_arrptr import transform_arrptr
from .transform_assignment import transform_assignment
from .transform_binary import transform_binary
from .transform_block_instructions import transform_block_instructions
from .transform_constant import transform_constant
from .transform_dereference import transform_dereference
from .transform_global import transform_global
from .transform_if import transform_if
from .transform_local import transform_local
from .transform_make_reference import transform_make_reference
from .transform_stackvar import transform_stackvar
from .transform_switch import transform_switch
from .transform_procedure_call import transform_procedure_call
from .transform_reinterpret import transform_reinterpret
from .merge_split_copies import merge_split_copies
from .split_jumped_declarations import split_jumped_declarations
from .transform_for_loops import transform_for_loops
from .transform_returns import transform_returns
from .transform_struct_copy import transform_struct_copy
from .variables_declarations import insert_declarations


def make_high_level_code(procedure, declarations, inline_procedures):
    if procedure.address is not None:
        file_declarations = declarations.symbols.get_file_declarations(
            procedure.address, declarations.files_declarations)
    else:
        file_declarations = None
    characteristics = declarations.characteristics[procedure.address]
    procedure = apply_parameters_names(procedure, characteristics)
    proc_info = procedure.proc_info
    proc_decl = procedure.proc_decl
    stack_vars = procedure.implicit_stack_variables
    instrs = goto_eliminator.transform(procedure.instructions, stack_vars)
    analysis = Analysis()
    context = dict(
        analysis=analysis,
        procedure=procedure,
        stack_vars=stack_vars,
        file_declarations=file_declarations,
        declarations=declarations,
        characteristics=characteristics,
        inline_procedures=inline_procedures,
    )
    instrs = _transform_instructions(instrs, **context)
    _validate_procedure_info(proc_info, proc_decl)
    if proc_decl is not None:
        instrs = _eliminate_procedure_info(proc_info, instrs)
    instrs = transform_returns(proc_info, proc_decl, characteristics, instrs)
    instrs = _transform_instructions(instrs, **context)
    instrs = merge_split_copies(instrs)
    analysis.collect_stack_accesses(instrs)
    analysis.fill_stack_variables(
        stack_vars, characteristics.variables_names)
    instrs = _transform_instructions(instrs, **context)
    instrs = _transform_instructions(instrs, **context)
    # Types of stack variables become known after transformations above
    analysis.collect_stack_accesses(instrs)
    if analysis.fill_stack_variables(
        stack_vars, characteristics.variables_names
    ):
        instrs = _transform_instructions(instrs, **context)
    instrs = transform_for_loops(instrs)
    instrs = transform_class_returns(proc_decl, instrs)
    procedure = procedure.copy(instrs=instrs)
    procedure = remove_inlined_base_structors(procedure)
    procedure = remove_member_array_construction(procedure)
    procedure = discover_fields_initialization(procedure)
    procedure = discover_fields_destroying(procedure)
    procedure = insert_declarations(procedure, stack_vars)
    return split_jumped_declarations(procedure)


def _transform_instructions(instrs, analysis, **kwargs):
    call_args_matcher = CallArgumentsMatcher()
    new_instructions = transform_block(
        instrs,
        _ExpressionTransformer,
        call_args_matcher=call_args_matcher,
        analysis=analysis,
        **kwargs,
    )
    call_args_matcher.expect_all_args_are_matched()
    analysis.on_transformation_finished()
    return new_instructions


def _validate_procedure_info(proc_info, proc_decl):
    if proc_decl is None:
        return
    validate_procedure_declaration(
        proc_decl, proc_info.stack_delta, proc_info.is_thiscall)


def _eliminate_procedure_info(proc_info, instrs):
    if instrs[0] == proc_info:
        instrs.pop(0)
    return instrs


class _ExpressionTransformer(ExpressionTransformer):
    @staticmethod
    def transform_code_instruction(expression, **kwargs):
        return transform_struct_copy(expression, **kwargs)

    @staticmethod
    def transform_assignment(dst, src, **kwargs):
        return transform_assignment(dst, src, **kwargs)

    @staticmethod
    def transform_if(*args, **kwargs):
        return transform_if(*args, **kwargs)

    @staticmethod
    def transform_switch(*args, **kwargs):
        return transform_switch(*args, **kwargs)

    @staticmethod
    def transform_binary(operator, left, right, **kwargs):
        return transform_binary(operator, left, right, **kwargs)

    @staticmethod
    def transform_constant(c, **kwargs):
        return transform_constant(c, **kwargs)

    @staticmethod
    def transform_dereference(expression, **kwargs):
        return transform_dereference(expression, **kwargs)

    @staticmethod
    def transform_make_reference(expression, **kwargs):
        return transform_make_reference(expression, **kwargs)

    @staticmethod
    def transform_procedure_call(copy_pc, proc_name, arguments, **kwargs):
        return transform_procedure_call(copy_pc(), **kwargs)

    @staticmethod
    def transform_static_cast(data_type, expression, **kwargs):
        return inline_functions.transform_static_cast(
            data_type, expression, **kwargs)

    @staticmethod
    def transform_reinterpret_cast(data_type, expression, **kwargs):
        return transform_reinterpret(data_type, expression, **kwargs)

    @staticmethod
    def transform_access(*args, **kwargs):
        return transform_access(*args, **kwargs)

    @staticmethod
    def transform_arrptr(*args, **kwargs):
        return transform_arrptr(*args, **kwargs)

    @staticmethod
    def transform_global(*args, **kwargs):
        return transform_global(*args, **kwargs)

    @staticmethod
    def transform_local(*args, **kwargs):
        return transform_local(*args, **kwargs)

    @staticmethod
    def transform_stackvar(*args, **kwargs):
        return transform_stackvar(*args, **kwargs)

    @staticmethod
    def transform_block_instructions(block_instructions, **kwargs):
        return transform_block_instructions(block_instructions, **kwargs)
