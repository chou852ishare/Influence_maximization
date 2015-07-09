from igraph import *


def read_graph(gfile):
    print '**********************************'
    graph = Graph.Read_GraphML(gfile)
    print summary(graph)
    ISDIR = graph.is_directed()
    print 'The graph is directed:', ISDIR
    if not ISDIR:
        graph = graph.as_directed()
    print 'The graph is directed (after as_directed()):', graph.is_directed()
    return graph


def break_cycle(graph):
    print '**********************************'
    FDAG = graph.is_dag()
    print 'The graph is a DAG:', FDAG
    if FDAG:
        # nothing to do
        pass
    else:
        # need to remove feedback_arc_set
        # for cycle breaking
        print 'breaking cycles...'
        fas = graph.feedback_arc_set(weights='weight')
        graph.delete_edges(fas)
        print 'The graph is a DAG (after remove feedback-arc-set):', graph.is_dag()
        print summary(graph)


def normalize_inweight(graph):
    print '**********************************'
    print 'normalizing in-weight...'
    # sort by target
    for v in graph.vs:
        eseq    = graph.es(_target=v.index)
        sumw    = sum(eseq['weight'])
        eseq['normalized inweight'] = [w/sumw for w in eseq['weight']]
    print summary(graph)


def preprocess(fname):
    path = './data'
    gfile = path + fname
    g = read_graph(gfile)
    break_cycle(g)
    normalize_inweight(g)
    return len(g.vs), [e.source for e in g.es], [e.target for e in g.es], [w for w in g.es['normalized inweight']]


def main():
    fname = 'SAMPIN.GraphML'
    preprocess(fname)


if __name__ == '__main__':
    main()
