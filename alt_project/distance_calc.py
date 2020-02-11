# author: Martín Quesada Zaragoza

import argparse
import pickle
from time import time  # funciona bien en linux / max, usar time.clock() en windows
from alt_project.ALT_library import find_word, is_terminal, levenshtein, damerau_levenshtein, levenshtein_dynamic, \
    damerau_levenshtein_dynamic, levenshtein_branchbound, damerau_levenshtein_branchbound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vocab', required=True,
                        help='Path al archivo pickle file donde está la lista del vocabulario')
    parser.add_argument('--trie', required=True,
                        help='Path al archivo pickle file donde está el trie del vocabulario')
    parser.add_argument('--word', required=True, help='Palabra a comparar')
    parser.add_argument('--levenshtein', default=True, action='store_true')
    parser.add_argument('--damerau_levenshtein', default=True)
    parser.add_argument('--levenshtein_dynamic', default=True)
    parser.add_argument('--damerau_levenshtein_dynamic', default=True)
    parser.add_argument('--levenshtein_branchbound', default=True)
    parser.add_argument('--damerau_levenshtein_branchbound', default=True)
    parser.add_argument('--threshold', default=1, type=int)
    args = parser.parse_args()

    with open(args.vocab, 'rb') as fh:
        vocab_list = pickle.load(fh)
        print("TAMAÑO DEL VOCABULARIO GLOBAL: " + str(len(vocab_list)) + "\n")
        if args.levenshtein:
            print("LEVENSHTEIN DISTANCE CALC FOR WORD " + args.word)
            start = time()
            found = []
            for word in vocab_list:
                dst = levenshtein(args.word, word)
                if dst <= args.threshold:
                    found.append((word, dst))
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

        if args.damerau_levenshtein:
            print("\nDAMERAU-LEVENSHTEIN DISTANCE CALC FOR WORD " + args.word)
            start = time()
            found = []
            for word in vocab_list:
                dst = damerau_levenshtein(args.word, word)
                if dst <= args.threshold:
                    found.append((word, dst))
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

    with open(args.trie, 'rb') as fh:
        # las medidas de tiempo para funciones con trie no cuentan el tiempo de carga del trie
        trie, lookup, node_dict = pickle.load(fh)

        if args.levenshtein_dynamic:
            print("\nLEVENSHTEIN DYNAMIC DISTANCE CALC FOR WORD " + args.word)
            start = time()
            found = levenshtein_dynamic(args.word, trie, lookup, node_dict, threshold=args.threshold)
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

        if args.damerau_levenshtein_dynamic:
            print("\nDAMERAU-LEVENSHTEIN DYNAMIC DISTANCE CALC FOR WORD " + args.word)
            start = time()
            found = damerau_levenshtein_dynamic(args.word, trie, lookup, node_dict, threshold=args.threshold)
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

        if args.levenshtein_branchbound:
            print("\nLEVENSHTEIN BRANCH BOUND CALC FOR WORD " + args.word)
            start = time()
            found = levenshtein_branchbound(args.word, trie, lookup, node_dict, args.threshold)
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")

        if args.levenshtein_branchbound:
            print("\nDAMERAU-LEVENSHTEIN BRANCH BOUND CALC FOR WORD " + args.word)
            start = time()
            found = damerau_levenshtein_branchbound(args.word, trie, lookup, node_dict, args.threshold)
            end = time()
            elapsed = end - start
            print(f"Time elapsed {elapsed} seconds")
            print(args.word + "\t" + str(args.threshold) + "\t" + str(len(found)) + "\t", end="")
            for word, dst in found:
                print(str(dst) + ":" + word, end="  ")


if __name__ == '__main__':
    main()
