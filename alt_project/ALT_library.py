# author: Martín Quesada Zaragoza

import re
import numpy as np

tokenize_re = re.compile(r'\W+')


def clean_text(text):
    return tokenize_re.sub(' ', text).lower()


def vocab_from_file(filename):
    vocab = {}
    with open(filename, mode='r') as f:
        for line in f:
            for word in clean_text(line).split():
                vocab[word] = vocab.get(word, 0) + 1

    vocab_list = [k for k, v in vocab.items() if v > 0]
    return vocab_list


def vocab_from_clean_text(clean_text):
    vocab = {}
    for word in clean_text.split():
        vocab[word] = vocab.get(word, 0) + 1
    vocab_list = [k for k, v in vocab.items() if v > 0]
    return vocab_list


def build_trie(vocab):
    alphabet = {}
    # construimos un diccionario de referencia columna - símbolo
    lookup = {}
    # diccionario de correspondencia nodo - (prefijo/palabra, terminal)
    node_dict = {}
    for w in vocab:
        for let in w:
            alphabet[let] = alphabet.get(let, 0) + 1
    for i, (k, v) in enumerate(alphabet.items()):
        lookup[k] = i

    # obtenemos el máximo número de nodos posible a partir de la talla del vocabulario
    max_nodes = sum([len(word) for word in vocab])

    # iniciamos la matriz a 1/2 de la cantidad máxima posible de nodos
    m = np.zeros(dtype=np.int64, shape=(int(max_nodes/2), len(alphabet)))
    deepest_node = 0
    node_dict = {0: {'prefix': "", 'terminal': False}}
    for word in vocab:
        current_node = 0
        for i, let in enumerate(word):
            try:
                next_node = m[current_node][lookup[let]]
            except IndexError:
                # añade nuevos modos hasta que se cumplen los requerimientos de tamaño
                while m.shape[0] <= current_node:
                    z = np.zeros(dtype=np.int64, shape=(1, len(alphabet)))
                    m = np.concatenate((m, z), axis=0)
                next_node = m[current_node][lookup[let]]
            if next_node == 0:
                deepest_node += 1
                m[current_node][lookup[let]] = deepest_node
                if i == len(word) - 1:
                    node_dict[deepest_node] = {'prefix': word[:i+1], 'terminal': True}
                else:
                    node_dict[deepest_node] = {'prefix': word[:i+1], 'terminal': False}
            current_node = m[current_node][lookup[let]]
            if i == len(word) - 1:
                node_dict[current_node] = {'prefix': word[:i + 1], 'terminal': True}
    return m, lookup, node_dict


def is_terminal(node_dict, node):
    return node_dict[node]['terminal']


def find_word(matrix, lookup, word):
    current_node = 0
    for i, let in enumerate(word):
        current_node = matrix[current_node][lookup[let]]
    return current_node


def parent(matrix, lookup, node_dict, node):
    node_prefix = node_dict[node]['prefix'][:-1]
    current_node = 0
    for i, let in enumerate(node_prefix):
        current_node = matrix[current_node][lookup[let]]
    return current_node


def depth(node_dict, node):
    node_word = node_dict[node]['prefix']
    return len(node_word)


def symbol(matrix, lookup, node_dict, node):
    p = matrix[parent(matrix, lookup, node_dict, node)]
    for i, child in enumerate(p):
        if child == node:
            for k, v in lookup.items():
                if v == i:
                    return k


def hamming(seq1, seq2):
    if len(list(seq1)) != len(list(seq2)):
        return -1
    distance = 0
    for w1, w2 in zip(seq1, seq2):
        if w1 != w2:
            distance += 1
    return distance


def levenshtein(seq1, seq2):
    L = np.zeros(dtype=np.int64, shape=(len(seq1) + 1, len(seq2) + 1))
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
    L = np.zeros(dtype=np.int64, shape=(len(seq1) + 1, len(seq2) + 1))
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


def levenshtein_dynamic(seq, trie, lookup, node_dict, threshold):
    # iniciamos la matriz de programación dinámica
    D = np.zeros(dtype=np.int32, shape=(len(node_dict) , len(seq) + 1))
    for i, cell in enumerate(D[0]):
        D[0, i] = i
    for n, node in enumerate(D[1:], start=1):
        D[n, 0] = depth(node_dict, n)
        for i, let in enumerate(node[1:], start=1):
            D[n, i] = min(D[n, i - 1] + 1,
                          D[parent(trie, lookup, node_dict, n), i] + 1,
                          D[parent(trie, lookup, node_dict, n), i-1] + (seq[i - 1] != symbol(trie, lookup, node_dict, n)))
    results = []
    for n, node in enumerate(D):
        dst = D[n][-1]
        if is_terminal(node_dict, n) and dst <= threshold:
            results.append((node_dict[n]['prefix'], dst))
    return results

