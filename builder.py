import sqlite3
import re
import chardet
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk import pos_tag
from numpy import *
import h5py
import clustering
import time
import operator

size = 1000

def create_wiki_database():
    con = sqlite3.connect('wiki.db')
    con.execute('CREATE TABLE ru_words (word TEXT, row NUMERIC)')
    con.execute('CREATE TABLE en_words (word TEXT, row NUMERIC)')
    con.execute('CREATE TABLE categories (ID INTEGER PRIMARY KEY, ru TEXT, en TEXT, name TEXT)')
    con.execute('CREATE TABLE ru_wikipages (col NUMERIC, name TEXT, content TEXT, category TEXT)')
    con.execute('CREATE TABLE en_wikipages (col NUMERIC, name TEXT, content TEXT, category TEXT)')
    con.commit()
    con.close()

def create_webpages_database():
    con = sqlite3.connect('sites.db')
    con.execute('CREATE TABLE links (ID INTEGER PRIMARY KEY, page TEXT, backlink TEXT)')
    con.execute('CREATE TABLE ru_pages (link TEXT, col NUMERIC)')
    con.execute('CREATE TABLE en_pages (link TEXT, col NUMERIC)')
    con.execute('CREATE TABLE extPages (language TEXT, link TEXT, content TEXT, predicted TEXT)')
    con.commit()
    con.close()

def build_ru_matrix():
    con = sqlite3.connect('wiki.db')
    con.execute('delete from ru_words')
    stemmer = SnowballStemmer('russian')

    terms = dict()
    docs = dict()
    row = 0
    col = 0
    h_size = con.execute('select count(*) from ru_wikipages').fetchone()
    print ('%s articles found' % h_size[0])
    ru_matrix = zeros((1, h_size[0]), dtype='int')
    tmp_matrix = zeros((size, h_size[0]), dtype='int')
    addcount = 0
    
    for article in con.execute('select content, category from ru_wikipages') :
        name = 'art' + str(article[0])
        content = article[0]
        docs[col] = article[1]
        content = re.sub('ё', 'е',  content)
        content = re.sub("[^'ЙЦУКЕНГШЩЗХФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбю']", ' ',  content).split()
        for word in content:
            word = word.lower()
            if word in stopwords.words('russian'):
                continue
            word = stemmer.stem(word)
            if len(word) < 4:
                continue
            if word in terms:
                if word in terms:
                    if ru_matrix.shape[0] != 1:
                        if terms[word] > (ru_matrix.shape[0] - 1):
                            tmp_matrix[terms[word] - ru_matrix.shape[0], col] += 1
                        else:
                            ru_matrix[terms[word], col] += 1
                    else:
                        tmp_matrix[terms[word], col] += 1
            else:
                terms[word] = row
                if addcount < size:
                    tmp_matrix[addcount, col] += 1
                else:
                    ru_matrix = vstack((ru_matrix, tmp_matrix))
                    if ru_matrix.shape[0] == size + 1:
                        ru_matrix = delete(ru_matrix, 0, 0)
                    tmp_matrix = zeros((size, h_size[0]), dtype='int')
                    addcount = 0
                    tmp_matrix[addcount, col] += 1
                row += 1
                addcount += 1
        col += 1

    if addcount < size-1:
        tmp_matrix = tmp_matrix[0:addcount]
    ru_matrix = vstack((ru_matrix, tmp_matrix))
    l = []
    to_del = []
    for r in range(ru_matrix.shape[0]):
        if count_nonzero(ru_matrix[r]) > 1:
            l.append(r)
        else:
            to_del.append(r)
    ru_matrix = ru_matrix[l,:]
    print('Building finished:', ru_matrix.shape)
    
    f = h5py.File('hdf5/ru_matrix.hdf5', 'w')
    dset = f.create_dataset('ru_matrix', data=ru_matrix)
    f.close()
    sorted_terms = sorted(terms.items(), key=operator.itemgetter(1))
    row = 0
    for word in sorted_terms:
        if word[1] not in to_del:
            con.execute('insert into ru_words values (?, ?)', (word[0], row))
            row += 1
    con.commit()
    con.close()
    print('Inserting finished')   

