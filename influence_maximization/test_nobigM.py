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
import calculate_LT


# paramters of IM
S = 10
T = 5


fname = '/bkfrat-GraphML/BKFRAB.GraphML' # 'SAMPIN.GraphML'
# get directed weighted network
g = read_graphml.preprocess(fname)
print 'g is a DAG:', g.is_dag()


# influence maximization - original
size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]
ssCplex = cplex_tiny.optimize(S, T, size, source, target, weight)


inweights   = []
outweights  = []
for v in g.vs:
    inweights.append([(e.source, e['normalized inweight']) for e in g.es(_target = v.index)])
    outweights.append([(e.target, e['normalized inweight']) for e in g.es(_source = v.index)])
# influence maximization - benders decomposition
sepflag = 0
snobigM = bendersIM_nobigM.optimize(S, T, sepflag, inweights, outweights)


# calculate expected spread 
calculate_LT.run(ssCplex, S, T, size, source, target, weight)
print 'seed set selected by Cplex'
calculate_LT.run(snobigM, S, T, size, source, target, weight)
print 'seed set selected by nobigM Benders'
