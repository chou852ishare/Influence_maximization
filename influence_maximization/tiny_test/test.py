import igraph
import cplex
import read_graphml
import cplex_tiny
import bendersIM

fname = '/bkfrat-GraphML/BKFRAB.GraphML' # 'SAMPIN.GraphML'
# get directed weighted network
g = read_graphml.preprocess(fname)
print 'g is a DAG:', g.is_dag()


# influence maximization - original
size, source, target, weight = len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]
cplex_tiny.optimize(size, source, target, weight)


# influence maximization - benders decomposition
# form of inweights (example):
# node  [(in-node1, in-weight1) (in-node2, in-weight2) ...]
# 0     [(1,0.3) (3,0.4) (7,0.9) ...]
# 1     [(2,0.2) (6,0.2) (8,0.1) ...]
# 2     [(1,0.3) (3,0.4) ...]
# ...
inweights = []
for v in g.vs:
    inweights.append([(e.source, e['normalized inweight']) for e in g.es(_target = v.index)])
separate = 0
bendersIM.optimize(separate, inweights)


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
for i in xrange(5):
    print node_sumw[i]
