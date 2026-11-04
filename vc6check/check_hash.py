"""Check the hash of local variable names (stack_layout.bucket) with cl.exe.

Procedures with int local variables of random names are compiled, buckets
of the names are found from the order of the variables in the listing and
compared with stack_layout.bucket.
"""
import argparse
import random
import re

import stack_layout
import vc6_listing

# Single letter names of all buckets: 'p' is in bucket 0, 'a' in bucket 1...
REFERENCES = list("pabcdefghijklmno")
KEYWORDS = {
    "asm", "auto", "bool", "break", "case", "catch", "char", "class",
    "const", "continue", "default", "delete", "do", "double", "else", "enum",
    "extern", "false", "float", "for", "friend", "goto", "if", "inline",
    "int", "long", "new", "operator", "private", "protected", "public",
    "register", "return", "short", "signed", "sizeof", "static", "struct",
    "switch", "template", "this", "throw", "true", "try", "typedef",
    "union", "unsigned", "using", "virtual", "void", "volatile", "while",
}


def variables_order(groups):
    """Compile a procedure per group of names, return orders of variables."""
    source = "int use__(void*);\n"
    for index, names in enumerate(groups):
        source += "void t{}() {{\n".format(index)
        for name in names:
            source += "    int {0}; use__(&{0});\n".format(name)
        source += "}\n"
    orders = {}
    for name, variables, _ in vc6_listing.read_procedures(
        vc6_listing.compile_listing(source)
    ):
        index = int(re.match(r'^\?t(\d+)@@', name).group(1))
        locals_ = sorted(variables, key=lambda v: -variables[v])
        orders[index] = [vc6_listing.variable_name(v) for v in locals_]
    return [orders[index] for index in range(len(groups))]


def buckets(names, chunk=100):
    """Find buckets of names by compiling them with the reference names.

    The reference names are declared first, so a later declared name is
    placed first in its bucket: a new bucket starts where the index of
    declaration increases.
    """
    groups = []
    for start in range(0, len(names), chunk):
        groups.append(
            REFERENCES +
            [n for n in names[start:start + chunk] if n not in REFERENCES])
    result = {}
    for group, order in zip(groups, variables_order(groups)):
        declaration_index = {name: i for i, name in enumerate(group)}
        bucket = 0
        result[order[0]] = bucket
        for previous, name in zip(order, order[1:]):
            if declaration_index[name] > declaration_index[previous]:
                bucket += 1
            result[name] = bucket
    return result


def random_names(count, seed):
    rng = random.Random(seed)
    first = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    names = set()
    while len(names) < count:
        name = rng.choice(first) + "".join(
            rng.choice(first + "0123456789")
            for _ in range(rng.randint(0, 30)))
        if name not in KEYWORDS:
            names.add(name)
    return sorted(names)


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument("names", nargs="*", help="names to check")
    arg_parser.add_argument("--random", type=int, default=600,
                            help="number of random names (default: 600)")
    arg_parser.add_argument("--seed", type=int, default=7)
    args = arg_parser.parse_args()
    names = args.names or random_names(args.random, args.seed)
    found = buckets(names)
    mismatches = [n for n in names if found[n] != stack_layout.bucket(n)]
    for name in mismatches:
        print("MISMATCH {} cl.exe: {} hash: {}".format(
            name, found[name], stack_layout.bucket(name)))
    print("Names: {}, mismatches: {}".format(len(names), len(mismatches)))


if __name__ == "__main__":
    main()
