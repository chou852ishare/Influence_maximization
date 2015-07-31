import numpy as np
import cPickle as pickle
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
T = 10


fname = '/astrocollab-GraphML/astrocollab.GraphML' 
#fname = '/hepcollab-GraphML/hepcollab.GraphML' 
#fname = '/netscience-GraphML/netscience.GraphML' 
#fname = '/bkfrat-GraphML/BKFRAB.GraphML' # 'SAMPIN.GraphML'
# get directed weighted network
g = read_graphml.preprocess(fname)
print 'g is a DAG:', g.is_dag()


size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]

# influence maximization - original
ssLp = lpIM_nobigM.optimize(S, T, size, source, target, weight)

# influence maximization - original
#ssMip = mipIM_nobigM.optimize(S, T, size, source, target, weight)


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

node_sumw = []
for v in g.vs:
    node_sumw.append((v.index, sum(g.es(_source = v.index)['normalized inweight'])))
node_sumw.sort(reverse_comp)
for i in xrange(S):
    print node_sumw[i]


# calculate expected spread 
calculate_LT.run(ssMip, S, T, size, source, target, weight)
print 'seed set selected by original MIP_nobigM'
calculate_LT.run(ssLp, S, T, size, source, target, weight)
print 'seed set selected by LP_nobigM'
