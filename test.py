#!/usr/bin/env python3
from RadixTree import RadixTree
from TreeNode import TreeNode

import sys
from pathlib import Path
from pickle import loads, dumps


def main(args):
    tree = RadixTree()
    root = TreeNode()
    with Path(args[0]).open("rt") as infile:
        for line in infile:
            tree.store_word(line.rstrip())
            root.store_word(line.rstrip())

    treebytes = dumps(tree)
    rootbytes = dumps(root)

    print(tree)
    print(f"tree: {sys.getsizeof(treebytes)}")
    print(f"root: {sys.getsizeof(rootbytes)}")


if __name__ == "__main__":
    main(sys.argv[1:])
