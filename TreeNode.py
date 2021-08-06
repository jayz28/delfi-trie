from __future__ import annotations
from typing import MutableMapping, NewType, Union, NamedTuple, Optional
from collections import namedtuple


# define some type protocols
class SplitResult(NamedTuple):
    matched_prefix: str = ""
    remaining_prefix: str = ""
    remaining_word: str = ""


class FindResult(NamedTuple):
    node: TreeNode
    split: SplitResult


class TreeNode:
    def __init__(self, word: str = "", children: MutableMapping[str, TreeNode] = {}):

        self._children: MutableMapping[str, TreeNode] = children
        self._count: int = 0
        self._word: str = ""

        if word:
            self.set_is_word(word)

    @property
    def children(self) -> MutableMapping[str, TreeNode]:
        return self._children

    @children.setter
    def children(self, value: MutableMapping[str, TreeNode]):
        self._children = value

    @property
    def is_word(self) -> bool:
        return True if self._word else False

    @property
    def increment_count(self) -> None:
        self._count += 1

    def set_is_word(self, word: str) -> None:
        self._word = word
        self._count += 1

    def store_word(self, word: str):
        node, split = self._find_closest_match(word)

        # if there is no matched, add the fragment here
        if not split.matched_prefix:
            node.children[split.remaining_word] = TreeNode(word)
            return

        # if there is any remaining prefix, a split is necessary
        if split.remaining_prefix:
            oldnode = node.children.pop(str(split.matched_prefix + split.remaining_prefix))
            newnode = TreeNode(children={str(split.remaining_prefix): oldnode})

            node.children[str(split.matched_prefix)] = newnode

            node = newnode

        # if there are any characters left, create a new child node for them
        if split.remaining_word:
            node.children[str(split.remaining_word)] = TreeNode(word)
        else:
            node.set_is_word(word)  # if there is nothing left, it was an exact match

    def find_word(self, word: str):
        pass

    def _find_closest_match(self, fragment: str) -> FindResult:

        currentNode: TreeNode = self
        emptySplit: SplitResult = SplitResult(remaining_word=fragment)

        # loop through each edge to find a match
        for edge, node in currentNode.children.items():
            split: SplitResult = TreeNode._split_word(fragment, edge)

            if not split.matched_prefix:
                continue

            if split.remaining_prefix:
                return FindResult(currentNode, split)

            if split.remaining_word:
                return node._find_closest_match(split.remaining_word)
            else:
                return FindResult(node, split)

        return FindResult(currentNode, emptySplit)
        # # if we ave an exact match, return it
        # if TreeEdge(fragment) in self._children.keys():
        # return FindResult(node=self, split=SplitResult(matched_prefix=fragment))

        # # loop through each edge and find the best match
        # for edge, node in list(self._children.items()):
        # split: SplitResult = TreeNode._split_word(fragment, edge)

        # if not split.matched_prefix:
        # continue

        # if split.remaining_prefix:
        # return FindResult(node=self, split=split)

        # if split.remaining_word != fragment:
        # return node._find_closest_match(split.remaining_word)

        # return FindResult(node=self, split=SplitResult(remaining_word=fragment))

    @staticmethod
    def _split_word(word: str, edge: str) -> SplitResult:
        for idx, (k, v) in enumerate(zip(word, edge), start=1):
            if k != v:
                idx -= 1
                break
        return SplitResult(
            matched_prefix=edge[:idx],
            remaining_prefix=edge[idx:],
            remaining_word=word[idx:],
        )

    def __repr__(self):
        return ", ".join(f'{{"{e}-{n._word}": [{n}]}}' for e, n in self.children.items())
