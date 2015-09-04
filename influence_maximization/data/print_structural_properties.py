from igraph import *

g = load('heplt2-GraphML/heplt2.GraphML')

print '# of nodes: ', len(g.vs)
print '# of edges: ', len(g.es)
print 'average degree: ', mean(g.degree())
print 'average out-degree: ', mean(g.outdegree())
print 'average in-degree: ', mean(g.indegree())
print 'max out-degree: ', max(g.outdegree())
scc = g.clusters(mode=STRONG)
print scc.summary()
print 'average component size: ', mean(scc.sizes())
print '# of nodes in largest strongly connected component: ', len(scc.giant().vs)
print '# of edges in largest strongly connected component: ', len(scc.giant().es)
wcc = g.clusters(mode=WEAK)
print wcc.summary()
print 'average component size: ', mean(wcc.sizes())
print '# of nodes in largest strongly connected component: ', len(wcc.giant().vs)
print '# of edges in largest strongly connected component: ', len(wcc.giant().es)

print 'average clustering coefficient: ', g.transitivity_undirected()
print 'diameter: ', g.diameter()
print 'assortativity: ', g.assortativity_degree()
