#!/usr/bin/env python3
from RadixTree import RadixTree, SuffixTree
from TreeNode import TreeNode

import sys
from pathlib import Path
from pickle import loads, dumps


def main(args):
    tree = RadixTree()
    root = SuffixTree()
    with Path(args[0]).open("rt") as infile:
        for line in infile:
            tree.store_word(line.rstrip())
            root.store_word(line.rstrip())

    treebytes = dumps(tree)
    rootbytes = dumps(root)

    print(tree)
    print("\n")
    print(root)
    print(f"radix: {sys.getsizeof(treebytes)}")
    print(f"suffix: {sys.getsizeof(rootbytes)}")

    print(f'node: {tree.find_word("ATAACCTGAG")}')

    print(root.count_occurrence("GG"))
    print(root.count_fraction(["G", "C"]))


if __name__ == "__main__":
    main(sys.argv[1:])
