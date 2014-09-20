#!/usr/bin/python


#    mypub_convert.py:
#      Convert a publication list between different formats
#        Input formats:  XML, SQL
#        Output formats: HTML, SQL, Plain, XML
#
#    Copyright (C) 2014  Jian-Ming Tang <jian.ming.tang@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import xml.sax
from xml.sax import handler
import sys, re, codecs
import argparse
import textwrap
import psycopg2 as psqldb

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

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

SQL_write = {
	'article': 'INSERT INTO mypub_article (Title,Author,Abstract,' \
		+ 'journal_id) VALUES (%s,%s,%s,%s) RETURNING id',
	'journal': 'INSERT INTO mypub_journal (Title,Volume,Page,Year,Link) ' \
		+ 'VALUES (%s,%s,%s,%s,%s) RETURNING id',
	'vj': 'INSERT INTO mypub_vj (Title,Volume,Issue,Year,article_id) ' \
		+ 'VALUES (%s,%s,%s,%s,%s)',
	'url': 'INSERT INTO mypub_url (Name,Link,article_id) ' \
		+ 'VALUES (%s,%s,%s)',
}

class Journal:
	def __init__(self):
		self.data = {
			'name' : '',
			'volume' : '',
			'page' : '',
			'year' : 0,
			'link' : '',
		}
# needs to be in fixed order for SQL insert
journal_keys = ['name', 'volume', 'page', 'year', 'link']

class vJournal:
	def __init__(self):
		self.data = {
			'name' : '',
			'volume' : '',
			'issue' : '',
			'year' : 0,
		}
vj_keys = ['name', 'volume', 'issue', 'year']

class URL:
	def __init__(self):
		self.data = {
			'name' : '',
			'link' : '',
		}
url_keys = ['name', 'link']

class Article:
	def __init__(self):
		self.data = {
			'title' : '',
			'author' : '',
			'abstract' : '',
			'journal' : Journal(),
			'vjournal' : [],
			'url' : [],
		}
article_keys = [ 'title', 'author', 'abstract' ]


def print_sql(plist):
	for a in reversed(plist):
		pJ = [ a.data['journal'].data[k] for k in journal_keys ]
		if pJ[0] in jlist_keys:
			pJ[0] = jlist[pJ[0]]
		print SQL_write['journal'], pJ
		pA = [ a.data[k] for k in article_keys ] + ['jid']
		print SQL_write['article'], pA
		for v in a.data['vjournal']:
			pV = [ v.data[k] for k in vj_keys ] + ['aid']
			print SQL_write['vj'], pV
		for u in a.data['url']:
			pU = [ u.data[k] for k in url_keys ] + ['aid']
			print SQL_write['url'], pU

def sql_commit(cursor, plist):
	cursor.execute('BEGIN TRANSACTION;')
	for a in reversed(plist):
		pJ = [ a.data['journal'].data[k] for k in journal_keys ]
		if pJ[0] in jlist_keys:
			pJ[0] = jlist[pJ[0]]
		cursor.execute(SQL_write['journal'],pJ)
		jid = cursor.fetchone()[0]
		pA = [ a.data[k] for k in article_keys ] + [jid]
		cursor.execute(SQL_write['article'],pA)
		aid = cursor.fetchone()[0]
		for v in a.data['vjournal']:
			pV = [ v.data[k] for k in vj_keys ] + [aid]
			cursor.execute(SQL_write['vj'],pV)
		for u in a.data['url']:
			pU = [ u.data[k] for k in url_keys ] + [aid]
			cursor.execute(SQL_write['url'],pU)
	cursor.execute('COMMIT;')

def sql_query(cursor):
	plist = []
	sA = 'SELECT * from mypub_article ORDER BY id ASC'
	sJ = 'SELECT * from mypub_journal WHERE id = %s'
	sV = 'SELECT * from mypub_vj WHERE article_id = %s ORDER BY id ASC'
	sU = 'SELECT * from mypub_url WHERE article_id = %s ORDER BY id ASC'
	cursor.execute(sA)
	alist = cursor.fetchall()
	for a in reversed(alist):
		art = Article()
		art.data['title'] = a[1]
		art.data['author'] = a[2]
		art.data['abstract'] = a[3]
		cursor.execute(sJ,[a[4]])
		j = cursor.fetchone()
		art.data['journal'].data['name'] = j[1]
		art.data['journal'].data['volume'] = j[2]
		art.data['journal'].data['page'] = j[3]
		art.data['journal'].data['year'] = str(j[4])
		art.data['journal'].data['link'] = j[5]
		cursor.execute(sV,[a[0]])
		vlist = cursor.fetchall()
		for v in vlist:
			vj = Journal()
			vj.data['name'] = v[1]
			vj.data['volume'] = v[2]
			vj.data['issue'] = v[3]
			vj.data['year'] = str(v[4])
			art.data['vjournal'].append(vj)
		cursor.execute(sU,[a[0]])
		ulist = cursor.fetchall()
		for u in ulist:
			url = URL()
			url.data['name'] = u[1]
			url.data['link'] = u[2]
			art.data['url'].append(url)
		plist.append(art)
	return plist

