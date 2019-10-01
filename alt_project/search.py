# authors: David Ferrer Pérez, Martín Quesada Zaragoza, Javier Francés Martínez

import os
import sys
import json
import pickle
import re
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer('spanish')
clean_re = re.compile('\W+')


def clean_text(text):
    return clean_re.sub(' ', text)


def load_index(filename):
    with open(filename, 'rb') as fh:
        data = pickle.load(fh)
    return data


def load_jason(filename):
    with open(filename) as fh:
        obj = json.load(fh)
    return obj


def get_doc_list(doc_dir):
    '''
    Devuelve una lista de documentos que se encuentran dentro del directorio doc_dir
    '''
    doc_list = []
    for dirname, subdirs, docs in os.walk(doc_dir):
        for doc in docs:
            #guarda los caminos completos a cada documento en el mismo orden que art_index (corresponde a cada entero secuencial identificador)
            doc_list.append(os.path.join(dirname, doc))
    return doc_list


def post_negated(post, n_arts):
    '''
    Devuelve los artículos que no se encuentran en la posting list post
    '''
    post_negated = [i for i in range(n_arts) if i not in post]
    return post_negated


def post_intersection(post1, post2):
    inter_post = []
    i=j=0
    while i < len(post1) and j < len(post2):
        if post1[i] == post2[j]:
            inter_post.append(post1[i])
            i += 1
            j += 1
        else:
            if post1[i] < post2[j]:
                i += 1
            else:
                j += 1
    return inter_post


def post_union(post1, post2):
    '''
    Devuelve la unión entre las dos posting list dadas
    '''
    uni_post = []
    i=j=0
    while i < len(post1) and j < len(post2):
        if post1[i] == post2[j]:
            uni_post.append(post1[i])
            i += 1
            j += 1
        else:
            if post1[i] < post2[j]:
                uni_post.append(post1[i])
                i += 1
            else:
                uni_post.append(post2[j])
                j += 1
    while i < len(post1):
        uni_post.append(post1[i]) 
        i += 1  
    while j < len(post2):
        uni_post.append(post2[j]) 
        j += 1 
    return uni_post


def term_permuterm(word):
    '''
    Saca el mecanismo de busqueda de una wildcard query.
    '''
    if '*' not in word:
        return word + '$'
    elif word[0] == '*' and word[len(word)-1] == '*':
        return word[1:]
    elif word[0] == '*':
        return word[1:] + '$*'
    elif word[len(word)-1] == '*':
        return '$' + word
    else:
        x1 = word.split('*')[0]
        x2 = word.split('*')[1]
        return x2 + '$' + x1 + '*'


def list_term_perm(word, indice):
    '''
    Este método busca todas las rotaciones en un indice de rotaciones que tienen como prefijo word
    '''
    #Le eliminamos el * al final
    pref = word[:len(word)-1]
    #Busqueda binaria de las rotaciones
    res = binary_search(indice, pref)
    return res


def binary_search(lista, word):
    '''
    Busqueda binaria de TODAS las palabras en lista que empiezan con word.
    '''
    primero = 0
    ultimo = len(lista)-1
    found = False
    #Hacemos una busqueda binaria para encontrar la posción de una palabra que empiece por word
    while primero <= ultimo and not found:
        medio = (primero+ultimo)//2
        #print(str(primero)+ ': ' + str(lista[primero]) + '   ' + str(medio)+ ': ' + str(lista[medio]) + '   ' + str(ultimo)+ ': ' + str(lista[ultimo]))
        if lista[medio].startswith(word):
            found = True
        else:
            if word < str(lista[medio]):
                ultimo = medio-1
            else:
                primero = medio+1
    res = []
    if found:
        #Buscamos todas las palabras que empiecen por word a la izquierda y a la derecha
        #IZQUIERDA:
        finish = False
        pos = medio
        while not finish and pos >= 0:
            aux = lista[pos]
            if aux.startswith(word):
                res.append(aux)
            elif not aux.startswith(word): #Si encontramos una palabra que no empieza por word, dejamos de buscar
                finish = True
            pos = pos -1
        #DERECHA:
        finish = False
        pos = medio + 1
        while not finish and pos < len(lista):
            aux = lista[pos]
            if aux.startswith(word):
                res.append(aux)
            elif not aux.startswith(word): #Si encontramos una palabra que no empieza por word, dejamos de buscar
                finish = True
            pos = pos +1

    return res


