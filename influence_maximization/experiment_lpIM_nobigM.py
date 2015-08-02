import numpy as np
import cPickle as pickle
import os
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


# paramters of IM
S = 5
T = 1

netname = 'astrocollab'
#netname = 'astrocollab'
#netname = 'astrocollab'
#netname = 'astrocollab'
fname = './data/%s-GraphML/%s.GraphML' % (netname, netname) 
pname = './data/%s-GraphML/%s.pickle' % (netname, netname)
if not os.path.exists(pname):
    # get directed weighted network
    g = read_graphml.preprocess(fname)
    pickle.dump(g, open(pname, 'wb'))

g = pickle.load(open(pname))
size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]
print 'g is a DAG:', g.is_dag()

# influence maximization - original
ssLp = lpIM_nobigM.optimize(S, T, size, source, target, weight)

# influence maximization - original
ssMip = mipIM_nobigM.optimize(S, T, size, source, target, weight)


# double check
# sort nodes by sum(out-weight)
print '*********************************************************************************************'
print 'Double check through intuition (sorted out-weights)'
def reverse_comp(x, y):
    if x[1] > y[1]:
        return -1
    if x[1] < y[1]:
        return 1
    return 0

node_sumw   = []
ssMaxWeight = []
#for v in g.vs:
#    node_sumw.append((v.index, sum(g.es(_source = v.index)['normalized inweight'])))
#node_sumw.sort(reverse_comp)
#for i in xrange(S):
#    ssMaxWeight.append(node_sumw[i][0])
#    print node_sumw[i]


# calculate expected spread 
calculate_LT.run(ssLp, S, T, size, source, target, weight)
print 'seed set selected by LP_nobigM'
#calculate_LT.run(ssMaxWeight, S, T, size, source, target, weight)
#print 'seed set selected by max weighted degree'
#calculate_LT.run(ssMip, S, T, size, source, target, weight)
#print 'seed set selected by original MIP_nobigM'
