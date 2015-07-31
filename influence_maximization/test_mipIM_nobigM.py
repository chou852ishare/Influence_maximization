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
S = 6
T = 10


fname = '/bkfrat-GraphML/BKFRAB.GraphML' # 'SAMPIN.GraphML'
# get directed weighted network
g = read_graphml.preprocess(fname)
print 'g is a DAG:', g.is_dag()


# influence maximization - original
size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]
ssCplex = cplex_tiny.optimize(S, T, size, source, target, weight)


# influence maximization - original
ssMip = mipIM_nobigM.optimize(S, T, size, source, target, weight)


# calculate expected spread 
calculate_LT.run(ssCplex, S, T, size, source, target, weight)
print 'seed set selected by Cplex'
calculate_LT.run(ssMip, S, T, size, source, target, weight)
print 'seed set selected by MIP_nobigM'
