#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import threading
import logging
import Queue

from BeautifulSoup import BeautifulSoup
import requests

'''
todo: przerobić na wątki, tyle wątków ile adresów
'''

''' 
	http://thepiratebay.org/browse/205/0/3 			- browse tv shows 
	http://thepiratebay.org/browse/205/1/3 			- 2 strona
	http://thepiratebay.org/browse/205/4/3			- 4 strona

	http://thepiratebay.org/browse/201/0/3			- browse movies
	http://thepiratebay.org/browse/201/1/3			- 2 strona itd
'''

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s',)

TV_ADDRESS = r'http://thepiratebay.org/browse/205/%d/3'
MOVIE_ADDRESS = r'http://thepiratebay.org/browse/201/%d/3'
THREADS = 20

strony = {}
q=Queue.Queue()

def process_page(page, bufor):
	soup = BeautifulSoup(page)
	tabela = soup.find('table', id='searchResult').findAll('tr')[1:-1]

	for row in tabela:
		# title = row.div.a['title']
		title = row.div.a.text
		leechers = int(row.findAll('td', align='right')[1].text)
		link = 'http://thepiratebay.com' + row.div.a['href']
		
		# 
		# if leechers > 29:
		# 	bufor.append((leechers, title))
		bufor.append((leechers, title, link))

def print_result(bufor):
	for e in sorted(bufor, reverse=True)[:20]:
		try:
			print e[0], e[1]
		except UnicodeEncodeError:
			print '*'*30


def process_job():
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

	print 'tv shows * ' * 100, '\n'*2
	print_result(tv_shows)
	
	print '\n'*5, 'movies * ' * 100, '\n'*2
	print_result(movies)


if __name__ == '__main__':

	try:
		pages_count=int(sys.argv[1])
	except (IndexError, ValueError):
		pages_count=10

	main(pages_count)	