import sys, os
import logging
logger = logging.getLogger(__name__)


langs = sys.argv[2].split(',')
ftype = sys.argv[1] #wiki-latest-pages-articles-multistream.xml.bz2

ret = 0

for lang in langs:
	logger.info('Start:Download dump for s = %s' % lang)
    url = 'https://dumps.wikimedia.org/%(lang)swiki/latest/%(lang)s%(ftype)s' % {'lang': lang, 'ftype':ftype}
    destdir = '/user/ellery/translation-recs-app/data/%s' % lang
    os.system('hadoop fs -mkdir %s' % destdir)
    destfile = "%(dest)s/%(lang)s%(ftype)s" % {'ftype':ftype[:-4], 'dest': destdir, 'lang': lang}
    os.system('hadoop fs -rm -r %s' % destfile)
    ret += os.system("wget -O - %(url)s | bunzip2 | hadoop fs -put - %(destfile)s" % {'url': url,  'destfile': destfile})
    logger.info('End: Download dump for s = %s' % lang)

assert ret == 0, 'error in downloading dump'