#!/usr/bin/python

import numpy as np
import cplex
from cplex.exceptions import CplexError
import sys


# parameters
# constants
T   = 0              # time horizon
S   = 0              # |seed set|
UB  = 1              # upper bound of variables
# network parameters - set_network()
N           = 0      # number of nodes in network
w_to        = []
w_fr        = []
w_val       = []
# objective and constraint bounds - set_coefficients()
im_obj_t    = []
im_obj_0    = [] 
im_ub_t     = []
im_ub_0     = []
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
    w_to.extend(target)
    w_fr.extend(source)
    w_val.extend(map(lambda x: -x, weight))


def set_coefficients():
    im_obj_t.extend([1] * (N*T))
    im_obj_0.extend([1] * N)
    im_ub_t.extend([UB] * (N*T))
    im_ub_0.extend([UB] * N)
    im_rhs.extend([0]*(N*T) + [1]*N + [S])
    im_sense.extend('L' * (N*T + N + 1))


def set_constraint_matrix():
    # sparse constraint matrix
    # basic indices and values
    ind_w   = (w_to, w_fr)
    val_w   = w_val
    ind_I   = (range(N), range(N))
    val_I   = [1] * N
    for t in xrange(T):
        # nonzero coefficients of w
        ind0.extend([x+t*N for x in ind_w[0]])
        ind1.extend([x+t*N for x in ind_w[1]])
        val.extend(val_w)
        # nonzero coefficients of I in c2
        ind0.extend([x+t*N for x in ind_I[0]])
        ind1.extend([x+(t+1)*N for x in ind_I[1]])
        val.extend(val_I)
    for i in xrange(N):
        # nonzero coefficients of y in c3
        ind0.extend([T*N + i])
        ind1.extend([i])
        val.extend([1])
        # nonzero coefficients of x in c3
        ind0.extend([T*N+i for t in xrange(1,T+1)])
        ind1.extend([t*N+i for t in xrange(1,T+1)])
        val.extend([1]*T)
    # nonezero coefficients for budget constraint
    ind0.extend([N*T+N] * N)
    ind1.extend(range(N))
    val.extend([1] * N)


def populatebynonzero(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    # lower bounds are all 0.0 (the default)
    # xi0 and xit are continuous
    prob.variables.add(obj = im_obj_0, ub = im_ub_0)
    prob.variables.add(obj = im_obj_t, ub = im_ub_t)
    prob.linear_constraints.add(senses = im_sense, rhs = im_rhs)    
    prob.linear_constraints.set_coefficients(zip(ind0, ind1, val))


def optimize(S, T, size, source, target, weight):
    print '******************************************************************************************'
    print 'Solve the LP relaxation directly'
    set_ST(S, T)
    set_network(size, source, target, weight)
    set_coefficients()
    set_constraint_matrix()
    try:
        im_prob = cplex.Cplex()
        handle = populatebynonzero(im_prob)
        im_prob.solve()
    except CplexError, exc:
        print exc
        return
    print
    print '**********************************'
    # solution.get_status() returns an integer code
    print "Solution status = " , im_prob.solution.get_status(), ":",
    # the following line prints the corresponding string
    print im_prob.solution.status[im_prob.solution.get_status()]
    print "Solution value  = ", im_prob.solution.get_objective_value()
    x     = im_prob.solution.get_values()
    x     = np.reshape(x, (T+1, N))
    #print "Solution variables = ", x
    print reduce(lambda x1, x2: x1+x2, x)
    seedSet = []
    for i,sol in enumerate(x[0]):
        if sol > 1e-03:
            print i, sol 
            seedSet.append(i)
    
    return seedSet
