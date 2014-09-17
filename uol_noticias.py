# -*- coding: utf-8 -*-

'''
Created on 10/set/2014

@author: Sergio (srodriguex[at]gmail.com).

Craw in UOL Notícias web page looking for news URLs.
'''

import codecs
import goose
import pymongo
import requests as req

from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool

client = pymongo.MongoClient()
UOL_CRAWLER = client.UOL_CRAWLER
URLS = UOL_CRAWLER.urls
ARTICLE = UOL_CRAWLER.article

config = {
    'threads': 40,  # Number of threads used in the fetching pool
}

class crawler(object):

    def __init__(self, limit):
        self.sources = []
        self.limit = limit
        
        
    def add_source(self, name, base_url, limit=10):
        """
        Returns an list of 'limit' news links contained in the 'base_url' link of UOL Notícias portal. The 'base_url' MUST BE that give the list of news like:
            http://noticias.uol.com.br/ciencia/noticias
            http://noticias.uol.com.br/cotidiano/noticias
            http://noticias.uol.com.br/politica/noticias

        
        Parameters:
        limit: Number of news URLs to look for.
        base_url: URL of the starting page with news.
        """

        # List of links to be returned.
        news = []

        # HTTP Header configuration to simulate a "real" browser and prevent anti crawling policies.
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        # Initialize the next url to fetch with the base url given.
        next_url = base_url

        # Loop until stop conditions are satisfied.
        while(True):

            # Get the URL text content.
            html = req.get(next_url, headers=headers).text

            # Parse the text conent.
            if html:
                doc = BeautifulSoup(html, 'html.parser')

            # Extract all news links found.
            if doc:
                articles = doc.findAll('article')

                for art in articles:
                    # datetime = art.time['datetime']
                    href = art.a['href']
                    # title = art.span.text
                    news.append(href)
                    exists = list(URLS.find({"url":href}))
                    if not exists:
                        news_url = {'name':name, 'url':href}
                        URLS.save(news_url)

            next_page = doc.find('a', text=u'Próxima')

            # Check stop conditions. If they are true, return the list.
            if len(news)>self.limit or not next_page :
                return news
            # If the stop conditions aren't yet satisfied, load next page.
            else:
                #self.sources.append({'name':name, 'url':news})
                next_url = base_url+next_page['href']
                #print next_url
     
    def fetch_url(self, mongo_object):
        Goo = goose.Goose({'enable_image_fetching':False})
        try:
            article = Goo.extract(mongo_object['url'])
            article_info = {'publish_date':article.publish_date,
                    'tags':list(article.tags),
                    'title':article.title,
                    'meta_keywords':list(article.meta_keywords),
                    'cleaned_text':article.cleaned_text,
                    'domain':article.domain,
                    'parsed': True}
            print 'Inserting %s' % str(mongo_object['_id'])
        except:
            aticle_info = {'error':'error'}
            print 'Inserting %s' % str(mongo_object['_id'])
        URLS.update({'_id':mongo_object['_id']}, {"$set": article_info}, upsert=False)                
        
                
    def  download_article(self):
        #feed_count = FEEDS.count()
        thread_pool = ThreadPool(config['threads'])
        urls_download = list(URLS.find({'parsed':{'$exists': False}}))
        thread_pool.map(self.fetch_url, urls_download)
        
            
                
        
if __name__ == '__main__':
    # Example of use.   
    uol = crawler(limit=1000)
    thread_pool = ThreadPool(config['threads'])
    
    ciencia = 'http://noticias.uol.com.br/ciencia/noticias'
    cotidiano = 'http://noticias.uol.com.br/cotidiano/noticias'
    politica = 'http://noticias.uol.com.br/politica/noticias'
    carros = 'http://carros.uol.com.br/noticias/'
    musica = 'http://musica.uol.com.br/ultimas/'
    cinema = 'http://cinema.uol.com.br/ultimas/'
    esporte = 'http://esporte.uol.com.br/noticias/'
    internacional = 'http://noticias.uol.com.br/internacional/noticias'
    saude = 'http://noticias.uol.com.br/saude/noticias'
    tecnologia = 'http://tecnologia.uol.com.br/noticias'
    eleicoes = 'http://eleicoes.uol.com.br/2014/ultimas/'
    economia = 'http://economia.uol.com.br/noticias/'
    
    sessions = [('ciencia', ciencia), ('cotidiano', cotidiano), ('politica', politica),
        ('carros', carros), ('musica', musica), ('cinema', cinema), ('esporte', esporte),
        ('internacional', internacional), ('saude', saude), ('tecnologia', tecnologia),
        ('eleicoes', eleicoes), ('economia', economia)]
    thread_pool.map(lambda x: uol.add_source(name=x[0], base_url=x[1]), sessions)    
    
    uol.download_article()
    
