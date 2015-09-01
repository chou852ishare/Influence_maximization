from datetime import datetime
from multiprocessing import Manager, Pool
import numpy as np
import cPickle as pickle
import os
import sys
import igraph
import cplex
import read_graphml
import cplex_tiny
import bendersIM
import bendersIM_exactWorker
import bendersIM_CB
import bendersIM_nobigM
import lpIM_nobigM
import mipIM_nobigM
import calculate_LT
import ncol


def set_ST(s, t, net, mth):
    # paramters of IM
    global S, T, netname, method
    S = s
    T = t
    netname = net
    method  = mth


def gen_graph():
    #netname = 'astrocollab'
    #fname = './data/%s-GraphML/%s.GraphML' % (netname, netname) 
    #pname = './data/%s-GraphML/%s.pickle' % (netname, netname)
    #if not os.path.exists(pname):
    #    # get directed weighted network
    #    g = read_graphml.preprocess(fname)
    #    pickle.dump(g, open(pname, 'wb'))

    # generate graph from ncol edgelist
    fname = './data/%s-GraphML/%s.inf' % (netname, netname) 
    ename = './data/%s-GraphML/%s.edgelist' % (netname, netname)
    gname = './data/%s-GraphML/%s.GraphML' % (netname, netname)
    pname = './data/%s-GraphML/%s.pickle' % (netname, netname)
    if not os.path.exists(pname):
        # get directed weighted network
        ncol.run(fname, ename, gname)
        g = read_graphml.preprocess(gname)
        pickle.dump(g, open(pname, 'wb'))
    return pname


def load_graph(pname):
    # load graph and get properties
    g = pickle.load(open(pname))
    size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]
    print 'g is a DAG:', g.is_dag()
    return g, size, source, target, weight


def write_result(netname, method, dInf, seedSet, sol_time):
    # output results to file
    pout = './output/%s' % netname
    if not os.path.exists(pout):
        os.mkdir(pout)
        
    # output delta influence
    f_delta = open('%s/%s_%s_%s_%s.deltaInf' % (pout, netname, S, T, method), 'w')
    for d in dInf:
        print >> f_delta, d
    f_delta.close()
    
    # output seedset
    f_ss = open('%s/%s_%s_%s_%s.seedset' % (pout, netname, S, T, method), 'w')
    for s in seedSet:
        if s == seedSet[-1]:
            print >> f_ss, s, sol_time, sum(dInf)
        else:
            print >> f_ss, s
    f_ss.close()


def get_result_fix(g, size, source, target, weight, ssfile):
    # calculate spread of fixed seed set
    t_start   = datetime.now()
    ssFX_name = map(lambda s: g.vs[s]['name'], ssMW)
    ssFX      = map(lambda sn: g.vs['name'=sn], ssFX_name)
    t_end     = datetime.now()
    dInf      = calculate_spread(ssMW, size, source, target, weight)
    write_result(netname, 'weight', dInf, ssMW_name, (t_end - t_start).seconds)


def calculate_spread(ss, size, source, target, weight):
    # calculate expected spread
    return calculate_LT.run(ss, S, T, size, source, target, weight)


def run_fix(ssfile):
    print 'Selecte seed set by max-weighted-dgree'
    pname = gen_graph()
    g, size, source, target, weight = load_graph(pname)
    get_result_fix(g, size, source, target, weight, ssfile)
    print 'Done! seed set selected by MAX-weighted-degree'


if __name__ == '__main__':
    set_ST(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4])
    if sys.argv[4] == 'greedy':
        ssfile = open('./goyal_package/output/%s/%s_%s_%s_%s/LT_Greedy.txt' % (netname, netname, S, T, method))
    elif sys.argv[4] == 'simpath':
        ssfile = open('./goyal_package/output/%s/%s_%s_%s_%s/LTNew_SimPath_4_0.001.txt' % (netname, netname, S, T, method))
    elif sys.argv[4] == 'ldag':
        ssfile = open('./goyal_package/output/%s/%s_%s_%s_%s/ldag_0.003125.txt' % (netname, netname, S, T, method))
    run_fix(ssfile)

