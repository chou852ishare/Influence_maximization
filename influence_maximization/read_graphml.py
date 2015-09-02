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


def make_simple(graph):
    print '**********************************'
    isSimple = graph.is_simple()
    print 'The graph is simple:', isSimple
    if not isSimple:
        graph.simplify(multiple=True, loops=True, combine_edges=sum)
        print 'The graph is simple (after simplifying):', graph.is_simple()


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
        print 'feedback-arc-set size: ', len(fas)
        graph.delete_edges(fas)
        print 'The graph is a DAG (after remove feedback-arc-set):', graph.is_dag()
    print summary(graph)


def normalize_in_a_process(start, step, graph, wseq):
    # sort by target
    for v in graph.vs[start::step]:
        eseq    = graph.es(_target=v.index)
        sumw    = sum(eseq['weight'])
        for e in eseq:
            wseq[e.index] = e['weight'] / sumw


def normalize_inweight(graph):
    print '**********************************'
    print 'normalizing in-weights in parallel mode'
    print 'wait...'
    mgr  = Manager()
    wseq = mgr.list(range(len(graph.es)))
    np   = 24
    p    = Pool()
    for start in xrange(np):
        p.apply_async(normalize_in_a_process, args=(start, np, graph, wseq))
    p.close()
    p.join()
    graph.es['normalized inweight'] = wseq
    print 'Done!'
    print summary(graph)


def preprocess(fname):
    gfile = fname
    g = read_graph(gfile)
    make_simple(g)
    normalize_inweight(g)
    #break_cycle(g)
    return g


def main():
    fname = 'SAMPIN.GraphML'
    preprocess(fname)


if __name__ == '__main__':
    main()
