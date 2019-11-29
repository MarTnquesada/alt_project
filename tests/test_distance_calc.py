# authors: Martín Quesada Zaragoza

from alt_project import distance_calc
from alt_project.vocab_trie import build_trie


class TestDistanceCalc:

    def test_hamming(self):
        chain1 = "AACBDCE"
        chain2 = "ACBBBCF"
        correct_distance = 4
        obtained_distance = distance_calc.hamming(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_levenshtein(self):
        chain1 = "AACBDCEF"
        chain2 = "ACBBBCFE"
        correct_distance = 5
        obtained_distance = distance_calc.levenshtein(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_damerau_levenshtein(self):
        chain1 = "AACBDCEF"
        chain2 = "ACBBBCFE"
        correct_distance = 4
        obtained_distance = distance_calc.damerau_levenshtein(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_levenshtein_dynamic(self):
        vocab_list = ["caro", "cara", "codo", "caros"]
        m, lookup = build_trie(vocab_list)
        res = distance_calc.levenshtein_dynamic("cara", m, lookup)
        # check that "cara" has not distance with itself
        assert list(res[8]) == [4, 0, 0, 0, 0]

