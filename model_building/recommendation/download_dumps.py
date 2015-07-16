import sys, os

langs = sys.argv[2].split(',')
ftype = sys.argv[1] #wiki-latest-pages-articles-multistream.xml.bz2

for lang in langs:
	url = 'https://dumps.wikimedia.org/%(lang)swiki/latest/%(lang)s%(ftype)s' % {'lang': lang, 'ftype':ftype}
	destdir = '/user/ellery/translation-recs-app/data/%s' % lang
	os.system('hadoop fs -mkdir %s' % destdir)
	destfile = "%(dest)s/%(lang)s%(ftype)s" % {'ftype':ftype[:-4], 'dest': destdir, 'lang': lang}
	os.system('hadoop fs -rm -r %s' % destfile)
	os.system("wget -O - %(url)s | bunzip2 | hadoop fs -put - %(destfil)s" % {'url': url,  'destfile': destfile})