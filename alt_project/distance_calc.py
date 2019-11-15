# author: Martín Quesada Zaragoza

import argparse
import pickle
import numpy as np

def hamming(seq1, seq2):
    if len(list(seq1)) != len(list(seq2)):
        return -1
    distance = 0
    for w1, w2 in zip(seq1, seq2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(seq1, seq2):
    L = np.zeros(dtype=np.int8, shape=(len(seq1) + 1, len(seq2) + 1))
    for i, cell in enumerate(L[0]):
        L[0, i] = i
    for pos1, row in enumerate(L[1:], start=1):
        L[pos1, 0] = pos1
        for pos2, cell in enumerate(row[1:], start=1):
            L[pos1, pos2] = min(L[pos1 - 1, pos2 - 1] + (seq1[pos1 - 1] != seq2[pos2 - 1]),
                                L[pos1, pos2 - 1] + 1,
                                L[pos1 - 1, pos2] + 1)
    return L[len(seq1)][len(seq2)]


def damerau_levenshtein(seq1, seq2):
    L = np.zeros(dtype=np.int8, shape=(len(seq1) + 1, len(seq2) + 1))
    for i, cell in enumerate(L[0]):
        L[0, i] = i
    for i, cell in enumerate(L[1]):
        L[1, i] = min(L[1 - 1, i - 1] + (seq1[1 - 1] != seq2[i - 1]),
                                L[1, i - 1] + 1,
                                L[1 - 1, i] + 1)
    for pos1, row in enumerate(L[2:], start=2):
        L[pos1, 0] = pos1
        L[pos1, 1] = min(L[pos1 - 1, 1 - 1] + (seq1[pos1 - 1] != seq2[1 - 1]),
                                L[pos1, 1 - 1] + 1,
                                L[pos1 - 1, 1] + 1)
        for pos2, cell in enumerate(row[2:], start=2):
            L[pos1, pos2] = min(L[pos1 - 1, pos2 - 1] + (seq1[pos1 - 1] != seq2[pos2 - 1]),
                                L[pos1, pos2 - 1] + 1,
                                L[pos1 - 1, pos2] + 1,
                                L[pos1 - 2, pos2 - 2] + 1
                                if seq1[pos1 - 1] == seq2[pos2 - 2] and seq1[pos1 - 2] == seq2[pos2 - 1]
                                else float('inf'))
    return L[len(seq1)][len(seq2)]


def levenshtein_dynamic(seq, trie, lookup):
    # TODO dont do this recursively you son of a, dynamic programming
    D = []
    for i in reversed(seq):
        pass
    pass


def levenshtein_branch_bound():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vocab', required=True, help='Path of the pickle file where the vocabulary list is contained')
    parser.add_argument('--word', required=True, help='Word to compare with the given dictionary')
    parser.add_argument('--levenshtein', default=True)
    parser.add_argument('--damerau_levenshtein', default=True)
    parser.add_argument('--threshold', default=1, type=int)
    args = parser.parse_args()

    with open(args.vocab, 'rb') as fh:
        vocab_list = pickle.load(fh)

        if args.levenshtein:
            print("LEVENSHTEIN DISTANCE CALC FOR WORD " + args.word)
            found = []
            for word in vocab_list:
                dst = levenshtein(args.word, word)
                if dst <= args.threshold:
                    found.append((word, dst))
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

        if args.damerau_levenshtein:
            print("\nDAMERAU-LEVENSHTEIN DISTANCE CALC FOR WORD " + args.word)
            found = []
            for word in vocab_list:
                dst = damerau_levenshtein(args.word, word)
                if dst <= args.threshold:
                    found.append((word, dst))
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")


if __name__ == '__main__':
    main()