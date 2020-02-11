# author: Martín Quesada Zaragoza

from alt_project import ALT_library as lib
import numpy as np


class TestDistanceCalc:

    # Tests relative to building the trie
    def test_build_trie(self):
        vocab_list = ["caro", "cara", "codo", "caros"]
        correct_matrix = np.zeros(shape=(8, 6), dtype=np.int8)
        nodes = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 6, 0, 0], [0, 0, 3, 0, 0, 0], [0, 5, 0, 4, 0, 0], [0, 0, 0, 0, 0, 9],
                 [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0], [0, 0, 0, 8, 0, 0]]
        for i, n in enumerate(nodes):
            correct_matrix[i] = n

        m, lookup = lib.build_trie(vocab_list)
        assert np.array_equal(m, correct_matrix)

    def test_is_terminal(self):
        correct_matrix = np.zeros(shape=(8, 6), dtype=np.int8)
        nodes = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 6, 0, 0], [0, 0, 3, 0, 0, 0], [0, 5, 0, 4, 0, 0], [0, 0, 0, 0, 0, 9],
                 [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0], [0, 0, 0, 8, 0, 0]]
        for i, n in enumerate(nodes):
            correct_matrix[i] = n
        assert lib.is_terminal(correct_matrix, 5)

    def test_parent(self):
        correct_matrix = np.zeros(shape=(8, 6), dtype=np.int8)
        nodes = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 6, 0, 0], [0, 0, 3, 0, 0, 0], [0, 5, 0, 4, 0, 0], [0, 0, 0, 0, 0, 9],
                 [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0], [0, 0, 0, 8, 0, 0]]
        for i, n in enumerate(nodes):
            correct_matrix[i] = n
        assert lib.parent(5 == 3)

    def test_depth(self):
        correct_matrix = np.zeros(shape=(8, 6), dtype=np.int8)
        nodes = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 6, 0, 0], [0, 0, 3, 0, 0, 0], [0, 5, 0, 4, 0, 0], [0, 0, 0, 0, 0, 9],
                 [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0], [0, 0, 0, 8, 0, 0]]
        for i, n in enumerate(nodes):
            correct_matrix[i] = n
        assert lib.depth(correct_matrix, 5) == 4

    def test_symbol(self):
        vocab_list = ["caro", "cara", "codo", "caros"]
        m, lookup = lib.build_trie(vocab_list)
        assert(lib.symbol(m, lookup, 1) == "c")

    # Test relative to calcutating distance between sequences
    def test_hamming(self):
        chain1 = "AACBDCE"
        chain2 = "ACBBBCF"
        correct_distance = 4
        obtained_distance = lib.hamming(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_levenshtein(self):
        chain1 = "AACBDCEF"
        chain2 = "ACBBBCFE"
        correct_distance = 5
        obtained_distance = lib.levenshtein(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_damerau_levenshtein(self):
        chain1 = "AACBDCEF"
        chain2 = "ACBBBCFE"
        correct_distance = 4
        obtained_distance = lib.damerau_levenshtein(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_levenshtein_dynamic(self):
        vocab_list = ["caro", "cara", "codo", "caros"]
        m, lookup, node_dict = lib.build_trie(vocab_list)
        res = lib.levenshtein_dynamic("cara", m, lookup, node_dict)
        # check that "cara" has not distance with itself
        assert list(res[8]) == [4, 0, 0, 0, 0]