def fix_HTML(s):
	s = re.sub(r'\$(.*?)_{(.*?)}(.*?)\$', r'$\1<sub>\2</sub>\3$',s)
	s = re.sub(r'\$(.*?)\^{(.*?)}(.*?)\$', r'$\1<sup>\2</sup>\3$',s)
	s = re.sub(r'\$(.*?)\$', r'<i>\1</i>',s)

#	p = s.find('$_{')
#	while p >= 0:
#		ns = s[0:p] + '<sub><i>' + s[p+3:]
#		p = ns.find('}$')
#		s = ns[0:p] + '</i></sub>' + ns[p+2:]
#		p = s.find('$_{')
#
#	p = s.find('$^{')
#	while p >= 0:
#		ns = s[0:p] + '<sup><i>' + s[p+3:]
#		p = ns.find('}$')
#		s = ns[0:p] + '</i></sup>' + ns[p+2:]
#		p = s.find('$^{')
#
#	p = s.find('$')
#	while p >= 0:
#		ns = s[0:p] + '<i>' + s[p+1:]
#		p = ns.find('$')
#		s = ns[0:p] + '</i>' + ns[p+1:]
#		p = s.find('$')

#	s = s.replace('\\bar{1}',u'1\u0305')
	s = s.replace('\\bar{1}',
		'<span style="text-decoration: overline">1</span>')
	s = s.replace('\\delta','<math><mi>&delta;</mi></math>')
	s = s.replace('\\AA{}','&Aring;')
	s = s.replace('\\%','%')
	s = s.replace(u'\u00e9','&eacute;')
	s = s.replace(u'\u00c7','&Ccedil;')

#	p = s.find('\\delta')
#	while p >= 0:
#		ns = s[0:p] + '<math>&delta;</math>' + s[p+6:]
#		s = ns
#		p = s.find('\\delta')
#
#	p = s.find('\AA{}')
#	while p >= 0:
#		ns = s[0:p] + '&Aring;' + s[p+5:]
#		s = ns
#		p = s.find('\AA{}')
#
#	p = s.find(u'\u00e9')
#	while p >= 0:
#		ns = s[0:p] + '&eacute;' + s[p+1:]
#		s = ns
#		p = s.find(u'\u00e9')
#
#	p = s.find(u'\u00c7')
#	while p >= 0:
#		ns = s[0:p] + '&Ccedil;' + s[p+1:]
#		s = ns
#	 	p = s.find(u'\u00c7')
	return s

def print_html(plist):
	print '<!DOCTYPE html>'
	print '<html>'
	print '<body>'
	print '<h1>Publication List:</h1>'
	print '<ol>'
	for a in plist:
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
		print '<br>'
		for v in a.data['vjournal']:
			print vjlist['0'] + vjlist[v.data['name']] \
				+ ' <b>' + v.data['volume'] + '</b>, ' \
				+ v.data['issue'] + ' (' + v.data['year'] +');'
		print '    <dd>' + abstract
		print '    </dl>'
		print '  </li>'
	print '</ol>'
	print '</body>'
	print '</html>'

def my_indent_print(m,n,s):
	w = textwrap.TextWrapper(width = 80 - max(m,n))
	w.initial_indent = ' ' * m
	w.subsequent_indent = ' ' * n
	w.break_long_words = False
	w.break_on_hyphens = False
	for l in w.wrap(s):
		print l
#		print l.encode('utf-8')

def print_text(plist):
	i = 0
	for a in plist:
		print i
		my_indent_print(0,2,'Title: '+a.data['title'])
		my_indent_print(0,2,'Authors: '+a.data['author'])
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
		my_indent_print(0,2,'Abstract: '+a.data['abstract'])
		print
		i = i + 1

