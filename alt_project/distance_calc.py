


def hamming(chain1, chain2):
    if len(list(chain1)) != len(list(chain2)):
        return -1

    distance = 0
    for w1, w2 in zip(chain1, chain2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(chain1, chain2, threshold):
    distance = 0



def damerau_levenshtein(chain1, chain2, threshold):
    pass