import igraph
import cplex
import read_graphml

fname = 'SAMPIN.GraphML'
# get directed weighted network
source, target, weight = read_graphml.preprocess(fname)

# influence maximization
cplex_tiny(source, target, weight)
