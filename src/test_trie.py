import pytest
from .tries import RadixTree, SuffixTree


@pytest.fixture
def test_trees():
    return (RadixTree(), SuffixTree())


def test_radix_store(test_trees):
    radix_tree, suffix_tree = test_trees
    radix_tree.store_word("ATCG")
    assert radix_tree.find_word("ATCG")
    assert not radix_tree.find_word("NNN")


def test_suffix_store(test_trees):
    _, suffix_tree = test_trees
    suffix_tree.store_word("ATCG")
    print(suffix_tree)
    assert suffix_tree.count_occurrence("TC") == 1
    assert suffix_tree.count_occurrence("NNN") == 0
    assert suffix_tree.count_occurrence("ATC") == 1
