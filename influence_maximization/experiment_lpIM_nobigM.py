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
import numpy_sort


def set_ST(s, t, net):
    # paramters of IM
    global S, T, netname
    S = s
    T = t
    netname = net


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


def get_result_lp(g, size, source, target, weight):
    # influence maximization - LP relaxation
    t_start         = datetime.now()
    ssLp, pLp, dInf = lpIM_nobigM.optimize(S, T, size, source, target, weight)
    ssLp_name       = map(lambda s: g.vs[s]['name'], ssLp)
    t_end           = datetime.now()
    seed_prob       = map(lambda i: str(ssLp_name[i]) + '_' + str(pLp[i]), xrange(len(ssLp)))
    write_result(netname, 'lp', dInf, seed_prob, (t_end - t_start).seconds)
    
    # influence maximization - MAX-LP
    dtype           = [('index', 'int'), ('name', 'int'), ('prob', 'float')]
    vseed_prob      = map(lambda i: (ssLp[i], ssLp_name[i], pLp[i]), xrange(len(ssLp)))
    vseed_prob_arr  = np.array(vseed_prob, dtype = dtype)
    vseed_prob_sort = np.sort(vseed_prob_arr, order = 'prob')
    ssMaxlp_name    = map(lambda i: vseed_prob_sort[-i-1][1], xrange(S))
    ssMaxlp         = map(lambda i: int(vseed_prob_sort[-i-1][0]), xrange(S))
    dInf            = calculate_spread(ssMaxlp, size, source, target, weight)
    t_end1          = datetime.now()
    write_result(netname, 'maxlp', dInf, ssMaxlp_name, (t_end1 - t_start).seconds)


def get_result_mip(g, size, source, target, weight):
    # influence maximization - original MIP
    t_start         = datetime.now()
    ssMip, dInf     = mipIM_nobigM.optimize(S, T, size, source, target, weight)
    ssMip_name      = map(lambda s: g.vs[s]['name'], ssMip)
    t_end           = datetime.now()
    write_result(netname, 'mip', dInf, ssMip_name, (t_end - t_start).seconds)


def process_i(i, g, inweights, outweights, numprocess):
    for i in xrange(i, len(g.vs), numprocess):
        v             = g.vs[i]
        inweights[i]  = [(e.source, e['normalized inweight']) for e in g.es(_target = v.index)]
        outweights[i] = [(e.target, e['normalized inweight']) for e in g.es(_source = v.index)]
    

def gen_ioweight(g):
    # influence maximization - approximate benders
    # form of inweights (example):
    # node  [(in-node1, in-weight1) (in-node2, in-weight2) ...]
    # 0     [(1,0.3) (3,0.4) (7,0.9) ...]
    # 1     [(2,0.2) (6,0.2) (8,0.1) ...]
    # 2     [(1,0.3) (3,0.4) ...]
    # ...
    print 'Start... Generating in/out-weights'
    manager     = Manager()
    inweights   = manager.list(range(len(g.vs)))
    outweights  = manager.list(range(len(g.vs)))
    numprocess  = 20
    pool        = Pool(numprocess)
    for i in xrange(numprocess):
        pool.apply_async(process_i, args=(i, g, inweights, outweights, numprocess))
    pool.close()
    pool.join()
    print 'Done! Generating in/out-weights'
    print inweights[:3]
    return inweights, outweights


def get_result_benders(g, size, source, target, weight, sepflag, inweights, outweights):
    t_start         = datetime.now()
    ssBenders       = bendersIM.optimize(S, T, sepflag, inweights, outweights)
    ssBenders_name  = map(lambda s: g.vs[s]['name'], ssBenders)
    t_end           = datetime.now()
    dInf            = calculate_spread(ssBenders, size, source, target, weight)
    write_result(netname, 'benders', dInf, ssBenders_name, (t_end - t_start).seconds)


def get_result_base():
    # sort nodes by sum(out-weight)
    print 'Baseline (max out-weights)'
    ssMW      = numpy_sort.run(netname, S)
    ssMW_name = map(lambda s: g.vs[s]['name'], ssMW)
    return ssMW, ssMW_name


def calculate_spread(ss, size, source, target, weight):
    # calculate expected spread
    return calculate_LT.run(ss, S, T, size, source, target, weight)


def run_lp():
    print 'Selecte seed set by LP-relaxation'
    pname = gen_graph()
    g, size, source, target, weight = load_graph(pname)
    get_result_lp(g, size, source, target, weight)
    print 'Done! seed set selected by LP-relaxation and MAX-LP'


def run_mip():
    print 'Selecte seed set by original-MIP'
    pname = gen_graph()
    g, size, source, target, weight = load_graph(pname)
    get_result_mip(g, size, source, target, weight)
    print 'Done! seed set selected by original-MIP'


def run_benders():
    print 'Selecte seed set by approx-Benders'
    pname = gen_graph()
    g, size, source, target, weight = load_graph(pname)
    inweights, outweights = gen_ioweight(g)
    sepflag = 0
    get_result_benders(g, size, source, target, weight, sepflag, inweights, outweights)
    print 'Done! seed set selected by approx-Benders'


if __name__ == '__main__':
    set_ST(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    if sys.argv[4] == 'lp':
        run_lp()
    elif sys.argv[4] == 'mip':
        run_mip()
    elif sys.argv[4] == 'benders':
        run_benders()
