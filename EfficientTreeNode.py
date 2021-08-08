from __future__ import annotations
from typing import (
    OrderedDict,
    TypedDict,
    MutableMapping,
    Union,
    NamedTuple,
    Tuple,
    Callable,
)


# TypedDict at runtime is a native dict, minimizing memory overhead
class TreeNode(TypedDict):
    children: MutableMapping[int, TreeNode]
    word: str
    count: int


# Lightweight NamedTuple protocol to reduce mistakes
_EdgeSplit = NamedTuple("_EdgeSplit", [("match", str), ("new", str), ("fragment", str)])
_FindResult = NamedTuple("_FindResult", [("node", TreeNode), ("split", _EdgeSplit)])


class RadixTree:

    _base_map: OrderedDict = {"N": 1, "A": 2, "T": 3, "C": 4, "G": 5}

    def __init__(self):
        self._root = TreeNode(children={}, word="", count=0)

    def store_word(self, word: str) -> None:
        node, split = self._find_node(word)

        get_int: Callable[[str]] = RadixTree._get_int

        # we need to split an existing key
        if split.new:
            old_key = get_int("".join([split.match, split.new]))
            old_node = node["children"].pop(old_key)
            new_node = TreeNode(
                word=word, children={get_int(split.new): old_node}, count=1
            )
            node["children"][get_int(split.match)] = new_node

        # if there's no match, attach the whole word here
        elif not split.match:
            node["children"][get_int(word)] = TreeNode(word=word, count=1)

        # otherwise, this is a perfect match, increment the node count
        else:
            node.word = word
            node.count += 1

    def _find_node(self, fragment: str) -> _FindResult:
        currentSplit: _EdgeSplit = _EdgeSplit(match="", new="", fragment=fragment)
        currentNode: TreeNode = self._root

        # find an edge that matches the fragment
        for edgeint, node in self._root["children"].items():
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
            return _FindResult(self._children[matchint], currentSplit)

        # otherwise, recurse and keep searching
        return self._children[matchint]._find_node(currentSplit.fragment)

    @staticmethod
    def _split_edge(edge: str, fragment: str) -> _EdgeSplit:
        """
        Split edge if necessary, calculate remaining fragment
        """
        for idx, (k, v) in enumerate(zip(edge, fragment)):
            if k != v:
                idx -= 1
                break
        return _EdgeSplit(match=edge[:idx], new=edge[idx:], fragment=fragment[idx:])

    @staticmethod
    def _get_int(word: str) -> Union[int, None]:
        """
        Convert arbitrary string composed of {A,T,C,G,N} to 3bit integer representation
        """
        result: int = 0
        if not word:
            return None

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
            return """