def original_terms(lista):
    '''
    A partir de una lista de rotaciones de palabras, saca las palabras originales.
    '''
    res = []
    for term in lista:
        x1 = term.split('$')[0]
        x2 = term.split('$')[1]
        aux = x2 + x1
        res.append(aux)
    return res


def make_query(clean_q, article_index, inverted_index, title_index, summary_index, keywords_index, date_index, stem_index, stemming, perm_rotations, perm_rotations_keywords, perm_rotations_date, perm_rotations_title, perm_rotations_sum, n_docs):
    '''
    Realiza una query sobre el índice dado y devuelve una posting list final como resultado
    '''
    term_list = []
    last = ''
    #lista que acumula la sección ya resuelta de la consulta 
    tail = []
    actual_dict = inverted_index
    actual_word = ''
    i = 0
    #recorrer la consulta término a término, resolviéndola de izquierda a derecha article_index,
    while i < len(clean_q):
        word = clean_q[i]

        #en caso de encontrar el comienzo de una subquery
        if word[:1] == '(':
            #resolver subqueries entre paréntesis de forma recursiva y añadir el resultado a la cola
            j = i
            found_par = 0
            word_aux = ''
            #recorrer la consulta hasta encontrar el final de la subquery actual
            while j < len(clean_q):
                word_aux = clean_q[j]
                for let in word_aux:
                    if let == '(':
                        found_par += 1
                    elif let == ')':
                        found_par -= 1

                    if found_par == 0:
                        break
                if found_par == 0:
                    break
                j += 1
            subquery = clean_q[i:j+1]
            subquery[0] = subquery[0][1:]
            last_w = subquery[len(subquery) - 1]
            last_w_mod = last_w[:len(last_w) - 1]
            subquery[len(subquery) - 1] = last_w_mod
            #realizamos una llamada recursiva sobre la subquery encontrada
            r_subquery = make_query(subquery, article_index, inverted_index, title_index, summary_index, keywords_index, date_index, stem_index, stemming, perm_rotations, perm_rotations_keywords, perm_rotations_date, perm_rotations_title, perm_rotations_sum, n_docs)
            #procedemos de la misma forma que al encontrar un término en la consulta
            if last == 'not':
                tail[len(tail)-1] = post_negated(r_subquery, len(article_index)) 
            else:
                tail.append(r_subquery)
            #cuando la cola tiene 3 elementos, resolvemos esta sección 
            # de la consulta colocamos su posting como primer elemento de la cola    
            if len(tail) == 3:
                    if tail[1] == 'or':
                        tail = [post_union(tail[0], tail[2])]
                    elif tail[1] == 'and':
                        tail = [post_intersection(tail[0], tail[2])]
                    else:
                        print('You wrote ' + clean_q[i-1] + ', which is not a logical operator')
                        exit(1)
            i = j
        #en caso de no encontrar una subquery, resolver la consulta de forma estándar
        else:
            #si encontramos un operador lógico, añadirlo a la cola
            if word == 'not':
                tail.append('not')
                last = 'not'
            elif word == 'and':
                tail.append('and')
                last = 'and'
            elif word == 'or':
                tail.append('or')
                last = 'or'
            #en caso contrario, hemos encontrado un término
            else:
                
                #determinar en qué diccionario hemos de buscar el término
                if 'title:' in word:
                    actual_dict = title_index
                    actual_word = word.split(':')[1]
                elif 'summary:' in word:
                    actual_dict = summary_index
                    actual_word = word.split(':')[1]
                elif 'article:' in word:
                    actual_dict = inverted_index
                    actual_word = word.split(':')[1]
                elif 'keywords:' in word:
                    actual_dict = keywords_index
                    actual_word = word.split(':')[1]
                elif 'date:' in word:
                    actual_dict = date_index
                    actual_word = word.split(':')[1]
                else:
                    actual_dict = inverted_index
                    actual_word = word

                term_list.append(word)

                posting_list = []

                #Si la palabra contiene un asterisco, se trata de un término permuterm
                if('*' in word):
                    term_perm = term_permuterm(actual_word)
                    #Buscamos todas las palabras en las rotaciones que empiezan por perm_term
                    #Buscamos en la lista de rotaciones correspondiente al indice que buscamos
                    if actual_dict == inverted_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == keywords_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_keywords)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == title_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_title)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == summary_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_sum)
                        retrieved_terms = original_terms(list_rotations) 
                    elif actual_dict == date_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_date)
                        retrieved_terms = original_terms(list_rotations)
                    for rterm in retrieved_terms:
                        posting_list = post_union(posting_list, actual_dict.get(rterm, []))
                #Si la palabra contiene un ? entonces hacemos lo mismo que con el * pero descartamos 
                # las palabras que tengan una longitud diferente a word.
                elif('?' in word):
                    x1 = actual_word.split('?')[0]
                    x2 = actual_word.split('?')[1]
                    aux = x1 + '*' + x2
                    term_perm = term_permuterm(aux)
                    #Buscamos todas las palabras en las rotaciones que empiezan por perm_term
                    #Buscamos en la lista de rotaciones correspondiente al indice que buscamos
                    if actual_dict == inverted_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == keywords_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_keywords)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == title_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_title)
                        retrieved_terms = original_terms(list_rotations)
                    elif actual_dict == summary_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_sum)
                        retrieved_terms = original_terms(list_rotations) 
                    elif actual_dict == date_index:
                        list_rotations = list_term_perm(term_perm, perm_rotations_date)
                        retrieved_terms = original_terms(list_rotations)
                    for rterm in retrieved_terms:
                        if len(rterm) == len(actual_word):#Solo añadimos si las lengths son iguales
                            posting_list = post_union(posting_list, actual_dict.get(rterm, []))
                #si estamos usando stemming
                elif(stemming and actual_dict == inverted_index):
                    stem_word = stemmer.stem(word)
                    for value in stem_index.get(stem_word, []): 
                        posting_list = post_union(posting_list, actual_dict[value])
                else:
                    posting_list = actual_dict.get(actual_word, [])

                #tras añadir la posting list del término, si el último operador era 'not' la negamos
                if last == 'not':
                    tail[len(tail)-1] = post_negated(posting_list, len(article_index)) 
                else:
                    tail.append(posting_list)
                #cuando la cola tiene 3 elementos, resolvemos esta sección 
                # de la consulta colocamos su posting como primer elemento de la cola
                if len(tail) == 3:
                    if tail[1] == 'or':
                        tail = [post_union(tail[0], tail[2])]
                    elif tail[1] == 'and':
                        tail = [post_intersection(tail[0], tail[2])]
                    else:
                        print('You wrote ' + clean_q[i-1] + ', which is not a logical operator')
                        exit(1)
        i += 1
    return tail[0]


