from igraph import *
from multiprocessing import Pool, Manager

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


def normalize_in_a_process(start, step, graph, wseq):
    print 'subprocess %s start...' % start
    # sort by target
    for v in graph.vs[start::step]:
        eseq    = graph.es(_target=v.index)
        sumw    = sum(eseq['weight'])
        for e in eseq:
            wseq[e.index] = e['weight'] / sumw
    print 'subprocess %s done' % start


def normalize_inweight(graph):
    print '**********************************'
    print 'normalizing in-weight...'
    mgr  = Manager()
    wseq = mgr.list(range(len(graph.es)))
    np   = 24
    p    = Pool()
    for start in xrange(np):
        p.apply_async(normalize_in_a_process, args=(start, np, graph, wseq))
    p.close()
    p.join()
    print len(wseq)
    print wseq[0:10]
    graph.es['normalized inweight'] = wseq
    print summary(graph)


def preprocess(fname):
    gfile = fname
    g = read_graph(gfile)
    break_cycle(g)
    normalize_inweight(g)
    return g


def main():
    fname = 'SAMPIN.GraphML'
    preprocess(fname)


if __name__ == '__main__':
    main()
