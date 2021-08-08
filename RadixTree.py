from __future__ import annotations
from typing import (
    TypedDict,
    MutableMapping,
    Union,
    NamedTuple,
    Tuple,
    Callable,
    Optional,
)


# TypedDict at runtime is a native dict, minimizing memory overhead
class TreeNode(TypedDict):
    children: dict
    word: str
    count: int


# Lightweight NamedTuple protocol to reduce mistakes
_EdgeSplit = NamedTuple("_EdgeSplit", [("match", str), ("new", str), ("fragment", str)])
_FindResult = NamedTuple("_FindResult", [("node", TreeNode), ("split", _EdgeSplit)])


class RadixTree:

    _base_map: dict = {"N": 1, "A": 2, "T": 3, "C": 4, "G": 5}

    def __init__(self):
        self._root = TreeNode(children={}, word="", count=0)

    def store_word(self, word: str) -> None:
        node, split = self._find_node(word, self._root)

        get_int: Callable[[str], int] = RadixTree._get_int

        # if there's no match, attach the whole word here
        if not split.match:
            node["children"][get_int(word)] = TreeNode(children={}, word=word, count=1)
            return

        # if it's a perfect match, increment the count
        if not (split.new or split.fragment):
            node["word"] = word
            node["count"] += 1
            return

        # we need to split an existing key
        if split.new:
            old_key: int = get_int("".join([split.match, split.new]))
            old_node = node["children"].pop(old_key)
            new_node = TreeNode(
                word="",
                children={
                    get_int(split.new): old_node,
                },
                count=0,
            )
            node["children"][get_int(split.match)] = new_node
            node = new_node

        # if there's a fragment left
        if split.fragment:
            node["children"][get_int(split.fragment)] = TreeNode(
                word=word, children={}, count=1
            )

    @staticmethod
    def _find_node(fragment: str, start: TreeNode) -> _FindResult:
        currentSplit: _EdgeSplit = _EdgeSplit(match="", new="", fragment=fragment)
        currentNode: TreeNode = start

        # find an edge that matches the fragment
        for edgeint, node in currentNode["children"].items():
            edge: str = RadixTree._get_str(edgeint)
            split: _EdgeSplit = RadixTree._split_edge(edge, fragment)
            if split.match:
                currentSplit = split
                break

        matchint: int = RadixTree._get_int(currentSplit.match)

        # if we find none, or if we need to split, return the current node
        if not currentSplit.match or currentSplit.new:
            return _FindResult(currentNode, currentSplit)

        # if we find a perfect match, return the matched node
        if not (currentSplit.new or currentSplit.fragment):
            return _FindResult(currentNode["children"][matchint], currentSplit)

        # otherwise, recurse and keep searching
        return RadixTree._find_node(
            currentSplit.fragment, start=currentNode["children"][matchint]
        )

    @staticmethod
    def _split_edge(edge: str, fragment: str) -> _EdgeSplit:
        """
        Split edge if necessary, calculate remaining fragment
        """
        for idx, (k, v) in enumerate(zip(edge, fragment), start=1):
            if k != v:
                idx -= 1
                break
        return _EdgeSplit(match=edge[:idx], new=edge[idx:], fragment=fragment[idx:])

    @staticmethod
    def _get_int(word: str) -> int:
        """
        Convert arbitrary string composed of {A,T,C,G,N} to 3bit integer representation
        """
        result: int = 0

        for idx, char in enumerate([RadixTree._base_map[c] for c in word]):
            result += char << 3 * idx

        return result

    @staticmethod
    def _get_str(wordint: int) -> str:
        """
        Restore original string from 3bit integer representation
        """
        if wordint > 0:
            next_val: int = wordint >> 3
            base: str = list(RadixTree._base_map.keys())[wordint - (next_val << 3) - 1]
            return "".join([base, RadixTree._get_str(next_val)])
        else:
            return ""
