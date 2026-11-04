"""Show which calls of inline functions cl.exe leaves not expanded.

Each experiment is a procedure calling inline methods of struct A: Big*
methods have the same body of a few statements, Small returns a field,
F1, F2 and G call other inline methods. For each procedure the calls left
in the listing are printed in their order, an expanded call has no call
instruction.
"""
import re

import vc6_listing

BIG = (
    "    int {name}(int x) {{ if (x > v) {{ v += x; if (v > 10) v = 10; }}"
    " else {{ v -= x; }} return v - {index}; }}\n")

STRUCT = (
    "struct A {\n"
    "    int v;\n" +
    "".join(BIG.format(name="Big%d" % i, index=i) for i in range(1, 8)) +
    "    int Small() { return v; }\n"
    "    void F1() { Big1(1); Big2(2); }\n"
    "    void F2() { Big3(3); Big4(4); }\n"
    "    void G() { F2(); Big5(5); }\n"
    "};\n"
    "A a;\n")

EXPERIMENTS = {
    # The calls are expanded in the order of the source until the limit,
    # the rest are left.
    "Sequence15": " ".join("a.Big7(%d);" % i for i in range(15)),
    "Sequence30": " ".join("a.Big7(%d);" % i for i in range(30)),
    # Calls of small methods hardly count.
    "SmallFirst": (
        " ".join("a.Small();" for i in range(20)) + " " +
        " ".join("a.Big7(%d);" % i for i in range(12))),
    # Calls in the procedure are expanded first, calls in the expanded
    # inline functions after them. Each expanded inline function has its
    # own limit of nested expansions: one Big* fits into F1, not two;
    # Big3 and Big4 don't fit into G with F2 and Big5.
    "Nested": (
        "a.F1(); a.G(); " +
        " ".join("a.Big6(%d);" % i for i in range(6))),
}


def source():
    text = STRUCT
    for name, body in EXPERIMENTS.items():
        text += "int {}() {{ {} return 0; }}\n".format(name, body)
    return text


def calls_left(listing):
    """Return {procedure: [called methods of A]}."""
    result = {}
    for match in re.finditer(
            r'^\?(\w+)@@YAHXZ PROC NEAR.*?ENDP', listing, re.M | re.S):
        result[match.group(1)] = re.findall(
            r'call\t\?(\w+)@A@@', match.group(0))
    return result


def main():
    left = calls_left(vc6_listing.compile_listing(source(), ("/Od", "/Ob1")))
    for name in EXPERIMENTS:
        calls = left.get(name, [])
        print("{}: {} calls left: {}".format(
            name, len(calls), " ".join(calls)))


if __name__ == "__main__":
    main()
