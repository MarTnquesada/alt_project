# author: Martín Quesada Zaragoza


def hamming(chain1, chain2):
    if len(list(chain1)) != len(list(chain2)):
        return -1

    distance = 0
    for w1, w2 in zip(chain1, chain2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(chain1, chain2):
    return levenshtein_base(chain1, chain2, len(chain1), len(chain2))


def levenshtein_base(chain1, chain2, pos1, pos2):
    if pos1 == 0:
        if pos2 == 0:
            return 0
        else:
            return pos2
    elif pos2 == 0:
        return pos1
    else:
        return min(levenshtein_base(chain1, chain2, pos1-1, pos2-1) + (chain1[pos1 - 1] != chain2[pos2 - 1]),
                   levenshtein_base(chain1, chain2, pos1, pos2-1) + 1,
                   levenshtein_base(chain1, chain2, pos1-1, pos2) + 1)


def damerau_levenshtein(chain1, chain2):
    return damerau_levenshtein_base(chain1, chain2, len(chain1), len(chain2))


def damerau_levenshtein_base(chain1, chain2, pos1, pos2):
    if pos1 == 0:
        if pos2 == 0:
            return 0
        else:
            return pos2
    elif pos2 == 0:
        return pos1
    elif pos1 == 1 or pos2 == 1:
        return min(levenshtein_base(chain1, chain2, pos1-1, pos2-1) + (chain1[pos1 - 1] != chain2[pos2 - 1]),
                   levenshtein_base(chain1, chain2, pos1, pos2-1) + 1,
                   levenshtein_base(chain1, chain2, pos1-1, pos2) + 1)
    else:
        return min(
            levenshtein_base(chain1, chain2, pos1 - 1, pos2 - 1) + (chain1[pos1 - 1] != chain2[pos2 - 1]),
            levenshtein_base(chain1, chain2, pos1, pos2 - 1) + 1,
            levenshtein_base(chain1, chain2, pos1 - 1, pos2) + 1,
            levenshtein_base(chain1, chain2, pos1 - 2, pos2 - 2) + 1
            if chain1[pos1 - 1] == chain2[pos2 - 2] and chain1[pos1 - 2] == chain2[pos2 - 1] else float('inf'))
