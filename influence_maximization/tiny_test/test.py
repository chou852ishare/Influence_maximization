import igraph
import cplex
import read_graphml
import cplex_tiny


fname = '/bkfrat-GraphML/BKFRAB.GraphML' # 'SAMPIN.GraphML'
# get directed weighted network
size, source, target, weight = read_graphml.preprocess(fname)

# influence maximization
cplex_tiny.optimize(size, source, target, weight)
