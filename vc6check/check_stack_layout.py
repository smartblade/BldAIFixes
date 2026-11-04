"""Check the stack layout rules of stack-layout.md on compiled sources.

Local variables of each procedure of the listings (cl.exe /FAs) are sorted
by stack_layout.order_key: blocks and declarations are found in the source
file of the listing. The offsets of the sorted variables must decrease.
"this", temporaries of the compiler and procedures with variables that are
not found in the source are skipped.
"""
import argparse
import os
import re

import stack_layout
import vc6_listing

SKIPPED_PREVIOUS_WORDS = {
    "return", "delete", "else", "case", "goto", "sizeof", "new"
}


def blank_comments_and_strings(text):
    def blank(match):
        return re.sub(r'[^\n]', ' ', match.group(0))
    text = re.sub(r'//[^\n]*', blank, text)
    text = re.sub(r'/\*.*?\*/', blank, text, flags=re.S)
    text = re.sub(r'"(\\.|[^"\\\n])*"', blank, text)
    return re.sub(r"'(\\.|[^'\\\n])*'", blank, text)


def blocks_of_positions(body):
    """Index of the innermost block (in preorder) of each position."""
    stack, next_index, blocks = [], 0, []
    for ch in body:
        if ch == "{":
            stack.append(next_index)
            next_index += 1
        blocks.append(stack[-1] if stack else 0)
        if ch == "}" and stack:
            stack.pop()
    return blocks


def declarations(body, name):
    """Positions of declarations of a variable in the body."""
    result = []
    for match in re.finditer(r'(?<![\w.>])' + re.escape(name) + r'\b', body):
        before = body[:match.start()].rstrip()
        after = body[match.end():].lstrip()[:1]
        previous = re.search(r'([A-Za-z_]\w*|[*&>,])$', before)
        if (
            not previous or after not in ("=", ";", "(", "[", ",", ")") or
            previous.group(1) in SKIPPED_PREVIOUS_WORDS
        ):
            continue
        if previous.group(1) == "," and not _is_declarator_list(before):
            continue
        result.append(match.start())
    return result


def _is_declarator_list(before):
    """Whether a name after a comma is a declarator, e.g. 'int a, b'."""
    statement = re.split(r'[;{}]', before)[-1]
    depth = 0
    for ch in statement:
        depth += {"(": 1, ")": -1}.get(ch, 0)
        if depth < 0:
            return False
    return depth == 0 and re.match(r'\s*[A-Za-z_]\w*[\w\s:<>*&]*\s[*&]*[A-Za-z_]', statement) is not None


def check_procedure(source_lines, variables, lines):
    """Return sorted [(name, offset, block, bucket)] and whether it's valid.

    None is returned if the procedure can't be checked.
    """
    locals_ = {
        name: offset for name, offset in variables.items()
        if offset < 0 and not name.startswith("$T") and name != "_this$"
    }
    if len(locals_) < 2 or not lines or max(lines) > len(source_lines):
        return None
    text = "\n".join(source_lines[min(lines) - 1:max(lines)])
    if "{" not in text:
        return None
    body = text[text.index("{"):]
    blocks = blocks_of_positions(body)
    by_name = {}
    for listing_name in locals_:
        suffix = re.search(r'\$(\d*)$', listing_name).group(1)
        by_name.setdefault(vc6_listing.variable_name(listing_name), []).append(
            (int(suffix) if suffix else -1, listing_name))
    found = {}
    inlined = []
    for name, listing_names in by_name.items():
        positions = declarations(body, name)
        # A variable of the body of the procedure has no number in the
        # listing, variables of nested blocks are numbered in order of
        # declarations, variables of inlined procedures have the highest
        # numbers
        listing_names = sorted(listing_names)
        if listing_names[0][0] == -1:
            body_positions = [p for p in positions if blocks[p] == 0]
            if not body_positions:
                return None
            found[listing_names[0][1]] = (0, name, body_positions[0])
            positions.remove(body_positions[0])
            listing_names = listing_names[1:]
        for index, (_, listing_name) in enumerate(listing_names):
            if index < len(positions):
                position = positions[index]
                found[listing_name] = (blocks[position], name, position)
            else:
                inlined.append(listing_name)
    if len(found) < 2:
        return None
    order = sorted(found, key=lambda n: stack_layout.order_key(*found[n]))
    offsets = [locals_[n] for n in order]
    valid = all(a > b for a, b in zip(offsets, offsets[1:]))
    # Variables of inlined procedures are placed after the variables of
    # the source
    if inlined and max(locals_[n] for n in inlined) > min(offsets):
        valid = False
    details = [
        (found[n][1], locals_[n], found[n][0], stack_layout.bucket(found[n][1]))
        for n in order
    ] + [(vc6_listing.variable_name(n), locals_[n], "inlined") for n in inlined]
    return details, valid


def find_source(listing_path, source_dir):
    """Source of Dir_Name.asm: Name.cpp or Dir/Name.cpp in source_dir."""
    base = os.path.splitext(os.path.basename(listing_path))[0]
    for root, _, files in os.walk(source_dir):
        relative = os.path.relpath(root, source_dir)
        prefix = "" if relative == "." else relative.replace(os.sep, "_") + "_"
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext.lower() in (".cpp", ".c") and prefix + name == base:
                return os.path.join(root, file_name)
    return None


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument(
        "listings", help="directory of listings (name.asm or dir_name.asm "
        "for source dir/name.cpp)")
    arg_parser.add_argument("sources", help="directory of sources")
    arg_parser.add_argument("-v", "--verbose", action="store_true")
    args = arg_parser.parse_args()
    checked = valid = 0
    for file_name in sorted(os.listdir(args.listings)):
        if not file_name.endswith(".asm"):
            continue
        listing_path = os.path.join(args.listings, file_name)
        source_path = find_source(listing_path, args.sources)
        if source_path is None:
            continue
        with open(source_path, encoding="latin-1") as f:
            source_lines = blank_comments_and_strings(f.read()).split("\n")
        with open(listing_path, encoding="latin-1") as f:
            listing = f.read()
        for name, variables, lines in vc6_listing.read_procedures(listing):
            result = check_procedure(source_lines, variables, lines)
            if result is None:
                continue
            details, is_valid = result
            checked += 1
            valid += is_valid
            if args.verbose or not is_valid:
                print("{} {} {}".format(
                    "MATCH   " if is_valid else "MISMATCH", name, details))
    print("Checked procedures: {}, matching the rules: {}".format(
        checked, valid))


if __name__ == "__main__":
    main()
