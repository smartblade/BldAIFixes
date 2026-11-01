import json
import os

from get_procedure_declaration_at import get_procedure_declaration_at
from get_procedure_declaration_at import has_src_declaration
from hex_conversion import from_hex, to_hex
from make_tuple import add_attributes
from patterns.apply_pattern import apply_pattern
from patterns.annotate_import_jumps import annotate_import_jumps
from patterns.collect_read_only_data import collect_read_only_data
from patterns.collect_string_constants import collect_string_constants
from patterns.asm_parser import parse_asm_lines
from patterns.high_level import make_high_level_code
import patterns.high_level.inline_functions as inline_functions
from patterns.prefix_status import PrefixStatus
from patterns.structure import Patterns
from patterns.builder import ProcedureBuilder
from writer import Writer

# Procedures to convert for each module, None means all procedures
_converted_procedures = {
    "BBLibc.dll": None,
    "Blade.exe": {
        0x00401000,
        0x004015C5,
        0x0040A5D0,
        0x004501C1,
        0x00450327,
        0x00450380,
        0x00450407,
        0x00450417,
        0x00450450,
        0x0045047C,
        0x0045048C,
        0x0045050B,
        0x004506B5,
        0x004507B9,
        0x0045201F,
        0x00452082,
        0x00452191,
        0x00452232,
        0x00452388,
        0x00452845,
        0x00453067,
        0x00453264,
        0x0045327B,
        0x0045346F,
        0x00453490,
        0x004539A9,
        0x00453AC0,
    },
}


def process_asm_patterns(lines, declarations):
    module = declarations.symbols.module
    if module not in _converted_procedures:
        return []
    patterns_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "patterns.json")
    with open(patterns_path, "rt") as f:
        patterns = Patterns(json.load(f))
    writer = Writer()
    smallest_failed_proc_len = None
    smallest_failed_proc_exc = None
    smallest_failed_proc_addr = None
    standard_inlines = {}
    lines = annotate_import_jumps(lines)
    string_constants = collect_string_constants(lines)
    declarations = add_attributes(
        declarations,
        string_constants=string_constants,
        read_only_data=collect_read_only_data(lines),
    )
    inline_procedures = inline_functions.Dict()
    asm_procedures = _extract_procedures_lines_from_asm(
        lines, _converted_procedures[module])
    # Get all declarations before building procedures: demangling adds
    # undeclared types to declared types, so demangle exported names
    # before parsing declarations from sources
    proc_decls = {}
    for proc_addr in sorted(
        (proc_addr for proc_addr, _ in asm_procedures),
        key=lambda addr: has_src_declaration(declarations, addr)
    ):
        proc_decls[proc_addr] = get_procedure_declaration_at(
            declarations, proc_addr)
    procedures = []
    for proc_addr, proc_lines in asm_procedures:
        exc, procedure = _build_proc(
            declarations, standard_inlines, inline_procedures, patterns,
            proc_addr, proc_decls[proc_addr], proc_lines)
        procedures.append((exc, procedure))
        if exc is not None:
            if (
                smallest_failed_proc_len is None or
                len(proc_lines) < smallest_failed_proc_len
            ):
                smallest_failed_proc_len = len(proc_lines)
                smallest_failed_proc_addr = proc_addr
                smallest_failed_proc_exc = exc
    _write_procedures(writer, procedures)
    inline_procedures.make_high_level_code(declarations)
    inline_procedures.write_procedures(writer)
    with open("{}.cpp".format(module), "wt") as f:
        f.write(writer.get_string())
    if smallest_failed_proc_exc is not None:
        raise Exception(
            "Failed to build {}".format(to_hex(smallest_failed_proc_addr))
        ) from smallest_failed_proc_exc
    return [procedure for exc, procedure in procedures if exc is None]


def _build_proc(
    declarations, standard_inlines, inline_procedures, patterns,
    proc_addr, proc_decl, proc_lines
):
    builder = ProcedureBuilder(proc_decl, proc_addr, standard_inlines)
    error = None
    try:
        _parse_asm_proc(
            patterns,
            proc_lines,
            builder=builder,
            string_constants=declarations.string_constants,
            external_procedures=declarations.external_procedures,
        )
    except Exception as exc:
        error = exc
    procedure = builder.build_procedure()
    if error is None:
        procedure = make_high_level_code(
            procedure, declarations, inline_procedures)
    return error, procedure


def _extract_procedures_lines_from_asm(lines, converted_procedures):
    proc_addr = None
    proc_lines = []
    asm_procedures = []
    for line in lines:
        if line.startswith("l") and line.find("PROC") >= 0:
            proc_addr = from_hex(line[1:9])
            proc_lines = []
        elif proc_addr is not None and line.find("ENDP") >= 0:
            if (
                converted_procedures is None or
                proc_addr in converted_procedures
            ):
                asm_procedures.append((proc_addr, proc_lines))
            proc_addr = None
        elif proc_addr is not None:
            proc_lines.append(line.strip())
    return asm_procedures


def _write_procedures(writer, procedures):
    for exc, procedure in procedures:
        writer.write_line()
        procedure.emit_code(writer)
        if exc is not None:
            writer.write_line('Error: "{}"'.format(str(exc)))


def _parse_asm_proc(patterns, lines, **kwargs):
    instrs = parse_asm_lines(lines, patterns.commands_code_dict)
    prefix_status = PrefixStatus(patterns.make_prefix_builder(), instrs)
    cur_index = 0
    while cur_index < len(instrs):
        pattern, match_dict, cur_index = _match_patterns(
            prefix_status, patterns, cur_index, instrs)
        apply_pattern(pattern, match_dict, **kwargs)


def _match_patterns(prefix_status, patterns, first_index, instrs):
    instructions_patterns = patterns.instructions_patterns_by_prefix(
        prefix_status.prefix)
    for pattern in instructions_patterns:
        last_index, match_dict = _match_instructions_pattern(
            pattern, first_index, instrs)
        if last_index > first_index:
            prefix_status.update(last_index - first_index)
            return pattern, match_dict, last_index
    raise Exception(
        "Failed to find pattern for '{}'".format(instrs[first_index]))


def _match_instructions_pattern(pattern, first_index, instrs):
    match_dict = dict()
    cur_index = first_index
    for instr_pattern in pattern.instructions:
        if not _match_instruction(instr_pattern, instrs[cur_index], match_dict):
            return -1, None
        cur_index += 1
    return cur_index, match_dict


def _match_instruction(instr_pattern, instr, match_dict):
    if instr_pattern.command_code != instr.command_code:
        return False
    if len(instr_pattern.operands) != len(instr.operands):
        return False
    for op_index in range(len(instr.operands)):
        operand = instr.operands[op_index]
        operand_pattern = instr_pattern.operands[op_index]
        cur_match_dict = operand_pattern.match(operand.asm, operand.size)
        if cur_match_dict is None:
            return False
        for param, value in cur_match_dict.items():
            if param not in match_dict:
                match_dict[param] = value
            elif match_dict[param] != value:
                if param == "size":
                    match_dict[param].invalidate()
                else:
                    return False
    return True
