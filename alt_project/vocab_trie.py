# author: Martín Quesada Zaragoza

from alt_project.indexer import clean_text, save_object
import argparse
import numpy as np
import time


def vocab_from_file(filename):
    vocab = {}
    with open(filename, mode='r') as f:
        for line in f:
            for word in clean_text(line).split():
                vocab[word] = vocab.get(word, 0) + 1

    vocab_list = [k for k, v in vocab.items() if v > 0]
    return vocab_list


def build_trie(vocab):
    # we build the lookup dictionary for letter-column correspondence
    alphabet = {}
    lookup = {}
    for w in vocab:
        for let in w:
            alphabet[let] = alphabet.get(let, 0) + 1
    for i, (k, v) in enumerate(alphabet.items()):
        lookup[k] = i

    # obtaining the maximum number of nodes from the size of the given vocabulary (worst case)
    max_nodes = sum([len(word) for word in vocab])

    # we initialize the trie matrix with 1/2 of the maximum possible number of nodes
    m = np.zeros(dtype=np.int8, shape=(int(max_nodes/2), len(alphabet)))
    deepest_node = 0
    for word in vocab:
        current_node = 0
        for let in word:
            try:
                next_node = m[current_node][lookup[let]]
            except IndexError:
                # add new nodes until meeting the latest size requirements. new nodes are not created until accessed
                while m.shape[0] <= current_node:
                    z = np.zeros(dtype=np.int8, shape=(1, len(alphabet)))
                    m = np.concatenate((m, z), axis=0)
                next_node = m[current_node][lookup[let]]
            if next_node == 0:
                deepest_node += 1
                m[current_node][lookup[let]] = deepest_node
            current_node = m[current_node][lookup[let]]

    return m, lookup


def is_terminal(matrix, node):
    return not matrix[node].any()


def parent(matrix, node):
    if node == 0 or node > len(matrix):
        return -1
    for n in reversed(range(0, node)):
        if node in matrix[n]:
            return n
    return 0


def depth(matrix, node):
    if node > len(matrix):
        return -1
    if node == 0:
        return 0
    else:
        aux_node = node
        d = 1
        while parent(matrix, aux_node) != 0:
            d += 1
            aux_node = parent(matrix, aux_node)
        return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', help='Source plain text file')
    parser.add_argument('--vocab', help='Name of the pickle file containing the vocabulary as a list')
    parser.add_argument('--trie', help='Name of the pickle file containing the tuple (trie, lookup)')
    args = parser.parse_args()

    start_time = time.time()
    vocab_list = vocab_from_file(args.src)
    print("Created vocabulary list, time elapsed: " + str(time.time()-start_time))

    start_time = time.time()
    trie, lookup = build_trie(vocab_list)
    print("Created trie, time elapsed: " + str(time.time()-start_time))

    # saving the vocab_list pickle file
    save_object(vocab_list, args.vocab)
    # saving the trie pickle file
    save_object((trie, lookup), args.trie)


if __name__ == '__main__':
    main()
