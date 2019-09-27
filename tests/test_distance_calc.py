from alt_project.distance_calc import levenshtein, damerau_levenshtein


def class TestDistanceCalc():

    def test_levenshtein(self):
        chain1 = "AACBDCE"
        chain2 = "ACBBBCF"
        correct_distance = 4
        obtained_distance = hamming(chain1, chain2)
        assert correct_distance == obtained_distance

    def test_levenshtein(self):
        chain1 = "AACBDC"
        chain2 = "ACBBBC"
        correct_distance = 3
        obtained_distance = levenshtein(chain1, chain2, 10)
        assert correct_distance == obtained_distance


    def test_damerau_levenshtein(self):
        pass