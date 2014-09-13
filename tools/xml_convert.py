#!/usr/bin/python

import xml.sax
from xml.sax import handler
import sys
import argparse
import psycopg2 as psqldb


jlist = { '\\prl' : 'Phys. Rev. Lett.', '\\pra': 'Phys. Rev. A',
	'\\prb': 'Phys. Rev. B', '\\pre': 'Phys. Rev. E',
	'\\apl': 'Appl. Phys. Lett.', '\\jap': 'J. Appl. Phys.',
	'\\jltp': 'J. Low Temp. Phys.', '\\ijmpb': 'Intl. J. Mod. Phys. B',
	'\\ss' : 'Surf. Sci.',
	}
jlist_keys = jlist.keys()

vjlist = { '0' : 'Virtual Journal of ',
	'\\VJAS': 'Applications of Superconductivity',
	'\\VJNST': 'Nanoscale Science and Technology',
	'\\VJQI': 'Quantum Information',
	}
vjlist_keys = vjlist.keys()


#def print_sql():


def fix_HTML(s):
	p = s.find('$_{')
	while p >= 0:
		ns = s[0:p] + '<sub>' + s[p+3:]
		p = ns.find('}$')
		s = ns[0:p] + '</sub>' + ns[p+2:]
		p = s.find('$_{')

	p = s.find('$^{')
	while p >= 0:
		ns = s[0:p] + '<sup>' + s[p+3:]
		p = ns.find('}$')
		s = ns[0:p] + '</sup>' + ns[p+2:]
		p = s.find('$^{')

	p = s.find('$')
	while p >= 0:
		ns = s[0:p] + '<i>' + s[p+1:]
		p = ns.find('$')
		s = ns[0:p] + '</i>' + ns[p+1:]
		p = s.find('$')

	p = s.find('\delta')
	while p >= 0:
		ns = s[0:p] + '<math>&delta;</math>' + s[p+6:]
		s = ns
		p = s.find('\delta')

	p = s.find('\AA{}')
	while p >= 0:
		ns = s[0:p] + '&Aring;' + s[p+5:]
		s = ns
		p = s.find('\AA{}')

	p = s.find(u'\u00e9')
	while p >= 0:
		ns = s[0:p] + '&eacute;' + s[p+1:]
		s = ns
		p = s.find(u'\u00e9')

	p = s.find(u'\u00c7')
	while p >= 0:
		ns = s[0:p] + '&#x00c7;' + s[p+1:]
		s = ns
		p = s.find(u'\u00c7')

	return s

def print_html(ch):
	print '<h1>Publication List:</h1>'
	print '<ol>'
	for a in xh.article:
		title = fix_HTML(a.data['title'])
		author = fix_HTML(a.data['author'])
		abstract = fix_HTML(a.data['abstract'])
		jd = a.data['journal'].data
		jn = jd['name']
		if jn in jlist_keys:
			jn = jlist[jn]
		print '  <li>' + title
		print '    <dl>'
		print '    <dd><i>' + author + '</i>'
		print '    <dd><a href="' + jd['link'] + '" target="_blank">' \
			+ '<i>' + jn + '</i> ' \
			+ '<b>' + jd['volume'] + '</b>, ' \
			+ jd['page'] + ' (' + jd['year'] + ')</a>'
		for u in a.data['url']:
			if u.data['link'].find('http') >= 0:
				print '    <a href="' + u.data['link'] + '">' \
					+ u.data['name'] + '</a>'
			else:
				print '    <a href="Publication/' \
					+ u.data['link'] \
					+ '">' + u.data['name'] + '</a>'
		for v in a.data['vjournal']:
			print vjlist['0'] + vjlist[v.data['name']] \
				+ ' <b>' + v.data['volume'] + '</b>, ' \
				+ v.data['issue'] + ' (' + v.data['year'] +');'
		print '    <dd>' + abstract
		print '    </dl>'
		print '  </li>'
	print '</ol>'

