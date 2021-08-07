from __future__ import annotations
from typing import MutableMapping, NewType, Union, NamedTuple, Optional, cast
from collections import namedtuple
import sys


# define some type protocols to improve readability and leverge type checking
# using NamedTuple here for a lighterwight native implementation vs @dataclass
class SplitResult(NamedTuple):
    matched_prefix: str = ""
    remaining_prefix: str = ""
    remaining_fragment: str = ""


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
            node.children[split.remaining_fragment] = TreeNode(word)
            return

        # if there is any remaining prefix, a split is necessary
        if split.remaining_prefix:
            oldnode = node.children.pop(str(split.matched_prefix + split.remaining_prefix))
            newnode = TreeNode(children={str(split.remaining_prefix): oldnode})

            node.children[str(split.matched_prefix)] = newnode

            node = newnode

        # if there are any characters left, create a new child node for them
        if split.remaining_fragment:
            node.children[str(split.remaining_fragment)] = TreeNode(word)
        else:
            node.set_is_word(word)  # if there is nothing left, it was an exact match

    def find_word(self, word: str) -> Union[TreeNode, None]:
        result: FindResult = self._find_closest_match(word)

        if result.node.is_word:
            return result.node

        return None

    def _find_closest_match(self, fragment: str) -> FindResult:

        result: FindResult = FindResult(node=self, split=SplitResult(remaining_fragment=fragment))

        # on exact match, return the matched node and prefix
        if node := self.children.get(fragment, False):
            result = FindResult(cast(TreeNode, node), SplitResult(matched_prefix=fragment))
        else:
            # loop through each edge to find a match
            for edge, node in self.children.items():
                split: SplitResult = TreeNode._split_word(fragment, edge)
                if split.matched_prefix:
                    result = FindResult(self, split)

            # if there is no remaining prefix, serch recursively
            if result.split.matched_prefix and not result.split.remaining_prefix:
                result = result.node.children[result.split.matched_prefix]._find_closest_match(
                    result.split.remaining_fragment
                )

        return result

    @staticmethod
    def _split_word(word: str, edge: str) -> SplitResult:
        for idx, (k, v) in enumerate(zip(word, edge), start=1):
            if k != v:
                idx -= 1
                break
        return SplitResult(
            matched_prefix=edge[:idx],
            remaining_prefix=edge[idx:],
            remaining_fragment=word[idx:],
        )

    def __repr__(self):
        children: str = ", ".join(f'{{"{e}": [{n}]}}' for e, n in self.children.items())
        output: str = f'{{"word": "{self._word or "" }", "count": {self._count}, "children": [{children}]}}'
        return output
