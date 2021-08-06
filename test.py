#!/usr/bin/env python3
from TreeNode import *
import sys
from pathlib import Path


def main(args):
    root = TreeNode(children={})

    with Path(args[0]).open("rt") as infile:
        for line in infile:
            root.store_word(line.rstrip())

    print(f'[{root}]')


if __name__ == "__main__":
    main(sys.argv[1:])
