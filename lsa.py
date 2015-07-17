import h5py
import sqlite3
import operator
import math
from numpy import *
from numpy.linalg import inv
from sklearn.feature_extraction.text import TfidfTransformer
import scipy.sparse
from sparsesvd import sparsesvd

def tfidf(mtname):
    f = h5py.File('hdf5/' + mtname + '.hdf5', 'r')
    matrix = f[mtname][:]
    f.close()
    tfidf_transformer = TfidfTransformer()
    tfidf_transformer.set_params(norm=None)
    matrix = tfidf_transformer.fit_transform(matrix)
    f2 = h5py.File('hdf5/' + mtname + '_tfidf.hdf5', 'w')
    f2.create_dataset(mtname + '_tfidf', data=matrix.todense(), dtype='f4')
    f2.close()
    print('tf-idf performed')

def SVD(lang, dim):
    f = h5py.File(lang + '_matrix_tfidf.hdf5', 'r')
    matrix = f[lang + '_matrix_tfidf'][:]
    f.close()
    smatrix = scipy.sparse.csc_matrix(matrix)
    Ut, S, Vt = sparsesvd(smatrix, dim) 
    
    f2 = h5py.File(str(dim) + lang + '_matrixS.hdf5', 'w')
    f2.create_dataset(str(dim) + lang + '_matrixS', data=diag(S))
    f2.close()
    f3 = h5py.File(str(dim) + lang + '_matrixUt.hdf5', 'w')
    f3.create_dataset(str(dim) + lang + '_matrixUt', data=Ut)
    f3.close()
    f4 = h5py.File(str(dim) + lang + '_matrixVt.hdf5', 'w')
    f4.create_dataset(str(dim) + lang + '_matrixVt', data=Vt)
    f4.close()

def add_pages(lang, dim):
    f = h5py.File('hdf5/' + lang + '_pages_tfidf.hdf5', 'r')
    matrix = f[lang + '_pages_tfidf'][:]
    f.close()
    f2 = h5py.File('hdf5/' + str(dim) + lang + '_matrixUt.hdf5', 'r')
    Ut = f2[str(dim) + lang + '_matrixUt'][:]
    f2.close()
    f3 = h5py.File('hdf5/' + str(dim) + lang + '_matrixS.hdf5', 'r')
    S = f3[str(dim) + lang + '_matrixS'][:]
    f3.close()
    S = inv(S)
    col = matrix.shape[1]
    result = zeros((S.shape[0], col))
    for i in range(col):
        v = matrix[:,i]
        v = vstack(v)
        v2 = dot(Ut, v)
        v2 = dot(S, v2)
        result[:,i] = v2[:,0]
    f4 = h5py.File('hdf5/' + lang + '_pages_LSI.hdf5', 'w')
    f4.create_dataset(lang + '_pages_LSI', data=result)
    f4.close()
