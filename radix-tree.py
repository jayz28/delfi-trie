#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
from typing import MutableMapping, Union
from collections import namedtuple


class TreeNode:
    """
    Defines a node in the radix tree, internally represented as a hashmap,
    using the key as the edge and the value as the child node.
    """

    # define a lightweight protocol for the splitter for more readable access
    _SplitterResult: namedtuple = namedtuple("_SplitterResult", ["prefix", "edge", "data"])

    def __init__(self, children: MutableMapping[str, TreeNode] = {}, eow: bool = False):
        self.children: MutableMapping[str, TreeNode] = children
        self.eow: bool = eow
        self.weight: int = 1 if eow else 0
        self.count: int = 0
        self.label: str = ""

        for _, child in children.items():
            self.weight += child.weight

    # def add(self, fragment, word) -> TreeNode:
        # self.weight += 1

        # # on exact match, increment the weight and set eow
        # if match := self.children.get(data):
            # match.weight += 1
            # match.eow = True

        # result: Union[TreeNode, None] = None
        # for edge, node in list(self.children.items()):
            # split = TreeNode._splitter(edge, data)
            # if not split.prefix:
                # pass
            # else:
                # if split.edge:  # new edge is needed
                    # subtree = self.children.pop(edge)
                    # self.children[split.prefix] = TreeNode(children={split.edge: subtree})
                # if split.data:
                    # self.children[split.prefix].add(split.data)
                # result = self.children[split.prefix]

        # if not result:
            # self.children[data] = TreeNode(eow=True, children={})
            # result = self.children[data]
        # return result

    # def find(self, data) -> Union[TreeNode, None]:
        # result: Union[TreeNode, None] = None
        # print(data, file=sys.stderr)

        # if result := self.children.get(data, None):
            # return result

        # for edge, node in list(self.children.items()):
            # split: TreeNode._SplitterResult = TreeNode._splitter(edge, data)
            # print(split, file=sys.stderr)
            # if not split.prefix:
                # pass
            # elif split.edge:
                # return node
            # else:
                # return node.find(split.data)

    @staticmethod
    def _splitter(edge: str, data: str) -> _SplitterResult:

        for idx, (k, d) in enumerate(zip(edge, data), start=1):
            if k != d:
                idx -= 1
                break

        return TreeNode._SplitterResult(prefix=edge[:idx], edge=edge[idx:], data=data[idx:])

    def __repr__(self):

        return ", ".join(f'{{"{k}-{n.eow}": [{n}]}}' for k, n in self.children.items())


if __name__ == "__main__":
    root = TreeNode()
    with Path(sys.argv[1]).open("rt") as input_file:
        for line in input_file:
            node = root.add(line.rstrip())
    print(f"[{root}]")
    print(f'ok: {root.find("xxx").eow}', file=sys.stderr)
