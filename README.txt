The program is written in Python 3.4 and allows to analyze backlinks and find the topics of pages that contain them.
Currently the classification is available only for pages in English and Russian, but that can be easily changed.
There are 2 parts:
1. Building the training set (articles from Wikipedia), where the categories should be chosen manually (I know, it takes long, and maybe I'll work on that later). I use Latent Semantic Indexing (LSI) for reducing the size of the term-document matrix and removing "noise".
2. Checking a given website and analyzing its backlinks. I use k Nearest Neighbors algorithm here.
The result is a list of categories and numbers, which shows how many external pages belong to each category. 
The average precision (the amount of topics guessed correctly) is ~58%.

You need the following libraries:
BeautifulSoup
NLTK
cython
numpy
scipy
scikit-learn
langdetect
chardet
h5py
matplotlib
wikipedia
wikitools
sparsesvd

If you have any comments, questions and/or suggestions please feel free to contact me: vgeclair@gmail.com