def snippet(query, rnew_article):
    '''
    Devuelve un snippet como string dados un artículo y una query
    '''
    art = clean_text(rnew_article).split()
    #obtener la query sin paréntesis y formateada como lista
    clean_q = clean_text(query).lower().split()
    #añadir todos los términos que aparecen en la query a una lista de términos
    term_list = [] 
    last = ''
    for word in clean_q:
        if word != 'not' and word != 'and' and word != 'or':
            term_list.append(word)

    #para cada palabra sacamos sus ocurrencias en la lista term_pos
    # guardamos las posiciones de cada intervalo, si dos intervalos se solapan los juntamos en uno
    # snippet: "anterior termino siguiente ... anterior termino siguiente ... anterior termino termino siguiente"
    # not termino = snippet vacio
    term_pos = []
    for term in term_list:
        for i, word in enumerate(art):
            if word.lower() == term:
                term_pos.append(i)
                break 
    #confeccionamos e article_index,es de los términos en en artículo
    snippet = ''
    for i, pos in enumerate(term_pos):
        #si estamos en la primera posición del artículo
        if pos == 0:
            #si el text tiene una longitud de una sola palabra o menos
            if len(art) < 2:
                snippet += art[pos] 
            else:
                snippet += art[pos] + ' ' + art[pos + 1] 
        #en el resto de casos comprobamos si hay solapes
        elif pos == len(art):
            #El anterior del término es el siguiente del término previo
            if pos -  term_pos[i-1] == 2:
                snippet += ' ' + art[pos] 
            else:
                snippet += '...' + art[pos - 1] + ' ' + art[pos] 
        else:
            #El anterior del término es el término previo
            if pos - term_pos[i-1] == 1:
                snippet +=  ' ' + art[pos+1] 
            #El anterior del término es el siguiente del término previo
            elif pos -  term_pos[i-1] == 2:
                snippet +=  ' ' + art[pos] +  ' ' + art[pos+1] 
            else:
                snippet += '...' + art[pos - 1] +  ' ' + art[pos] +  ' ' + art[pos + 1]
    snippet += '...'
    return snippet


