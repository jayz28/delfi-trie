#!/usr/bin/env python3
from RadixTree import RadixTree
import sys
from pathlib import Path
from json import dumps, loads


def main(args):
    tree = RadixTree()
    with Path(args[0]).open("rt") as infile:
        for line in infile:
            tree.store_word(line.rstrip())

    print(f"{dumps(tree._root)}")


if __name__ == "__main__":
    main(sys.argv[1:])
