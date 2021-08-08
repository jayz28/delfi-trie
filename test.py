#!/usr/bin/env python3
from RadixTree import RadixTree
from TreeNode import TreeNode
from memory_profiler import profile

import sys
from pathlib import Path
from json import dumps, loads


@profile
def main(args):
    tree = RadixTree()
    root = TreeNode()
    with Path(args[0]).open("rt") as infile:
        for line in infile:
            tree.store_word(line.rstrip())
            root.store_word(line.rstrip())

    print(tree)
    print(get_size(tree), file=sys.stderr)
    print(get_size(root), file=sys.stderr)


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


if __name__ == "__main__":
    main(sys.argv[1:])
