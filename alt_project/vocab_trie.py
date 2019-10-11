from alt_project.indexer import clean_text, save_object
import argparse
import numpy as np


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
    m = np.zeros(dtype=np.int8, shape=(int(6), len(alphabet)))
    deepest_node = 0
    for word in vocab:
        current_node = 0
        for let in word:
            try:
                next_node = m[current_node][lookup[let]]
            except IndexError:
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src')
    parser.add_argument('--vocab')
    parser.add_argument('--trie')
    args = parser.parse_args()

    vocab_list = ["caro", "cara", "codo", "caros"]
    print(build_trie(vocab_list))


if __name__ == '__main__':
    main()
