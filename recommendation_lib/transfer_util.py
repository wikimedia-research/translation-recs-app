import os

fr = 'stat1002.eqiad.wmnet:/home/ellery/translation-recs-app/data'
to = '/Users/ellerywulczyn/translation-recs-app/data'

t_dict = {'en': ['fr', 'es', 'simple'], 'simple': ['fr', 'es'],}

def transfer(fr, to, fname):
    from_fname = os.path.join(fr, fname)
    to_fname = os.path.join(to, fname)
    cmd = 'scp %s %s' % (from_fname, to_fname)
    print (cmd)
    os.system(cmd)


# create directories
for s in t_dict.keys():
    for s in t_dict.keys():
        directory = os.path.join(to, s)
        if not os.path.exists(directory):
            os.makedirs(directory)
        for t in t_dict[s]:
            directory = os.path.join(to, s, t)
            if not os.path.exists(directory):
                os.makedirs(directory)


# language models
lm_files = ['article2index.txt', 'doc2topic.mtx']
for s in t_dict.keys():
    for f in lm_files:
        fname = os.path.join(s, f)
        try:
            transfer(fr, to, fname)
        except:
            print('Could not transfer %s' %fname)


# ranked missing

rank_files = [ 'ranked_missing_items.tsv']
for s in t_dict.keys():
    for t in t_dict[s]:
        for f in rank_files:
            fname = os.path.join(s, t, f)
            try:
                transfer(fr, to, fname)
            except:
                print('Could not transfer %s' % fname)
    