def build_en_matrix():
    con = sqlite3.connect('wiki.db')
    con.execute('delete from en_words')
    
    stemmer = SnowballStemmer('english')

    #en_parts = ['FW', 'NN', 'NNS', 'NNP', 'NNPS']

    terms = dict()
    docs = dict()
    row = 0
    col = 0
    h_size = con.execute('select count(*) from en_wikipages').fetchone()
    print ('%s articles found' % h_size[0])
    en_matrix = zeros((1, h_size[0]), dtype='int')
    tmp_matrix = zeros((size, h_size[0]), dtype='int')
    addcount = 0
    
    for article in con.execute('select content, category from en_wikipages'):
        content = article[0]
        docs[col] = article[1]
        content = re.sub("[^'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm']", ' ',  content).split()
        #content = pos_tag(content)
        for word in content:
            #if prt[1] not in en_parts:
                #continue
            word = word.lower()
            if word in stopwords.words('english'):
                continue
            word = stemmer.stem(word)
            if len(word) < 4:
                continue
            if word in terms:
                if en_matrix.shape[0] != 1:
                    if terms[word] > (en_matrix.shape[0] - 1):
                        tmp_matrix[terms[word] - en_matrix.shape[0], col] += 1
                    else:
                        en_matrix[terms[word], col] += 1
                else:
                        tmp_matrix[terms[word], col] += 1
            else:
                terms[word] = row
                if addcount < size:
                    tmp_matrix[addcount, col] += 1
                else:
                    en_matrix = vstack((en_matrix, tmp_matrix))
                    if en_matrix.shape[0] == size + 1:
                        en_matrix = delete(en_matrix, 0, 0)
                    tmp_matrix = zeros((size, h_size[0]), dtype='int')
                    addcount = 0
                    tmp_matrix[addcount, col] += 1
                row += 1
                addcount += 1
        col += 1

    if addcount < size-1:
        tmp_matrix = tmp_matrix[0:addcount]
    en_matrix = vstack((en_matrix, tmp_matrix))
    l = []
    to_del = []
    for r in range(en_matrix.shape[0]):
        if count_nonzero(en_matrix[r]) > 1:
            l.append(r)
        else:
            to_del.append(r)
    en_matrix = en_matrix[l,:]
    print('Building finished:', en_matrix.shape)
    
    f = h5py.File('hdf5/en_matrix.hdf5', 'w')
    dset = f.create_dataset('en_matrix', data=en_matrix)
    f.close()
    sorted_terms = sorted(terms.items(), key=operator.itemgetter(1))
    row = 0
    for word in sorted_terms:
        if word[1] not in to_del:
            con.execute('insert into en_words values (?, ?)', (word[0], row))
            row += 1
    con.commit()
    con.close()
    print('Inserting finished')

def build_rupg_matrix():
    stemmer = SnowballStemmer('russian')
    terms = dict()
    con = sqlite3.connect('wiki.db')
    for r in con.execute('select * from ru_words'):
        terms[r[0]] = r[1]
    pageID = dict()
    con.close()
    col = 0
    con2 = sqlite3.connect('sites.db')
    h_size = con2.execute('select count(*) from extPages where language="ru"').fetchone()
    v_size = len(terms)
    ru_matrix = zeros((v_size, h_size[0]), dtype='int')
    for page in con2.execute('select link, content from extPages where language="ru"'):
        content = page[1]
        content = re.sub('ё', 'е',  content)
        content = re.sub("[^'ЙЦУКЕНГШЩЗХФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбю']", ' ',  content).split()
        for word in content:
            word = word.lower()
            if word in stopwords.words('russian'):
                continue
            word = stemmer.stem(word)
            if len(word) < 4:
                continue
            if word not in terms:
                continue
            else:
                ru_matrix[terms[word], col] += 1
        pageID[page[0]] = col
        col += 1
    print('Building finished')
    
    f = h5py.File('hdf5/ru_pages.hdf5', 'w')
    dset = f.create_dataset('ru_pages', data=ru_matrix)
    f.close()
    con2.execute('delete from ru_pages')
    for link, col in pageID.items():
        con2.execute('insert into ru_pages values (?, ?)', (link, col))
    con2.commit()
    con2.close()
    print('Inserting finished')

def build_enpg_matrix():
    stemmer = SnowballStemmer('english')
    terms = dict()
    con = sqlite3.connect('wiki.db')
    for r in con.execute('select word, row from en_words'):
        terms[r[0]] = r[1]
    pageID = dict()
    con.close()
    col = 0
    con2 = sqlite3.connect('sites.db')
    h_size = con2.execute('select count(*) from extPages where language="en"').fetchone()
    v_size = len(terms)
    en_matrix = zeros((v_size, h_size[0]), dtype='int')

    for page in con2.execute('select link, content from extPages where language="en"'):
        content = page[1]
        content = re.sub("[^'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm']", ' ',  content).split()
        for word in content:
            word = word.lower()
            if word in stopwords.words('english'):
                continue
            word = stemmer.stem(word)
            if len(word) < 4:
                continue
            if word not in terms:
                continue
            else:
                en_matrix[terms[word], col] += 1
        pageID[page[0]] = col
        col += 1
    print('Building finished')
    
    f = h5py.File('hdf5/en_pages.hdf5', 'w')
    dset = f.create_dataset('en_pages', data=en_matrix)
    f.close()
    con2.execute('delete from en_pages')
    for link, col in pageID.items():
        con2.execute('insert into en_pages values (?, ?)', (link, col))
    con2.commit()
    con2.close()
    print('Inserting finished')

def give_ID():
    con = sqlite3.connect('wiki.db')
    con.execute('update ru_wikipages set col=(rowid-1)')
    con.commit()
    con.execute('update en_wikipages set col=(rowid-1)')
    con.commit()
    con.close()
