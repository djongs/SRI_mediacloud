# -*- coding: utf-8 -*-

'''
Created on 10/set/2014

@author: Sergio (srodriguex[at]gmail.com).

Craw in UOL Notícias web page looking for news URLs.
'''

import requests as req
from bs4 import BeautifulSoup
import codecs


def crawl(base_url, limit=100):
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

        next_page = doc.find('a', text=u'Próxima')

                
        # Check stop conditions. If they are true, return the list.
        if len(news)>limit or not next_page :
            return news
        # If the stop conditions aren't yet satisfied, load next page.
        else:
            next_url = base_url+next_page['href']
            #print next_url
        
if __name__ == '__main__':
    # Example of use.   
    ciencia = 'http://noticias.uol.com.br/ciencia/noticias'
    cotidiano = 'http://noticias.uol.com.br/cotidiano/noticias'
    politica = 'http://noticias.uol.com.br/politica/noticias'
    crawl(ciencia)