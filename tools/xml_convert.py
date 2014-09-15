#!/usr/bin/python


#    xml_convert.py:
#    Convert a publication list in XML format into other formats.
#    Copyright (C) <2014>  <Jian-Ming Tang>
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
import sys, re
import argparse
import textwrap
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
			'title' : '',
			'author' : '',
			'abstract' : '',
			'journal' : Journal(),
			'vjournal' : [],
			'url' : [],
		}
article_keys = [ 'title', 'author', 'abstract' ]


# SQL format for ' is ''
def sql_query(xh):
	xh.article.reverse()
	s1 = 'INSERT INTO mypub_article (Title,Author,Abstract,Note) ' \
		+ 'VALUES (%s,%s,%s,%s) RETURNING id'
	s2 = 'INSERT INTO mypub_journal (Name,Volume,Page,Year,Link) ' \
		+ 'VALUES (%s,%s,%s,%s,%s,%s) RETURNING id'
	for a in xh.article:
		p1 = [ a.data[k] for k in article_keys ] + ['']
		print p1
		cursor.execute('BEGIN TRANSACTION;')
		cursor.execute(s1,p1)
		a_id = cursor.fetchone()[0]
		print a_id
	if (args.commit):
		cursor.execute('COMMIT;')


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
	s = s.replace('\\delta','<math>&delta;</math>')
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

def print_html(xh):
	print '<!DOCTYPE html>'
	print '<html>'
	print '<body>'
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
		print '    <dd><i>' + author.encode('utf-8') + '</i>'
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
		print '    <dd>' + abstract.encode('utf-8')
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
		print l.encode('utf-8')

def print_text(xh):
	i = 0
	for a in xh.article:
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

def print_xml(xh):
	print '<?xml version="1.0" encoding="UTF-8"?>'
	print
	print '<publist>'
	print
	for a in xh.article:
		print '<article>'
		print '  <title>'
		my_indent_print (4,4,a.data['title'])
		print '  </title>'
		print '  <author>'
		my_indent_print (4,4,a.data['author'])
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
		my_indent_print (4,4,a.data['abstract'])
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
		elif (self.par == 'vjournal') and (name in vjournal_keys):
			ad[self.par][-1].data[name] = self.buf
# old format
#		elif name == 'pdf':
#			ad['url'][-1].data['name'] = '[Full Text]'
#			ad['url'][-1].data['link'] = self.buf
		elif (self.par == 'url') and (name in url_keys):
			ad[self.par][-1].data[name] = self.buf
		if name in { 'journal', 'vjournal', 'url' }:
			self.par = ''


# main program

parser = argparse.ArgumentParser(description=
	'Convert a publication list in XML format into other formats.')
parser.add_argument('xmlfile', help='the XML file to be parsed')
parser.add_argument('--commit', action='store_true',
	help='Commit SQL commands')
parser.add_argument('--html', action='store_true',
	help='HTML format')
parser.add_argument('--sql', action='store_true',
	help='Show SQL commands')
parser.add_argument('--text', action='store_true',
	help='Plain Text')
parser.add_argument('--xml', action='store_true',
	help='XML format')
args = parser.parse_args()


xh = xml_Handler()
xml_parser = xml.sax.make_parser()
xml_parser.setContentHandler(xh)


sys.stderr.write('Start Parsing...\n')
xml_parser.parse(args.xmlfile)
sys.stderr.write('Parsed %d titles\n' % len(xh.article))


if (args.html):
	print_html(xh)

if (args.text):
	print_text(xh)

if (args.xml):
	print_xml(xh)

if (args.sql):
	connection = psqldb.connect(user='jmtang',database='django')
	cursor = connection.cursor()
	sql_query(xh)
	connection.close()
