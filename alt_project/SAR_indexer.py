# author: Martín Quesada Zaragoza

import os
import sys
import json
import re
import pickle
from nltk.stem import SnowballStemmer
from ALT_library import vocab_from_clean_text, build_trie

stemmer = SnowballStemmer('spanish')
tokenize_re = re.compile(r'\W+')


def clean_text(text):
    return tokenize_re.sub(' ', text).lower()


def save_object(data, filename):
    with open(filename, 'wb') as fh:
        pickle.dump(data, fh)


def load_jason(filename):
    with open(filename) as fh:
        obj = json.load(fh)
    return obj


def list_permuterm(word):
    """
    Creates a permuterm list from a given word
    :param str word:
    :return: permuterm list of the given word
    :rtype: list
    """
    word = word + '$'
    res = []
    for i, letter in enumerate(word):
        word = word[1:] + word[0]
        res.append(word)
    return res


def new_index(doc_dir, index_dir):
    '''
    Genera un nuevo índice en index_dir a partir de las noticias contenidas en el directorio doc_dir
    '''
    n_arts = 0
    n_docs = 0
    #Extensión de queries con *
    #term_docID_ap_list = lista de tuplas [termino, docID, apariciones]
    #term_docID_ap_list = lista de tuplas [termino, docID, apariciones]dic_term_docID_ap_list = {}
    perm_rotations = [] 
    perm_rotations_keywords = [] 
    perm_rotations_date = []
    perm_rotations_title = []
    perm_rotations_sum = [] 
    art_index = {}
    inv_index = {}
    title_index = {}
    summary_index = {}
    keywords_index = {}
    date_index = {}
    global_vocab = set()
    print('\nCreando diccionarios...')
    for dirname, subdirs, docs in os.walk(doc_dir):
        for doc in docs:
            fullname = os.path.join(dirname, doc)
            obj = load_jason(fullname)
            for i, article in enumerate(obj):
                art_index[n_arts]=(n_docs,i) #i = posicion del articulo en el documento
                c_text = clean_text(article['article'].lower())
                # obtain a vocabulary from the newly opened article, keeping the union of this vocab and the global one
                local_vocab = vocab_from_clean_text(c_text)
                global_vocab = global_vocab.union(set(local_vocab))
                for word in c_text.split():    
                    if n_arts not in inv_index.get(word, []):
                        inv_index.setdefault(word, []).append(n_arts)
                c_title = clean_text(article['title'].lower())
                for word in c_title.split():
                    if n_arts not in title_index.get(word, []):
                        title_index.setdefault(word, []).append(n_arts) 
                c_summary = clean_text(article['summary'].lower())  
                for word in c_summary.split():
                    if n_arts not in summary_index.get(word, []):
                        summary_index.setdefault(word, []).append(n_arts)  
                c_keywords = clean_text(article['keywords'].lower()) 
                for word in c_keywords.split():
                    if n_arts not in keywords_index.get(word, []):
                        keywords_index.setdefault(word, []).append(n_arts)  
                c_date = article['date'] 
                for word in c_date.split():
                    if n_arts not in date_index.get(word, []):
                        date_index.setdefault(word, []).append(n_arts)  
                n_arts+=1
                    
            n_docs+=1
    print('Diccionarios creados')
    print('Creando Trie con el vocabulario global')
    # trie_struct = (trie, lookup, node_dict)
    trie, lookup, node_dict  = build_trie(list(global_vocab))
    print('Trie creado')
    print('Creando listas permuterm...')
    #creando la lista permuterm del cuerpo de los artículos
    for key, value in inv_index.items():
        list_perm = list_permuterm(key)
        perm_rotations = perm_rotations + list_perm
    #creando la lista permuterm del título
    for key, value in title_index.items():
        list_perm = list_permuterm(key)
        perm_rotations_title = perm_rotations_title + list_perm
    #creando la lista permuterm del resumen de los artículos
    for key, value in summary_index.items():
        list_perm = list_permuterm(key)
        perm_rotations_sum = perm_rotations_sum + list_perm
    #creando la lista permuterm de las palabras clave
    for key, value in keywords_index.items():
        list_perm = list_permuterm(key)
        perm_rotations_keywords = perm_rotations_keywords + list_perm
    #creando la lista permuterm de las fechas
    for key, value in date_index.items():
        list_perm = list_permuterm(key)
        perm_rotations_date = perm_rotations_date + list_perm
    print('Listas permuterm creadas')
    print('Ordenando listas permuterm...')
    #Ordenar la lista de rotaciones
    perm_rotations = sorted(perm_rotations)
    perm_rotations_sum = sorted(perm_rotations_sum)
    perm_rotations_title = sorted(perm_rotations_title)
    perm_rotations_keywords = sorted(perm_rotations_keywords)
    perm_rotations_date = sorted(perm_rotations_date)
    print('Listas permuterm ordenadas\n')
    stem_index = {}
    for key, value in inv_index.items():
        stem_index.setdefault(stemmer.stem(key), []).append(key)
    dicts=[doc_dir, art_index, inv_index, title_index, summary_index, keywords_index, date_index, stem_index,
           perm_rotations, perm_rotations_keywords, perm_rotations_date, perm_rotations_title, perm_rotations_sum,
           n_arts, (trie, lookup, node_dict)]
    save_object(dicts, index_dir)

    print('\nÍndice creado satisfactoriamente')
    print('Número de días del corpus ' + str(n_docs))
    print('Número de noticias: ' + str(n_arts))
    print('Número de términos en el título de las noticias(title) ' + str(len(title_index)))
    print('Número de términos en la fecha de las noticias(date) ' + str(len(date_index)))
    print('Número de términos en las palabras clave de las noticias(keywords) ' + str(len(keywords_index)))
    print('Número total de términos en el cuerpo de las noticias(article) ' + str(len(inv_index)))
    print('Número total de términos en el resumen de las noticias(summary) ' + str(len(summary_index)))
    print('Tamaño del vocabulario global ' + str(len(global_vocab)))
    print('Número de entradas permuterm en "article" ' + str(len(perm_rotations)))
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Argumentos insuficientes')
        print('USO: SAR_indexer <documents_directory> <index_directory>')
    else:
        new_index(sys.argv[1], sys.argv[2])