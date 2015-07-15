#!/usr/bin/python

import numpy as np
import cplex
from cplex.exceptions import CplexError
import sys


# parameters
# constants
T   = 10      # time horizon
S   = 3       # |seed set|
M   = 100     # big M
UB  = 100     # upper bound of variables
# network parameters - set_network()
N           = 0      # number of nodes in network
w_to        = []
w_fr        = []
w_val       = []
# objective and constraint bounds - set_coefficients()
im_obj_t    = []
im_obj_0    = [] 
im_ub       = []
im_rhs      = []
im_sense    = []
# sparse constraint coefficient matrix
ind0        = []
ind1        = []
val         = []


def set_ST(s, t):
    global S, T
    S = s
    T = t


def set_network(size, source, target, weight):
    global N
    N = size      # number of nodes in network
    del w_to[:]
    del w_fr[:]
    del w_val[:]
    w_to.extend(target)
    w_fr.extend(source)
    w_val.extend(map(lambda x: -x, weight))


def set_coefficients():
    del im_obj_t[:]
    del im_obj_0[:]
    del im_ub[:]
    del im_rhs[:]
    del im_sense[:]
    im_obj_t.extend([1] * (N*T))
    im_obj_0.extend([1] * N)
    im_ub.extend([UB] * (N*T))
    im_rhs.extend([0]*(N*T) + [M]*(N*T) + [S])
    im_sense.extend('L' * (2*N*T+1))


def set_constraint_matrix():
    # sparse constraint matrix
    del ind0[:]
    del ind1[:]
    del val[:]
    # basic indices and values
    ind_w   = (w_to, w_fr)
    val_w   = w_val
    ind_I   = (range(N), range(N))
    val_I   = [1] * N
    val_M   = [M] * N
    for t in xrange(T):
        # nonzero coefficients of w
        ind0.extend([x+t*N for x in ind_w[0]])
        ind1.extend([x+t*N for x in ind_w[1]])
        val.extend(val_w)
        # nonzero coefficients of I in c2
        ind0.extend([x+t*N for x in ind_I[0]])
        ind1.extend([x+(t+1)*N for x in ind_I[1]])
        val.extend(val_I)
        # nonzero coefficients of MI
        ind0.extend([x+(t+T)*N for x in ind_I[0]])
        ind1.extend(ind_I[1])
        val.extend(val_M)
        # nonzero coefficients of I in c3
        ind0.extend([x+(t+T)*N for x in ind_I[0]])
        ind1.extend([x+(t+1)*N for x in ind_I[1]])
        val.extend(val_I)
    ind0.extend([2*N*T] * N)
    ind1.extend(range(N))
    val.extend([1] * N)


def populatebynonzero(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    # lower bounds are all 0.0 (the default)
    # xi0 is binary
    # xit is continuous for t >= 1
    prob.variables.add(obj = im_obj_0, types = prob.variables.type.binary * N)
    prob.variables.add(obj = im_obj_t, ub = im_ub)
    prob.linear_constraints.add(senses = im_sense, rhs = im_rhs)    
    prob.linear_constraints.set_coefficients(zip(ind0, ind1, val))


def run(seedSet, S, T, size, source, target, weight):
    print '********************************************************************************************'
    print 'calculate expected spread'
    print 'seed set:', seedSet
    print 'calculate expected spread with fixed seed set'
    set_ST(S, T)
    set_network(size, source, target, weight)
    set_coefficients()
    set_constraint_matrix()
    try:
        im_prob = cplex.Cplex()
        im_prob.set_results_stream(None)
        im_prob.set_log_stream(None) 
        handle  = populatebynonzero(im_prob)
        numrows = im_prob.linear_constraints.get_num()
        # setup seed set constraints
        sensesS = 'E' * len(seedSet)
        rhsS    = [1] * len(seedSet)
        coeffsS = []
        for i,si in enumerate(seedSet):
            coeffsS.append((numrows+i, si, 1))
        im_prob.linear_constraints.add(senses = sensesS, rhs = rhsS)
        im_prob.linear_constraints.set_coefficients(coeffsS)
        # calculate expected spread
        im_prob.solve()
    except CplexError, exc:
        print exc
        return
    print "expected spread  = ", im_prob.solution.get_objective_value()
    x  = im_prob.solution.get_values(range(size))
    ss = filter(lambda xi: xi[1] > 1e-03, enumerate(x))
    print "seed set = ", ss

