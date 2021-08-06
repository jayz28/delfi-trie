from __future__ import annotations
from typing import MutableMapping, NewType, Union, NamedTuple, Optional
from collections import namedtuple


# define some type aliases/protocols
TreeEdge = NewType("TreeEdge", str)


class SplitResult(NamedTuple):
    matched_prefix: str = ""
    remaining_prefix: str = ""
    remaining_word: str = ""


class FindResult(NamedTuple):
    node: TreeNode
    split: SplitResult


class TreeNode:
    def __init__(self, word: str = "", children: MutableMapping[TreeEdge, TreeNode] = {}):

        self._children: MutableMapping[TreeEdge, TreeNode] = children
        self._eow: bool = True if word else False
        self._count: int = 0
        self._word: str = word

    @property
    def children(self) -> MutableMapping[TreeEdge, TreeNode]:
        return self._children

    @children.setter
    def children(self, value: MutableMapping[TreeEdge, TreeNode]):
        self._children = value

    @property
    def is_word(self) -> bool:
        return self._eow

    @property
    def increment_count(self) -> None:
        self._count += 1

    def store_word(self, word: str):
        node, split = self._find_closest_match(word)

        # if there is no matched, add the fragment here
        if not split.matched_prefix:
            node.children[TreeEdge(word)] = TreeNode(word)
            return
        if split.remaining_prefix:
            oldnode = node.children.pop(TreeEdge(split.matched_prefix + split.remaining_prefix))
            newnode = TreeNode(children={TreeEdge(split.remaining_prefix): oldnode})

            node.children[TreeEdge(split.matched_prefix)] = newnode

            node = newnode

        if split.remaining_word:
            node.children[TreeEdge(split.remaining_word)] = TreeNode(word)

    def find_word(self, word: str):
        pass

    def _find_closest_match(self, fragment: str) -> FindResult:

        # if we ave an exact match, return it
        if TreeEdge(fragment) in self._children.keys():
            return FindResult(node=self, split=SplitResult(matched_prefix=fragment))

        # loop through each edge and find the best match
        for edge, node in list(self._children.items()):
            split: SplitResult = TreeNode._split_word(fragment, edge)

            if not split.matched_prefix:
                continue

            if split.remaining_prefix:
                return FindResult(node=self, split=split)

            if split.remaining_word != fragment:
                return node._find_closest_match(split.remaining_word)

        return FindResult(node=self, split=SplitResult(remaining_word=fragment))

    @staticmethod
    def _split_word(word: str, edge: TreeEdge) -> SplitResult:
        for idx, (k, v) in enumerate(zip(word, edge), start=1):
            if k != v:
                idx -= 1
                break
        return SplitResult(matched_prefix=edge[:idx], remaining_prefix=edge[idx:], remaining_word=word[idx:])

    def __repr__(self):
        return ", ".join(f'{{"{e}": [{n}]}}' for e, n in self.children.items())
