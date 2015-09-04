from igraph import *


netname = 'pwh'
g = load('../../data/%s-GraphML/%s.pickle' % (netname, netname))
f = open('./%s.inf' % netname, 'w')
print >> f, 'Contact network: Prince of Wales Hospital'
for e in g.es:
    print >> f, g.vs[e.source]['name'], g.vs[e.target]['name'], e['normalized inweight']
f.close()
