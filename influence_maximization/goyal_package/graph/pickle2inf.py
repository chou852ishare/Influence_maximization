from igraph import *


netname = 'epinions'
g = load('../../data/%s-GraphML/%s.pickle' % (netname, netname))
f = open('./%s.inf' % netname, 'w')
print >> f, 'SocEpinions: global DAG'
for e in g.es:
    print >> f, g.vs[e.source]['name'], g.vs[e.target]['name'], e['normalized inweight']
f.close()