def damerau_levenshtein_dynamic(seq, trie, lookup, node_dict, threshold):
    # iniciamos la matriz de programación dinámica
    D = np.zeros(dtype=np.int32, shape=(len(node_dict) , len(seq) + 1))
    for i, cell in enumerate(D[0]):
        D[0, i] = i
    D[1, 0] = depth(node_dict, 1)
    for i, cell in enumerate(D[1][1:], start=1):
        D[1, i] = min(D[1, i - 1] + 1,
                      D[parent(trie, lookup, node_dict, 1), i] + 1,
                      D[parent(trie, lookup, node_dict, 1), i-1] + (seq[i - 1] != symbol(trie, lookup, node_dict, 1)))
    for n, node in enumerate(D[2:], start=2):
        D[n, 0] = depth(node_dict, n)
        D[n, 1] = min(D[n, 1 - 1] + 1,
                      D[parent(trie, lookup, node_dict, n), 1] + 1,
                      D[parent(trie, lookup, node_dict, n), 1-1] + (seq[1 - 1] != symbol(trie, lookup, node_dict, n)))
        for i, let in enumerate(node[2:], start=2):
            D[n, i] = min(D[n, i - 1] + 1,
                          D[parent(trie, lookup, node_dict, n), i] + 1,
                          D[parent(trie, lookup, node_dict, n), i-1] + (seq[i - 1] != symbol(trie, lookup, node_dict, n)),
                          D[parent(trie, lookup, node_dict, parent(trie, lookup, node_dict, n)), i-2] + 1
                          if seq[i - 1] == symbol(trie, lookup, node_dict, parent(trie, lookup, node_dict, n)) and
                             seq[i - 2] == symbol(trie, lookup, node_dict, n)
                          else float('inf'))
    results = []
    for n, node in enumerate(D):
        dst = D[n][-1]
        if is_terminal(node_dict, n) and dst <= threshold:
            results.append((node_dict[n]['prefix'], dst))
    return results


def levenshtein_branchbound(seq, trie, lookup, node_dict, threshold=float('inf')):
    # iniciamos los estados activos y los estados finales, así como un diccionario para guardar las mejores distancias
    best_distances = {}
    states = []
    terminal_states = set()
    word_len = len(seq)
    # establecemos el estado inicial, en la posición 0, 0 de la matriz de comparación de cadenas que representan los estados
    initial_state = (0, 0)
    states.append(initial_state)
    best_distances[initial_state] = 0

    def insert_state(n, i, d, S):
        if d <= threshold and d < best_distances.get((n, i), float('inf')):
            best_distances[(n, i)] = d
            if (n, i) not in states:
                S.append((n, i))

    def is_complete(n, i):
        return is_terminal(node_dict, n) and word_len == i

    while states:
        (n, i) = states.pop(0)
        d = best_distances[(n, i)]
        # si nos encontramos en un nodo terminal del trie y no se puede seguir recorriendo la palabra, el estado es final
        if is_complete(n, i):
            terminal_states.add(n)
        # si se puede seguir recorriendo la palabra, ramificamos el estado
        if i < word_len:
            insert_state(n, i + 1, d + 1, states)
        for child_node in trie[n]:
            if child_node != 0:
                insert_state(child_node, i, d + 1, states)
                if i < word_len:
                    weight = 0 if seq[i] == symbol(trie, lookup, node_dict, child_node) else 1
                    insert_state(child_node, i + 1, d + weight, states)
    return [(node_dict[n]['prefix'], best_distances[(n, word_len)]) for n in terminal_states]


def damerau_levenshtein_branchbound(seq, trie, lookup, node_dict, threshold=float('inf')):
    # iniciamos los estados activos y los estados finales, así como un diccionario para guardar las mejores distancias
    best_distances = {}
    states = []
    terminal_states = set()
    word_len = len(seq)
    # establecemos el estado inicial, en la posición 0, 0 de la matriz de comparación de cadenas que representan los estados
    initial_state = (0, 0)
    states.append(initial_state)
    best_distances[initial_state] = 0

    def insert_state(n, i, d, S):
        if d <= threshold and d < best_distances.get((n, i), float('inf')):
            best_distances[(n, i)] = d
            if (n, i) not in states:
                S.append((n, i))

    def is_complete(n, i):
        return is_terminal(node_dict, n) and word_len == i

    while states:
        (n, i) = states.pop(0)
        d = best_distances[(n, i)]
        # si nos encontramos en un nodo terminal del trie y no se puede seguir recorriendo la palabra, el estado es final
        if is_complete(n, i):
            terminal_states.add(n)
        # si se puede seguir recorriendo la palabra, ramificamos el estado
        if i < word_len:
            insert_state(n, i + 1, d + 1, states)
        for child_node in trie[n]:
            if child_node != 0:
                insert_state(child_node, i, d + 1, states)
                if i < word_len:
                    weight = 0 if seq[i] == symbol(trie, lookup, node_dict, child_node) else 1
                    insert_state(child_node, i + 1, d + weight, states)
                    # en damerau, todos los nodos n > 0 and i > 0 se computan añadiendo la posibilidad de intercambiar letras
                    if n > 0 and i > 0:
                        parent_n = parent(trie, lookup, node_dict, n)
                        if seq[i] == symbol(trie, lookup, node_dict, n) \
                                and seq[i - 1] == symbol(trie, lookup, node_dict, child_node):
                            insert_state(child_node, i + 1, best_distances[(parent_n, i - 1)] + 1, states)
    return [(node_dict[n]['prefix'], best_distances[(n, word_len)]) for n in terminal_states]


