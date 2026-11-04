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
        previous = re.search(r'([A-Za-z_]\w*|[*&>])$', before)
        if (
            previous and after in ("=", ";", "(", "[", ",", ")") and
            previous.group(1) not in SKIPPED_PREVIOUS_WORDS
        ):
            result.append(match.start())
    return result


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
    for name, listing_names in by_name.items():
        positions = declarations(body, name)
        if len(positions) < len(listing_names):
            return None
        # Variables of the same name are numbered in order of declarations
        for (_, listing_name), position in zip(
            sorted(listing_names), positions
        ):
            found[listing_name] = (blocks[position], name, position)
    order = sorted(
        locals_, key=lambda n: stack_layout.order_key(*found[n]))
    offsets = [locals_[n] for n in order]
    valid = all(a > b for a, b in zip(offsets, offsets[1:]))
    details = [
        (found[n][1], locals_[n], found[n][0], stack_layout.bucket(found[n][1]))
        for n in order
    ]
    return details, valid


def find_source(listing_path, source_dir):
    base = os.path.splitext(os.path.basename(listing_path))[0]
    candidates = [base]
    if "_" in base:
        candidates.append(os.path.join(*base.split("_", 1)))
    for candidate in candidates:
        for ext in (".cpp", ".CPP", ".c"):
            path = os.path.join(source_dir, candidate + ext)
            if os.path.exists(path):
                return path
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
