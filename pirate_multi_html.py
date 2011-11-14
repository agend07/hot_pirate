#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import threading
import logging
import Queue
import codecs



''' 
    http://thepiratebay.org/browse/205/0/3          - browse tv shows 
    http://thepiratebay.org/browse/205/1/3          - 2 strona
    http://thepiratebay.org/browse/205/4/3          - 4 strona

    http://thepiratebay.org/browse/201/0/3          - browse movies
    http://thepiratebay.org/browse/201/1/3          - 2 strona itd
'''

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',)

TV_ADDRESS = r'http://thepiratebay.org/browse/205/%d/3'
MOVIE_ADDRESS = r'http://thepiratebay.org/browse/201/%d/3'
OUTPUT_FILE = r'/home/arek/hot_pirate_torrents.html'
THREADS = 20
TOP_TORRENTS = 30

strony = {}
q=Queue.Queue()


def process_page(page, bufor):
    """Wyciągniej ze ściągniętej strony dane które mnie interesują:
        title, link, leechers, i dodaj je do bufora
    """ 
    from BeautifulSoup import BeautifulSoup

    soup = BeautifulSoup(page)
    tabela = soup.find('table', id='searchResult').findAll('tr')[1:-1]

    for row in tabela:
        # title = row.div.a['title']
        title = row.div.a.text
        leechers = int(row.findAll('td', align='right')[1].text)
        link = 'http://thepiratebay.com' + row.div.a['href']

        result = dict(title=title, leechers=leechers, link=link)
        bufor.append(result)

# def print_result_html(bufor):
#     for e in sorted(bufor, reverse=True)[:20]:
#         html_page += '<a href=%s> %d %s </a> \n' % (e.leechers, e.title, e.link )

def print_result(bufor):
    for e in sorted(bufor, reverse=True, key=lambda x:x['leechers'])[:20]:
        try:
            print e['leechers'], e['title'], '\n', '---->', e['link'], '\n'
        except UnicodeEncodeError:
            print '*'*30


def process_job():
    """Ściągnij treść strony i umieść w słowniku: strony[adres] = tekst"""

    import requests

    while True:
        adres = q.get()
        logging.debug('ściągam : %s' % adres)
        tekst = requests.get(adres).content
        strony[adres]=tekst
        q.task_done()


def main(pages_count):  
    '''zrobimy tak: na wątku będziemy ściągać, potem na głównym przerobimy wszystko na pozycje w liście'''

    for i in range(pages_count):
        q.put(TV_ADDRESS % i)
        q.put(MOVIE_ADDRESS % i)

    for i in range(THREADS):
        worker = threading.Thread(target=process_job)
        worker.setDaemon(True)
        worker.start()

    q.join()
    logging.debug('wszystko ściągnięte - teraz przetwarzam ...')

    # teraz wszystko mamy ściągnięte i czeka w słowniku: strony

    tv_shows=[]
    movies=[]

    for adres in strony:
        if '/browse/205/' in adres:
            process_page(strony[adres], tv_shows)
        elif '/browse/201/' in adres:
            process_page(strony[adres], movies)
    
    tv_shows = sorted(tv_shows, reverse=True, key=lambda x:x['leechers'])[:TOP_TORRENTS]
    movies = sorted(movies, reverse=True, key=lambda x:x['leechers'])[:TOP_TORRENTS]

    render_html(tv_shows, movies)

def render_html(tv_shows, movies):
    """Korzystając z jinja2 stwórz stronę z linkami, i zapisz ją do pliku OUTPUT_FILE"""

    from jinja2 import Environment, PackageLoader

    env = Environment(loader=PackageLoader('pirate', 'templates'))
    template = env.get_template('pirate.html')

    page = template.render(tv_shows=tv_shows, movies=movies)

    with codecs.open(OUTPUT_FILE, 'wt', encoding='utf-8') as f:
        f.write(page)

    logging.debug("I'm done !")


if __name__ == '__main__':

    try:
        pages_count=int(sys.argv[1])
    except (IndexError, ValueError):
        pages_count=10

    main(pages_count)   

    

