#!/usr/bin/env python3
from pathlib import Path
from typing import MutableMapping, Union, Any
from collections import namedtuple


class TrieNode:
    def __init__(self, children: MutableMapping[str, Any] = {}, eow: bool = False):
        self.children: MutableMapping[str, Any] = children
        self.eow: bool = eow
        self.weight: int = 1 if eow else 0

    def add(self, data) -> Any:
        self.weight += 1

        # on exact match, increment the weight and set eow
        if match := self.children.get(data, False):
            match.weight += 1
            match.eow = True

        result: Union[TrieNode, None] = None
        for key, node in list(self.children.items()):
            split = self._splitter(key, data)
            if not split.prefix:
                pass
            else:
                if split.key:  # new key is needed
                    subtree = self.children.pop(key)
                    self.children[split.prefix] = TrieNode(children={split.key: subtree})
                if split.data:
                    self.children[split.prefix].add(split.data)
                result = self.children[split.prefix]

        if not result:
            self.children[data] = TrieNode(eow=True, children={})

    _SplitResult: namedtuple = namedtuple("_Split", ["prefix", "key", "data"])

    def _splitter(self, key: str, data: str) -> _SplitResult:
        idx = 0

        for idx, (k, d) in enumerate(zip(key, data), start=1):
            if k != d:
                idx -= 1
                break

        return TrieNode._SplitResult(prefix=key[:idx], key=key[idx:], data=data[idx:])

    def __repr__(self):

        return ", ".join(f'{{"{k}": [{n}]}}' for k, n in self.children.items())


if __name__ == "__main__":
    root = TrieNode()
    with Path("long.txt").open("rt") as input_file:
        for line in input_file:
            node = root.add(line.rstrip())
    print(f"[{root}]")
