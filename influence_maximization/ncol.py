from igraph import Graph, summary
import cPickle as pickle


def gen_ncol(fn, fncol):
    fr = open(fn, 'r')
    fw = open(fncol, 'w')
    fr.readline()  # ignore first line if it is comment
    for line in fr.readlines():
        fw.write(line)
    fr.close()
    fw.close()


def gen_graph_from_nol(fncol):
    g = Graph()
    g = g.Read_Ncol(fncol, names=True, weights=True, directed=True)
    print summary(g)
    return g
     

def run(fname, ename, gname):
    gen_ncol(fname, ename)
    g = gen_graph_from_nol(ename)
    g.write_graphml(open(gname, 'w'))
    return g


if __name__ == '__main__':
    p     = './data/heplt2-edgelist/'
    fn    = p + 'hep_LT2.inf'
    fncol = p + 'heplt2.edgelist'
    gen_ncol(fn, fncol)
    gen_graph_from_nol(fncol)
