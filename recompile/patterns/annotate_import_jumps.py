import re

label_regexp = re.compile(
    r'^l(?P<addr>[\dABCDEF]{8})(:\s*(?P<instr>\S.*)|\s+PROC)$')
jump_regexp = re.compile(r'^jmp near ptr l(?P<addr>[\dABCDEF]{8})$')
import_jump_regexp = re.compile(r'^jmp \[__imp_\S+\];\s+(?P<external>\[.+\]\.)$')
call_regexp = re.compile(r'^(?P<call>\s+call l(?P<addr>[\dABCDEF]{8}))$')


def annotate_import_jumps(lines):
    """Annotate calls of chains of jumps to imported procedures.

    Calls of import thunks are annotated with names of imported procedures
    ('call l100415E4; [BICRT.??2@YAPAXI@Z].'), annotate calls of jumps to
    import thunks the same way, for example calls of operator new aliased
    to SmartHeap:

    l005BBD38 PROC
               jmp near ptr l005BBD5C
    ...
    l005BBD5C: jmp [__imp_shi_new]; [SHW32.shi_new].
    """
    first_instructions = _collect_first_instructions(lines)
    new_lines = []
    for line in lines:
        match = call_regexp.search(line.rstrip("\n"))
        if match:
            external = _find_import(first_instructions, match.group("addr"))
            if external is not None:
                line = "{}; {}\n".format(match.group("call"), external)
        new_lines.append(line)
    return new_lines


def _collect_first_instructions(lines):
    first_instructions = {}
    label = None
    for line in lines:
        line = line.rstrip("\n")
        if label is not None:
            first_instructions[label] = line.strip()
            label = None
            continue
        match = label_regexp.search(line)
        if not match:
            continue
        if match.group("instr") is not None:
            first_instructions[match.group("addr")] = match.group("instr")
        else:
            label = match.group("addr")
    return first_instructions


def _find_import(first_instructions, addr, max_jumps=4):
    for _ in range(max_jumps):
        instr = first_instructions.get(addr)
        if instr is None:
            return None
        match = jump_regexp.search(instr)
        if not match:
            break
        addr = match.group("addr")
        match = import_jump_regexp.search(first_instructions.get(addr, ""))
        if match:
            return match.group("external")
    return None
