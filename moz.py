import urllib.request
from bs4 import BeautifulSoup, Comment
import sqlite3
import requests
from io import StringIO
from langdetect import detect
import chardet
import hashlib
import hmac
import time
import base64
import re

class moz:
    
    def __init__(self):
        self.con = sqlite3.connect('sites.db')
        self.con.execute('delete from links')
        self.con.execute('delete from extPages')
        self.con.commit()
        
    def __del__(self):
        self.con.close()

    def is_indexed(self, content):
        u = self.con.execute('select * from extPages where content=?', (content,)).fetchone( )
        if u!=None: return True
        return False
    
    def get_text_only(self, soup):
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        if text == None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.get_text_only(t)
                resulttext += subtext+'\n'
            return resulttext
        else:
            return text.strip( )

    def check_mozscape(self, url, member, key, scope):
        expires = int(time.time() + 300)
        toSign  = '%s\n%i' % (member, expires)
        signature = base64.b64encode(hmac.new(key.encode(), toSign.encode(), hashlib.sha1).digest())
        params = dict()
        params['AccessID'] = member
        params['Expires'] = expires
        params['Signature'] = signature
        u = 'http://lsapi.seomoz.com/linkscape/links/' + url + '?Scope=' + scope + '&Sort=page_authority&Filter=external&Limit=1000&SourceCols=536870916&TargetCols=4&'
        u = u + urllib.parse.urlencode(params)
        print('Checking', u)
        try:
            c = urllib.request.urlopen(u)
        except:
            print ('Could not open', u)
            return
        html = c.read()
        soup = BeautifulSoup(html)
        self.get_links(soup, url)
        self.con.commit()

    def get_links(self, soup, site):
        result = self.get_text_only(soup)
        r = 'self.links = ' + result
        exec(r)
        print('Found', len(self.links), 'backlinks')
        for link in self.links:
            backlink ='http://' + link['uu']
            page = link['luuu']
            if self.get_content(backlink, site) != True:
                continue
            self.con.execute('insert into links(page, backlink) values(?, ?)', (page, backlink))     

    def get_content(self, url, site):
        u = self.con.execute('select * from extPages where link=?', [url]).fetchone()
        if u != None:
            return False
        try:
            c = urllib.request.urlopen(url)
        except:
            return False
        html = c.read() 
        soup = BeautifulSoup(html)
        print('Checking', url)
        if self.if_contains_a_link(soup, site) == False:
            return False
        comments = soup.findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]

        for script in soup.findAll('script'):
            script.extract()
        for frame in soup.findAll('iframe'):
            frame.extract()
        for frame in soup.findAll('frameset'):
            frame.extract()
        for style in soup.findAll('style'):
            style.extract()
            
        text = self.get_text_only(soup)
        try:
            language = detect(text)
        except:
            return False
        if self.is_indexed(text):
            return False
        self.con.execute('insert into extPages(link, content, language) values(?, ?, ?)', (url, text, language))
        print('Got content from', url)
        return True

    def if_contains_a_link(self, soup, site):
        site = site.replace('http://', '')
        site = site.replace('https://', '')
        site = site.replace('www.', '')
        site = site.replace('/', '')
        for a in soup.find_all('a', href=True):
            if site in a['href']:
                return True
        #print('This is an ex-parrot.')
        return False
