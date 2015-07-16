import sys, os

langs = sys.argv[2].split(',')
ftype = sys.argv[1] #wiki-latest-pages-articles-multistream.xml.bz2

for lang in langs:
	url = 'https://dumps.wikimedia.org/%(lang)swiki/latest/%(lang)s%(ftype)s' % {'lang': lang, 'ftype':ftype}
	dest = '/user/ellery/translation-recs-app/data/%s' % lang
	os.system('hadoop fs -mkdir %s' % dest)
	os.system("wget -O - %(url)s | bunzip2 | hadoop fs -put - %(dest)s/%(lang)s%(ftype)s" % {'url': url, 'ftype':ftype, 'dest': dest, 'lang': lang})