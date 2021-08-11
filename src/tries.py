"""
This file implements 2 primary classes: RadixTree and SuffixTree used to solve the python algorithm challenge.
The challenge calls for storing strings with a known alphabet {A,T,C,G,N} and the frequency of their appearance
in a memory efficient manner, with the added ability to search for single character patterns in the resulting trie.

To address memory efficiency, a compressed trie (RadixTree) is used, with nodes implemented as native python
dicts to avoid per node memory overhead from python instance methods.
The alphabet is stored as 3bit integers, bit packed into python integers which have a slightly smaller memory
footprint than python strings.

To support pattern searching of the stored strings, the RadixTree is extended to create a "brute-force"
SuffixTree, storing all possible suffixes for simple pattern search.  Possible improvements here is to use
Ukkonen's method for construction in O(n) time complexity if run time is of concern.

"""
from __future__ import annotations
from typing import (
    TypedDict,
    Union,
    NamedTuple,
    Callable,
    Iterable,
    List,
    OrderedDict,
)


# TypedDict at runtime is a native dict, minimizing memory overhead of python objects
class TreeNode(TypedDict):
    children: dict
    count: int


# Lightweight NamedTuple protocol to reduce mistakes in remembering field order
_EdgeSplit = NamedTuple("_EdgeSplit", [("match", str), ("new", str), ("fragment", str)])
_FindResult = NamedTuple("_FindResult", [("node", TreeNode), ("split", _EdgeSplit)])


class RadixTree:
    """
    Implement radix tree for better space efficiency
    """

    # map bases to 3bit integers, reserve 0 for "no word"
    _base_map: OrderedDict[str, int] = OrderedDict({"N": 0b001, "A": 0b010, "T": 0b011, "C": 0b100, "G": 0b101})

    def __init__(self):
        self._root = TreeNode(children={}, count=0)

    def find_word(self, word: str) -> Union[TreeNode, None]:
        """
        Returns leaf node representing word, or None
        """
        result: _FindResult = RadixTree._find_node(word, self._root)
        return result.node if result.node["count"] > 0 else None

    def store_word(self, word: str) -> None:
        """
        Stores new word into trie
        """

        # find path to closest match
        node, split = RadixTree._find_node(word, self._root)

        get_int: Callable[[str], int] = RadixTree._get_int

        # if there's no match, attach the whole word here
        if not split.match:
            node["children"][get_int(split.fragment)] = TreeNode(children={}, count=1)
            return

        # if it's a perfect match, increment the count
        if not (split.new or split.fragment):
            node["count"] += 1
            return

        # we need to split an existing key
        if split.new:
            old_key: int = get_int("".join([split.match, split.new]))
            old_node = node["children"].pop(old_key)
            new_node = TreeNode(
                children={
                    get_int(split.new): old_node,
                },
                count=1 if not split.fragment else 0,
            )
            node["children"][get_int(split.match)] = new_node
            node = new_node

        # if there's a fragment left, add it as a word
        if split.fragment:
            node["children"][get_int(split.fragment)] = TreeNode(children={}, count=1)

    @staticmethod
    def _find_node(fragment: str, start: TreeNode) -> _FindResult:
        """
        Find the closest node to the fragment
        """
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
        return RadixTree._find_node(currentSplit.fragment, start=currentNode["children"][matchint])

    @staticmethod
    def _split_edge(edge: str, fragment: str) -> _EdgeSplit:
        """
        Split edge if necessary, calculate remaining fragment
        """
        idx: int = 0
        for idx, (e, f) in enumerate(zip(edge, fragment), start=1):
            if e != f:
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

    @staticmethod
    def _render_node(node: TreeNode) -> str:
        """
        Recursively render nodes
        """
        children: str = ", ".join(
            f'{{ "{RadixTree._get_str(e)}" : {RadixTree._render_node(n)}  }}' for e, n in node["children"].items()
        )
        output: str = f'{{"count": {node["count"]}, "children": [{children}]}}'

        return output

    def __repr__(self):
        return RadixTree._render_node(self._root)


class SuffixTree(RadixTree):
    """
    Override store_word in base RadixTree to store every suffix of the word
    """

    def store_word(self, word: str) -> None:
        for idx in range(len(word)):
            super().store_word(word[idx:])

    def count_fraction(self, target_set: Iterable[str]) -> float:
        """
        Count the fraction of the target character set
        """

        sum_total: int = 0
        total_chars: int = SuffixTree._sum_counts(self._root)
        for char in target_set:
            assert len(char) == 1
            sum_total += self.count_occurrence(char)

        return sum_total / total_chars

    def count_occurrence(self, pattern: str) -> int:
        """
        Count the occurence of the search pattern
        """
        result: _FindResult = self._find_node(pattern, self._root)
        if result.split.match and not result.split.fragment:

            if result.split.new:
                return SuffixTree._sum_counts(result.node["children"][self._get_int(result.split.match + result.split.new)])
            else:
                return SuffixTree._sum_counts(result.node)


        return 0

    @staticmethod
    def _sum_counts(start: TreeNode) -> int:
        """
        Recursively sum counts of child nodes
        """
        count: int = start["count"]
        if start["children"]:
            count += sum([SuffixTree._sum_counts(node) for _, node in start["children"].items()])

        return count
