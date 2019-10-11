# authors: Martín Quesada Zaragoza

import numpy as np
from alt_project import vocab_trie


class TestDistanceCalc:

    def test_build_trie(self):
        vocab_list = ["caro", "cara", "codo", "caros"]
        correct_matrix = np.zeros(shape=(8, 6), dtype=np.int8)
        nodes = [[1, 0, 0, 0, 0, 0], [0, 2, 0, 6, 0, 0], [0, 0, 3, 0, 0, 0], [0, 5, 0, 4, 0, 0], [0, 0, 0, 0, 0, 9],
             [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 7, 0], [0, 0, 0, 8, 0, 0]]
        for i, n in enumerate(nodes):
            correct_matrix[i] = n

        m, lookup = vocab_trie.build_trie(vocab_list)
        assert np.array_equal(m, correct_matrix)
