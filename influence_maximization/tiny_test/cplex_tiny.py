#!/usr/bin/python

import numpy as np
import cplex
from cplex.exceptions import CplexError
import sys


# parameters
# constants
T   = 10      # time horizon
S   = 10      # |seed set|
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


def set_network(size, source, target, weight):
    global N
    N = size      # number of nodes in network
    w_to.extend(target)
    w_fr.extend(source)
    w_val.extend(map(lambda x: -x, weight))


def set_coefficients():
    im_obj_t.extend([1] * (N*T))
    im_obj_0.extend([1] * N)
    im_ub.extend([UB] * (N*T))
    im_rhs.extend([0]*(N*T) + [M]*(N*T) + [S])
    im_sense.extend('L' * (2*N*T+1))


def set_constraint_matrix():
    # sparse constraint matrix
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


def optimize(size, source, target, weight):
    print '************* start optimizing *********************'
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
    print "Solution variables = ", x


if __name__ == "__main__":
    size    = 60
    source  = [0] * (size-1)
    target  = range(1,size)
    weight  = [0.8] * (size-1)
    optimize(size, source, target, weight)

