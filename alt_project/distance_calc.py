
def hamming(chain1, chain2):
    if len(list(chain1)) != len(list(chain2)):
        return -1

    distance = 0
    for w1, w2 in zip(chain1, chain2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(chain1, chain2, threshold):
    return levenshtein_base(chain1,chain2, threshold, 0, 0)


def levenshtein_base(chain1, chain2, threshold, pos1, pos2):
    if pos1 == 0:
        if pos2 == 0:
            return 0
        else:
            return levenshtein_base(chain1, chain2, pos1, pos2-1) + 1
    elif pos2 == 0:
        return levenshtein_base(chain1, chain2, pos1-1, pos2) + 1
    else:
        return min(levenshtein_base(chain1, chain2, pos1-1, pos2-1),
                   levenshtein_base(chain1, chain2, pos1, pos2-1),
                   levenshtein_base(chain1, chain2, pos1-1, pos2)) 
                   + 1


def damerau_levenshtein(chain1, chain2, threshold):
    pass