def print_xml(plist):
	print '<?xml version="1.0" encoding="UTF-8"?>'
	print
	print '<publist>'
	print
	for a in plist:
		print '<article>'
		print '  <title>'
		my_indent_print(4,4,a.data['title'])
		print '  </title>'
		print '  <author>'
		my_indent_print(4,4,a.data['author'])
		print '  </author>'
		jd = a.data['journal'].data
		print '  <journal>'
		print '    <name>' + jd['name'] + '</name>' \
			+ '<volume>' + jd['volume'] + '</volume>'
		print '    <page>' + jd['page'] + '</page>' \
			+ '<year>' + jd['year'] +'</year>'
		print '    <link>' + jd['link'] + '</link>'
		print '  </journal>'
		for v in a.data['vjournal']:
			print '  <vjournal>'
			print '    <name>' + v.data['name'] + '</name>' \
				+ '<volume>' + v.data['volume'] + '</volume>'
			print '    <issue>' + v.data['issue'] + '</issue>' \
				+ '<year>' + v.data['year'] +'</year>'
			print '  </vjournal>'
		for u in a.data['url']:
			print '  <url>'
			print '    <name>' + u.data['name'] + '</name>'
			print '    <link>' + u.data['link'] + '</link>'
			print '  </url>'
		print '  <abstract>'
		my_indent_print(4,4,a.data['abstract'])
		print '  </abstract>'
		print '</article>'
		print
	print
	print '</publist>'


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
# old format
#		elif name == 'pdf':
#			self.article[-1].data['url'].append(URL())
		elif name == 'url':
			self.par = name
			self.article[-1].data[name].append(URL())
		self.buf = ''

	def characters(self, c):
		self.buf = self.buf + c

	def endElement(self, name):
		ad = self.article[-1].data
		self.buf = ' '.join(self.buf.split())
		if name in article_keys:
			ad[name] = self.buf
		elif (self.par == 'journal') and (name in journal_keys):
			ad[self.par].data[name] = self.buf
		elif (self.par == 'vjournal') and (name in vj_keys):
			ad[self.par][-1].data[name] = self.buf
# old format
#		elif name == 'pdf':
#			ad['url'][-1].data['name'] = '[Full Text]'
#			ad['url'][-1].data['link'] = self.buf
		elif (self.par == 'url') and (name in url_keys):
			ad[self.par][-1].data[name] = self.buf
		if name in { 'journal', 'vjournal', 'url' }:
			self.par = ''


def parse_xml(xmlfile):
	xh = xml_Handler()
	xml_parser = xml.sax.make_parser()
	xml_parser.setContentHandler(xh)
	sys.stderr.write('Start Parsing...\n')
	xml_parser.parse(xmlfile)
	sys.stderr.write('Parsed %d titles\n' % len(xh.article))
	return xh.article

def read_db(dbname):
	connection = psqldb.connect(user='jmtang',database=dbname)
	cursor = connection.cursor()
# In Python 2, the default return type is str, not unicode.
	psqldb.extensions.register_type(psqldb.extensions.UNICODE, cursor)
	plist = sql_query(cursor)
	connection.close()
	return plist

def write_db(dbname, plist):
	connection = psqldb.connect(user='jmtang',database=dbname)
	cursor = connection.cursor()
	sql_commit(cursor, plist)
	connection.close()


# main program

parser = argparse.ArgumentParser(description=
	'Convert a publication list between different formats. \
	Input formats: XML, SQL; Output formats: HTML, SQL, Plain, XML;')
parser.add_argument('--from-xml', metavar='xmlfile',
	help='input from a XML file')
parser.add_argument('--from-db', metavar='database',
	help='input from a database')
parser.add_argument('--to-db', metavar='database',
	help='output to a database')
parser.add_argument('--html', action='store_true',
	help='output HTML format')
parser.add_argument('--sql', action='store_true',
	help='output SQL commands')
parser.add_argument('--text', action='store_true',
	help='output Plain Text')
parser.add_argument('--xml', action='store_true',
	help='output XML format')
args = parser.parse_args()


# processing input
if (args.from_xml != None):
	plist = parse_xml(args.from_xml)
elif (args.from_db != None):
	plist = read_db(args.from_db)
else:
	sys.stderr.write('\nMissing input source (--from-) !!!\n\n')
	parser.print_usage(sys.stderr)
	exit(1)

# processing output
if (args.html):
	print_html(plist)
elif (args.sql):
	print_sql(plist)
elif (args.to_db != None):
	write_db(args.to_db, plist)
elif (args.text):
	print_text(plist)
elif (args.xml):
	print_xml(plist)
else:
	sys.stderr.write('\nOutput format not specified !!!\n\n')
	parser.print_usage(sys.stderr)
	exit(1)

