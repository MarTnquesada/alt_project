# author: Martín Quesada Zaragoza

import argparse
import pickle


def hamming(seq1, seq2):
    if len(list(seq1)) != len(list(seq2)):
        return -1
    distance = 0
    for w1, w2 in zip(seq1, seq2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(seq1, seq2):
    return levenshtein_base(seq1, seq2, len(seq1), len(seq2))


def levenshtein_base(seq1, seq2, pos1, pos2):
    if pos1 == 0:
        if pos2 == 0:
            return 0
        else:
            return pos2
    elif pos2 == 0:
        return pos1
    else:
        return min(levenshtein_base(seq1, seq2, pos1 - 1, pos2 - 1) + (seq1[pos1 - 1] != seq2[pos2 - 1]),
                   levenshtein_base(seq1, seq2, pos1, pos2 - 1) + 1,
                   levenshtein_base(seq1, seq2, pos1 - 1, pos2) + 1)


def damerau_levenshtein(seq1, seq2):
    return damerau_levenshtein_base(seq1, seq2, len(seq1), len(seq2))


def damerau_levenshtein_base(seq1, seq2, pos1, pos2):
    if pos1 == 0:
        if pos2 == 0:
            return 0
        else:
            return pos2
    elif pos2 == 0:
        return pos1
    elif pos1 == 1 or pos2 == 1:
        return min(levenshtein_base(seq1, seq2, pos1 - 1, pos2 - 1) + (seq1[pos1 - 1] != seq2[pos2 - 1]),
                   levenshtein_base(seq1, seq2, pos1, pos2 - 1) + 1,
                   levenshtein_base(seq1, seq2, pos1 - 1, pos2) + 1)
    else:
        return min(
            levenshtein_base(seq1, seq2, pos1 - 1, pos2 - 1) + (seq1[pos1 - 1] != seq2[pos2 - 1]),
            levenshtein_base(seq1, seq2, pos1, pos2 - 1) + 1,
            levenshtein_base(seq1, seq2, pos1 - 1, pos2) + 1,
            levenshtein_base(seq1, seq2, pos1 - 2, pos2 - 2) + 1
            if seq1[pos1 - 1] == seq2[pos2 - 2] and seq1[pos1 - 2] == seq2[pos2 - 1] else float('inf'))


def levenshtein_dynamic(seq, trie, lookup):
    pass


def levenshtein_branch_bound():
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vocab', required=True, help='Path of the pickle file where the vocabulary list is contained')
    parser.add_argument('--word', required=True, help='Word to compare with the given dictionary')
    parser.add_argument('--levenshtein', default=True)
    parser.add_argument('--damerau_levenshtein', default=True)
    parser.add_argument('--threshold', default=1)
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