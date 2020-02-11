# author: Martín Quesada Zaragoza

import argparse
from time import time  # works fine on linux / max, use time.clock() in windows
from alt_project.ALT_library import vocab_from_file, build_trie
from alt_project.SAR_indexer import save_object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', help='Source plain text file')
    parser.add_argument('--vocab', help='Name of the pickle file containing the vocabulary as a list')
    parser.add_argument('--trie', help='Name of the pickle file containing the tuple (trie, lookup)')
    args = parser.parse_args()

    start_time = time()
    vocab_list = vocab_from_file(args.src)
    print("Created vocabulary list, time elapsed: " + str(time()-start_time))

    start_time = time()
    trie, lookup, node_dict = build_trie(vocab_list)
    print("Created trie, time elapsed: " + str(time()-start_time))

    # saving the vocab_list pickle file
    save_object(vocab_list, args.vocab)
    # saving the trie pickle file
    save_object((trie, lookup, node_dict), args.trie)


if __name__ == '__main__':
    main()
