netname = 'epinions'
method1 = 'maxlp'
method2 = 'benders'
for S in range(5,51,5):
    fr = open('./%s/%s_%s_1_%s.seedset' % (netname, netname, S, method1))
    fw = open('./%s/%s_%s_1_%s.seedset' % (netname, netname, S, method2), 'w')
    fw.writelines(fr.readlines())
fr.close()
fw.close()
