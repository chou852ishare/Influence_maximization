import numpy as np
import cPickle as pickle
from datetime import datetime
from multiprocessing import Pool, Manager

def load_graph(netname):
    pname = './data/%s-GraphML/%s.pickle' % (netname, netname)
    return pickle.load(open(pname))
   
def process_i(i, step, nw, g):
    for v in g.vs[i::step]:
        nw.append((v.index, sum(g.es(_source = v.index)['normalized inweight'])))
    print 'subprocess %s done' % i

def gen_outweight_seq(g):
    t0 = datetime.now()
    mg = Manager()
    nw = mg.list()
    np = 20
    p  = Pool(np)
    for i in xrange(np):
        p.apply_async(process_i, args=(i, np, nw, g))
    p.close()
    p.join()
    t1 = datetime.now()
    print 'Construction time for inweight sequence: ', (t1-t0).seconds
    return nw
    

def sort_owseq(owseq, S):
    t1 = datetime.now()
    dtype = [('v index', int), ('weight', float)]
    warr  = np.array(owseq, dtype = dtype)
    sarr  = np.sort(warr, order = 'weight')
    t2 = datetime.now()
    ss = sarr[-S:]
    print 'seed set selected by max weighted degree: ', ss
    print 'influence spread: ', reduce(lambda x,y: (0, x[1]+y[1]), ss)[1] + S
    print 'Sort time: ', (t2-t1).seconds
    return ss

def run(netname, S):
    g       = load_graph(netname)
    owseq   = gen_outweight_seq(g)
    ss      = sort_owseq(owseq, S)


if __name__ == '__main__':
    run('astrocollab', 5)