def print_text (xh):
	i = 0
	for a in xh.article:
		print i
		print 'Title: ' + a.data['title']
		print 'Authors: ' + a.data['author'].encode('utf-8')
		jd = a.data['journal'].data
		jn = jd['name']
		if jn in jlist_keys:
			jn = jlist[jn]
		print 'Journal: ' + jn + ' ' + jd['volume'] + ', ' \
			+ jd['page'] + ' (' + jd['year'] +')'
		print 'Link: ' + jd['link']
		for v in a.data['vjournal']:
			print vjlist['0'] + vjlist[v.data['name']] \
				+ ' ' + v.data['volume'] + ', ' \
				+ v.data['issue'] + ' (' + v.data['year'] +')'
		for u in a.data['url']:
			print 'URL: ' + u.data['name'] + ', ' + u.data['link']
		print 'Abstract: ' + a.data['abstract']
		print
		i = i + 1


class Journal:
	def __init__(self):
		self.data = {
			'name' : '',
			'volume' : '',
			'page' : '',
			'year' : 0,
			'link' : '',
		}
journal_keys = Journal().data.keys()

class vJournal:
	def __init__(self):
		self.data = {
			'name' : '',
			'volume' : '',
			'issue' : '',
			'year' : 0,
		}
vjournal_keys = vJournal().data.keys()

class URL:
	def __init__(self):
		self.data = {
			'name' : '',
			'link' : '',
		}
url_keys = URL().data.keys()

class Article:
	def __init__(self):
		self.data = {
			'author' : '',
			'title' : '',
			'abstract' : '',
			'journal' : Journal(),
			'vjournal' : [],
			'url' : [],
		}
article_keys = { 'author', 'title', 'abstract' }

def strip_space(s):
	return ' '.join(s.split())

class xml_Handler(handler.ContentHandler):
	def __init__(self):
		self.buf = ''
		self.par = ''
		self.article = []

	def startElement(self, name, attrs):
		if name == 'article':
			self.article.append(Article())
		elif name == 'journal':
			self.par = name
		elif name == 'vjournal':
			self.par = name
			self.article[-1].data[name].append(vJournal())
		elif name == 'url':
			self.par = name
			self.article[-1].data[name].append(URL())
		self.buf = ''

	def characters(self, c):
		self.buf = self.buf + c

	def endElement(self, name):
		ad = self.article[-1].data
		self.buf = strip_space(self.buf)
		if name in article_keys:
			ad[name] = self.buf
		elif (self.par == 'journal') and (name in journal_keys):
			ad[self.par].data[name] = self.buf
		elif (self.par == 'vjournal') and (name in vjournal_keys):
			ad[self.par][-1].data[name] = self.buf
		elif (self.par == 'url') and (name in url_keys):
			ad[self.par][-1].data[name] = self.buf
		if name in { 'journal', 'vjournal', 'url' }:
			self.par = ''


# main program

parser = argparse.ArgumentParser(description='Parse a publication list in XML format and convert into other formats.')
parser.add_argument('xmlfile', help='the XML file to be parsed')
parser.add_argument('--sql', action='store_true',
	help='Show the SQL commands.')
parser.add_argument('--commit', action='store_true',
	help='Execute the SQL commands.')
parser.add_argument('--text', action='store_true',
	help='Print out plain text.')
parser.add_argument('--html', action='store_true',
	help='Ordered list in HTML.')
args = parser.parse_args()

#print args

sys.stderr.write('Start Parsing...\n')

xh = xml_Handler()
xml_parser = xml.sax.make_parser()
xml_parser.setContentHandler(xh)
xml_parser.parse(args.xmlfile)

sys.stderr.write('Parsed %d titles\n' % len(xh.article))

if (args.text):
	print_text(xh)

if (args.html):
	print_html(xh)

if (args.sql):
	print_sql(xh)

connection = psqldb.connect(user='jmtang',database='django')
cursor = connection.cursor()

connection.close()

