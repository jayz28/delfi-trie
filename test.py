#!/usr/bin/env python3
from TreeNode import *


def main():
    root = TreeNode(children={})
    root.store_word("hello")
    root.store_word("hello")
    root.store_word("goodbye")
    root.store_word("gojira")
    root.store_word("hellen")

    print(root)


if __name__ == "__main__":
    main()