def show_retrieved(rnews, art_index, doc_dir, query):
    '''
    Muestra los artículos recuperados de la posting list rnews
    '''
    num_news = len(rnews)
    print("\n------------------------------------------------------------\n")
    if num_news == 0:
        print('There are no news for that query.')
    doc_list = get_doc_list(doc_dir)

    if num_news <= 2:
        for n in rnews:
            name_doc = doc_list[art_index[n][0]] 
            doc = load_jason(name_doc)
            new = doc[art_index[n][1]]
            print("Document file: " + name_doc)
            print("Title: " + new['title'])
            print("Date: " + new['date'])
            print("Keywords: " + new['keywords'])
            print("Article: " + new['article'])
            print("\n------------------------------------------------------------\n")
    elif num_news >= 3 and num_news <= 5:
        for n in rnews:
            name_doc = doc_list[art_index[n][0]] 
            doc = load_jason(name_doc)
            new = doc[art_index[n][1]]
            print("Document file: " + name_doc)
            print("Title: " + new['title'])
            print("Date: " + new['date'])
            print("Keywords: " + new['keywords'])
            print("Article Snippet: ")
            print(snippet(query,new['article']))
            print("\n------------------------------------------------------------\n")
    else: #num_news > 5:
        for n in rnews[0:10]:
            name_doc = doc_list[art_index[n][0]] 
            doc = load_jason(name_doc)
            new = doc[art_index[n][1]]
            print("Document file: " + name_doc + "; Title: " + new['title'] + "; Date: " + new['date'] + "; Keywords: " + new['keywords'])
            print("\n------------------------------------------------------------\n")
    
    print('Number of retrieved news: ' + str(num_news) + '\n')
    return num_news


def search(filename, stemming=False, single_q=None):
    '''
    Realiza una query o sucesión de queries sobre el índice (filename) dado
    '''
    #cargamos cada diccionario a partir de la lista contenida en filename 
    dicts = load_index(filename)
    doc_dir = dicts[0]
    art_index = dicts[1]
    inv_index = dicts[2]
    title_index = dicts[3]
    summary_index = dicts[4]
    keywords_index = dicts[5]
    date_index = dicts[6]
    stem_index = dicts[7]
    perm_rotations = dicts[8]
    perm_rotations_keywords = dicts[9]
    perm_rotations_date = dicts[10]
    perm_rotations_title = dicts[11]
    perm_rotations_sum = dicts[12]
    n_docs = dicts[13]

    #si se realiza una única query
    if single_q==None:
        while(True):
            mult_q = input('\n Introduzca una nueva consulta: ') 
            if(mult_q == ''):
                break
            clean_q = mult_q.lower().split()
            rnews = make_query(clean_q, art_index, inv_index, title_index, summary_index, keywords_index, date_index, stem_index, stemming, perm_rotations, perm_rotations_keywords, perm_rotations_date, perm_rotations_title, perm_rotations_sum, n_docs)
            show_retrieved(rnews, art_index, doc_dir, mult_q)
    #si se pretende realizar múltiples queries
    else:
        clean_q = single_q.lower().split()
        rnews = make_query(clean_q, art_index, inv_index, title_index, summary_index, keywords_index, date_index, stem_index, stemming, perm_rotations, perm_rotations_keywords, perm_rotations_date, perm_rotations_title, perm_rotations_sum, n_docs)
        show_retrieved(rnews, art_index, doc_dir, single_q)

        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Insufficient arguments')
        print('USAGE: SAR_search -s(OPTIONAL) <index_directory>  <query>(OPTIONAL)')
    elif len(sys.argv) == 2:
        search(sys.argv[1])
    elif len(sys.argv) == 3:
        if sys.argv[1]=='-s':
            search(sys.argv[2], stemming=True)
        else:
            search(sys.argv[1], single_q=sys.argv[2])
    else:
        if sys.argv[1]!='-s':
            print('Unknown argument: ' + sys.argv[1])
            print('USAGE: SAR_search -s(OPTIONAL) <index_directory>  <query>(OPTIONAL)')
            exit(1)
        search(sys.argv[2], stemming=True, single_q=sys.argv[3])