#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys

from BeautifulSoup import BeautifulSoup
import requests

'''
todo: przerobić na wątki, tyle wątków ile adresów
'''

''' http://thepiratebay.org/recent/
	http://thepiratebay.org/recent/1 itd

	http://thepiratebay.org/browse/205 				- browse tv shows albo /205/0/3 - też może być
	http://thepiratebay.org/browse/205/1/3 			- 2 strona
	http://thepiratebay.org/browse/205/4/3			- 4 strona

	http://thepiratebay.org/browse/201				- browse movies
	http://thepiratebay.org/browse/201/1/3			- 2 strona itd
'''

TV_ADDRESS = r'http://thepiratebay.org/browse/205/%d/3'
MOVIE_ADDRESS = r'http://thepiratebay.org/browse/201/%d/3'

def process_page(page, bufor):
	soup = BeautifulSoup(page)
	tabela = soup.find('table', id='searchResult').findAll('tr')[1:-1]

	for row in tabela:
		# title = row.div.a['title']
		title = row.div.a.text
		leechers = int(row.findAll('td', align='right')[1].text)
		if leechers > 29:
			bufor.append((leechers, title))

	
def print_result(bufor):
	for e in sorted(bufor, reverse=True):
		try:
			print e[0], e[1]
		except UnicodeEncodeError:
			print '*'*30


def main(pages_count):	
	tv_shows=[]
	for i in range(pages_count):
		address = TV_ADDRESS % i
		sys.stderr.write('loading %s\n' % address)
		page = requests.get(address).content
		process_page(page, tv_shows)	
	

	movies=[]	
	for i in range(pages_count):
		address = MOVIE_ADDRESS % i
		sys.stderr.write('loading %s\n' % address)
		page = requests.get(address).content
		process_page(page, movies)	

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