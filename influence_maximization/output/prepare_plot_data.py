import numpy as np
import subprocess as sp


def prepare_running_time(netname, T, method):
    timef  = open('./%s/%s.runtime' % (netname, netname), 'w')
    for S in xrange(5,51,5):
        fi = open('./%s/%s_%s_%s_%s.seedset' % (netname, netname, S, T, method))    
        tm = int(fi.readlines()[-1].replace('\n','').split(' ')[1]) / 60  # unit minute
        print >> timef, S, tm
    return timef.name


def prepare_delta_influence(netname, S, T, method):
    return './%s/%s_%s_%s_%s.deltaInf' % (netname, netname, S, T, method)


def prepare_spread(netname, T, method):
    spreadf = open('./%s/%s.spread' % (netname, netname), 'w')
    for S in xrange(5,51,5):
        fi = open('./%s/%s_%s_%s_%s.seedset' % (netname, netname, S, T, method))    
        sd = fi.readlines()[-1].replace('\n','').split(' ')[2]
        print >> spreadf, S, sd
    return spreadf.name


def call_gnuplot(data):
    cmd = 'bash plot_runtime.sh ' + data
    sp.call(cmd, shell = True)


if __name__ == '__main__':
    netname = 'heplt2'
    method  = 'lp'

    for T in range(1,10,2):
    # plot running time against seed set size
        timef   = prepare_running_time(netname, T, method)
        call_gnuplot(timef)
   
    for T in range(1,10,2):
    # plot influence spread against seed set size
        spreadf = prepare_spread(netname, T, method)
        call_gnuplot(spreadf)
    
    T = 9
    for S in range(5,51,5):
    # plot delta influence against time step
        deltaf = prepare_delta_influence(netname, S, T, method)
        call_gnuplot(deltaf)

