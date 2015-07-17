import urllib.request
from bs4 import BeautifulSoup, Comment
from wikitools import wiki as w
from wikitools import category as c
from wikitools import page as pg
import wikipedia
import sqlite3
import chardet
import re

class wiki:

    def __init__(self):
        self.con = sqlite3.connect('wiki.db')

    def __del__(self):
        self.con.close()

    def is_indexed(self, name, lang):
        u = self.con.execute('select * from ' + lang + '_wikipages where name=?', (name,)).fetchone( )
        if u!=None: return True
        return False

    def get_categories(self):
        f = open('ru_categories.txt', 'r')
        ru_cats = f.read()
        f.close()
        ru_cats = re.sub('[,.]', ' ', ru_cats)
        ru_cats = ru_cats.split()
        f2 = open('en_categories.txt', 'r')
        en_cats = f2.read()
        f2.close()
        en_cats = re.sub('[,.]', ' ', en_cats)
        en_cats = en_cats.split()
        if len(ru_cats) != len(en_cats):
            print('Error: different number of categories')
            return
        
        self.con.execute('delete from categories')
        for i in range(len(en_cats)):
            name = re.sub('_', ' ', en_cats[i])
            self.con.execute('insert into categories(ru, en, name) values (?,?,?)', (ru_cats[i], en_cats[i], name))

    def get_articles(self, lang, update=False):

        if update==True:
            for r in self.con.execute('select distinct category from ' + lang + '_wikipages where category not in (select ' + lang + ' from categories)'):
                self.con.execute('delete from ' + lang + '_wikipages where category=?', (str(r[0]),))
                print('Deleting category', r[0], '...')
        else:
            self.con.execute('delete from ' + lang + '_wikipages')
        wikipedia.set_lang(lang)
        wikisite = 'http://' + lang + '.wikipedia.org/w/api.php'

        wikiObject = w.Wiki(wikisite)
        cats = self.con.execute('select ' + lang + ' from categories').fetchall()
        for cat in cats:
            print('Checking category:', cat[0])
            if lang == 'ru':
                wikiCategory = c.Category(wikiObject, title='Категория:' + cat[0])
            elif lang == 'en':
                wikiCategory = c.Category(wikiObject, title='Category:' + cat[0])
            else:
                break
            articles = wikiCategory.getAllMembers(namespaces=[0])
            if len(articles) > 200:
                articles = articles[0:200]
            for article in articles:
                try:
                    if self.is_indexed(article.title, lang):
                        continue
                    print('Loading article', article.title, '...')
                    new_article = wikipedia.page(article.title)
                    if len(new_article.content) == 0:
                        continue
                    self.con.execute('insert into ' + lang + '_wikipages(name, content, category) values(?, ?, ?)', (article.title, new_article.content, cat[0]))
                except:
                    continue
            self.con.commit()
