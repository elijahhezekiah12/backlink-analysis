import h5py
import sqlite3
import operator
import math
import re
from scipy.spatial.distance import cosine
from sklearn.metrics import precision_recall_fscore_support
from numpy import *
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib as mpl

def get_distances(matrix, v1, k):
    distlist = []
    col = matrix.shape[1]
    for i in range(col):
        v2 = matrix[:,i]
        distlist.append((cosine(v1, v2), i))
    distlist.sort()
    return distlist[:k]
    
def kNN(lang, dim, k):
    f = h5py.File('hdf5/' + lang + '_pages_LSI.hdf5','r')
    pages = f[lang + '_pages_LSI'][:]
    f.close()
    f2 = h5py.File('hdf5/' + str(dim) + lang + '_matrixVt.hdf5','r')
    matrix = f2[str(dim) + lang + '_matrixVt'][:]
    f2.close()
    
    col = pages.shape[1]
    categories = dict()
    articles = dict()
    con = sqlite3.connect('wiki.db')
    for r in con.execute('select col, category from ' + lang + '_wikipages'):
        articles[r[0]] = r[1]
    for r in con.execute('select ' + lang + ' from categories'):
        categories[r[0]] = 0
    con.close()
    pgcat = dict()

    for i in range(col):
        v = pages[:,i]
        distlist = get_distances(matrix, v, k)
        for dist in distlist:
            tmp = dist[1]
            tmp = articles[tmp]
            categories[tmp] += 1
        cat = max(categories, key=categories.get)
        pgcat[i] = cat
        categories = dict.fromkeys(categories, 0)

    stat = dict()
    for i in range(len(pgcat)):
        if pgcat[i] not in stat:
            stat[pgcat[i]] = 1
        else:
            stat[pgcat[i]] += 1
    return stat

def results(ru_stat, en_stat):
    shared = []
    con = sqlite3.connect('wiki.db')
    for cat in con.execute('select ru, en, name from categories'):
        val = 0
        if cat[0] in ru_stat:
            val += ru_stat[cat[0]]
        if cat[1] in en_stat:
            val += en_stat[cat[1]]
        if val > 0:
            shared.append((cat[2], val))
    con.close()
    shared.sort(key=lambda x: x[1], reverse=True)
    con = sqlite3.connect('sites.db')
    s = con.execute('select count(*) from extPages where language in ("ru", "en")').fetchone()
    s = s[0]
    labels = []
    sizes = []
    print ('Results:')
    for c in shared:
        print (c[0], ': ', c[1], ' (', '%.2f' % ((c[1]/s)*100), '%)', sep='')
        labels.append(c[0])
        sizes.append(c[1])
    mpl.rcParams['font.family'] = 'fantasy'
    mpl.rcParams['font.fantasy'] = 'Arial'
    explode = zeros((len(shared)), dtype='f')
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.show()
    

def statistics(lim):
    con = sqlite3.connect('sites.db')
    r = con.execute('select count(*) from extPages').fetchone()
    print ('Backlinks found:', r[0])
    r = con.execute('select count(*) from extPages where language="ru"').fetchone()
    print('Pages in Russian:', r[0])
    r = con.execute('select count(*) from extPages where language="en"').fetchone()
    print('Pages in English:', r[0])
    r = con.execute('select count(*) from extPages where language not in ("ru", "en")').fetchone()
    print('Pages in other languages:', r[0])
    print(lim, ' the most popular pages:', sep='')
    for r in con.execute('select page, count(backlink) as ct from links group by page order by ct desc limit ' + str(lim)):
        print(r[0], ' - ', r[1], ' links', sep='')
    con.close()
    
        
