import moz
import builder
import classification
#import lsa
import wiki
import time

# Build the training set:

#builder.create_wiki_database() #if not created
wiki = wiki.wiki()
wiki.get_categories()
wiki.get_articles('ru', True)
wiki.get_articles('en', True)
#builder.build_ru_matrix()
#builder.build_en_matrix()
#lsa.tfidf('ru_matrix')
#lsa.tfidf('en_matrix')
#builder.give_ID()
#SVD('ru', 100)
#SVD('en', 100)

# Analyze backlinks:
# ! You need an account on moz.com for using this !

#builder.create_webpages_database() #if not created
##t1 = time.clock()
##site = 'http://www.apmath.spbu.ru/'
##member = 'mozscape-123456789'
##key = 'b7ead4f08c83ef8738d9150845899a24'
##scope = 'page_to_subdomain'
##moz = moz.moz()
##moz.check_mozscape(site, member, key, scope)
##builder.build_rupg_matrix(0)
##builder.build_enpg_matrix(0)
###lsa.tfidf('ru_pages')
###lsa.tfidf('en_pages')
###lsa.add_pages('ru', 200)
###lsa.add_pages('en', 350)
##stat1 = classification.kNN('ru', 200, 65)
##stat2 = classification.kNN('en', 350, 89)
##classification.results(stat1, stat2)
##print('')
##classification.statistics(10)
##t2 = time.clock()
##print('time:', t2-t1)



