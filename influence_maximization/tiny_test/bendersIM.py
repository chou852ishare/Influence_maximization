#!/usr/bin/python
# ---------------------------------------------------------------------------
# Version 12.6
# ---------------------------------------------------------------------------
#
# benderIM.py solves an MILP model for an Influence Maximization (IM) 
# Problem under Linear Threshold Model through Benders decomposition.
#
# The in-weights of a node are given. The MILP model is decomposed 
# into a master MILP and a worker LP.
#
# The master MILP is then solved by adding Benders' cuts during
# the branch-and-cut process via the cut callback classes 
# LazyConstraintCallback and UserCutCallback.
# The cut callbacks add to the master MILP violated Benders' cuts
# that are found by solving the worker LP.
#
# The program allows to decide if Benders' cuts have to be separated:
#
# a) Only to separate integer infeasible solutions.
# In this case, Benders' cuts are treated as lazy constraints through the
# class LazyConstraintCallback.
#
# b) Also to separate fractional infeasible solutions.
# In this case, Benders' cuts are treated as lazy constraints through the
# class LazyConstraintCallback.
# In addition, Benders' cuts are also treated as user cuts through the
# class UserCutCallback.
#
# 
#    python bendersIM.py {0|1} 
# where
#     0         Indicates that Benders' cuts are only used as lazy constraints,
#               to separate integer infeasible solutions.
#     1         Indicates that Benders' cuts are also used as user cuts,
#               to separate fractional infeasible solutions.
# 
#
# IM instance defined on a directed graph G = (V, A)
# - V = {0, ..., n-1}, V0 = V \ {0}
# - A = {(i,j) : i in V, j in V, i != j }
# - forall i in V: delta-(i) = {(j,i) in A : j in V}
# - w(i,j) = in-weight associated with (i,j) in A
#
# MILP model
#
# Modeling variables:
# forall i in V:
#    y(i)   = 1, if node i is selected as seed
#           = 0, otherwise
# forall i,t in V*T:
#    x(i,t) = probability of node i being active at time t
#
# Objective:
# maximize sum(i in V) y(i) + sum(t in T) sum(i in V) x(i,t)    (1)
#
# Budget constraint:
#             sum(i in V) y(i) <= |S|                           (2)
# 
# Propagation constraints:
# forall i in V and t >= 1 : 
#                       x(i,t) <= (1-y(i))M                     (3)
# forall i in V:        x(i,1) <= sum(j in V) w(j,i)*y(j)       (4)
# forall i in V:        x(i,t) <= sum(j in V) w(j,i)*x(j,t-1)   (5)
#
# Binary constraints:
# forall i in V: y(i) in {0, 1}                                 (6)

import sys
from math import fabs
import cplex
from cplex.callbacks import UserCutCallback, LazyConstraintCallback
from cplex.exceptions import CplexError

# The class BendersLazyConsCallback 
# allows to add Benders' cuts as lazy constraints.
# 
class BendersLazyConsCallback(LazyConstraintCallback):
        
    def __call__(self):   
        y        = self.y
        x1       = self.x1
        z        = self.z
        workerLP = self.workerLP

        # Get the current y, x1 and z solution
        ySol    = self.get_values(y)
        x1Sol   = self.get_values(x1) 
        zSol    = self.get_values(z)
        print 'lazy constraint, y =', filter(lambda yi: yi[1] > 1e-03, enumerate(ySol))
        print 'lazy constraint, z =', zSol
         
        # Benders' cut separation
        if workerLP.separate(ySol, y, x1Sol, x1, zSol, z):
            self.add(constraint = workerLP.cutLhs, sense = "L", rhs = workerLP.cutRhs)


# The class BendersUserCutCallback 
# allows to add Benders' cuts as user cuts.
# 
class BendersUserCutCallback(UserCutCallback):
        
    def __call__(self):  
        y        = self.y
        x1       = self.x1
        z        = self.z
        workerLP = self.workerLP
        print 'user cut, len(y):', len(y)
        print 'user cut, len(x1):', len(x1)
        print 'user cut, len(z):', len(z)

        # Skip the separation if not at the end of the cut loop
        if self.is_after_cut_loop() == False:
            return
  
        # Get the current y, x1 and z solution
        ySol    = self.get_values(y)
        x1Sol   = self.get_values(x1) 
        zSol    = self.get_values(z)
        
        # Benders' cut separation
        if workerLP.separate(ySol, y, x1Sol, x1, zSol, z):
            self.add(cut = workerLP.cutLhs, sense = "L", rhs = workerLP.cutRhs)
      

# This class builds the (primal) worker LP and allows to separate 
# violated Benders' cuts.
# 
class WorkerLP:
    
    # The constructor sets up the Cplex instance to solve the worker LP, 
    # and creates the primal worker LP.
    #
    # Modeling variables:
    # z = auxiliary variable
    # forall i,t in V*range(2,T+1)
    #    x(i,t) = probability of node i being active at time t
    #
    # Objective:
    # maximize sum(t in range(2,T+1)) sum(i in V) x(i,t)            (8)
    #
    # Constraints:
    # forall i in V: x(i,2) <= sum(j in delta-(i)) w(j,i)*x(j,1)    (9)
    # for i,t in V*range(3,T+1):
    #         -sum(j in delta-(i)) w(j,i)*x(j,t-1) + x(i,t) <= 0    (10)
    # for i,t in V*range(2,T+1):
    #                x(i,t) <= 0                                    (11)
    #
    def __init__(self, inweights, outweights, T): 
        
        # parameters
        numNodes        = len(inweights)
        obj_subprob_xt  = [1] * ((T-1)*numNodes)
        ub_xt           = [1] * ((T-1)*numNodes)

        # Set up Cplex instance to solve the worker LP
        cpx = cplex.Cplex()
        cpx.set_results_stream(None)
        cpx.set_log_stream(None) 
         
        # Turn off the presolve reductions and set the CPLEX optimizer
        # to solve the worker LP with primal simplex method.
        cpx.parameters.preprocessing.reduce.set(0) 
        cpx.parameters.lpmethod.set(cpx.parameters.lpmethod.values.primal)
        
        cpx.objective.set_sense(cpx.objective.sense.maximize)
        
        # Create variables 
        # constraints are coupled with x1 and S, defined in separate()
        cpx.variables.add(obj = obj_subprob_xt, ub = ub_xt)
                                                   
        self.cpx        = cpx
        self.T          = T
        self.numNodes   = numNodes
        self.inweights  = inweights
        self.outweights = outweights

    # This method separates Benders' cuts violated by the current z (and x1) solution.
    # Violated cuts are found by solving the worker LP
    #
    def separate(self, ySol, y, x1Sol, x1, zSol, z): 
        cpx              = self.cpx
        T                = self.T
        numNodes         = self.numNodes
        inweights        = self.inweights
        outweights       = self.outweights
        violatedCutFound = False
        
        # parameters
        seed_set        = map(lambda yi: yi[0], filter(lambda yi: yi[1] > 1e-03, enumerate(ySol)))
        S               = len(seed_set)
        senses_subprob  = 'L' * (numNodes + (T-2)*numNodes + (T-1)*S)
        rhs9            = [sum([nw[1] * x1Sol[nw[0]] for nw in inweights[i]]) for i in xrange(numNodes)]
        rhs10           = [0] * ((T-2)*numNodes)          # rhs of c(10)
        rhs11           = [0] * ((T-1)*S)                 # rhs of c(11)
        rhs_subprob     = rhs9 + rhs10 + rhs11            # rhs of constraints
        # coefficients
        coefficients9   = map(lambda i: (i, i, 1), xrange(numNodes))
        # c(10)
        coefficients10  = []
        for t in xrange(3, T+1):
            for i in xrange(numNodes):
                coefficients10.extend(map(lambda j_wji: ((t-2)*numNodes + i, (t-3)*numNodes + j_wji[0], -j_wji[1]), inweights[i]))
                coefficients10.extend([((t-2)*numNodes + i, (t-2)*numNodes + i, 1)])
        # c(11)
        coefficients11  = []
        for t in xrange(2, T+1):
            coefficients11.extend(map(lambda si_i: ((T-1)*numNodes +(t-2)*S + si_i[0], (t-2)*numNodes + si_i[1], 1), enumerate(seed_set)))
        # all coefficients
        coefficients    = coefficients9 + coefficients10 + coefficients11

        # Update constraints in the worker LP
        cpx.linear_constraints.add(senses = senses_subprob, rhs = rhs_subprob)
        cpx.linear_constraints.set_coefficients(coefficients)
      
        # Solve the worker LP
        cpx.solve()
      
        # A violated cut is available iff the optimal value is less than zSol
        print 'subproblem solution status,', cpx.solution.get_status()
        if cpx.solution.get_objective_value() < zSol[0]:
            print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print 'found violated! zSol:', zSol[0], '> optimal_value:', cpx.solution.get_objective_value()
        
            # create violated cut with dual variables
            # violated cut:
            # -sum(j in V) (sum(i in V) u(i) * w(j,i)) * x1(j) + z <= 0
            # where u is dual variables
            u = cpx.solution.get_dual_values(range(numNodes))
            cutCoefsList = []
            for j in xrange(numNodes):
                suw = sum(map(lambda iw: u[iw[0]] * iw[1], outweights[j]))
                cutCoefsList.append(-suw)
            cutVarsList = x1 + z
            cutCoefsList.append(1)
            
            cutLhs = cplex.SparsePair(ind = cutVarsList, val = cutCoefsList)
            cutRhs = 0.0

            self.cutLhs = cutLhs
            self.cutRhs = cutRhs
            violatedCutFound = True

        return violatedCutFound


# This function creates the master MILP
#
# Modeling variables:
# forall i in V:
#    y(i)   = 1, if node i is selected in seed set S
#           = 0, otherwise
#    x1(i)  probability of node i is active at time 1
#    z      auxiliary variable
#
# Objective:
# maximize sum(i in V) ( y(i) + x1(i) + z )                 (1)
#
# Budget constraint:
# forall i in V:               sum(i in V) y(i) <= |S|      (2)
#
# Propagation constraint:
# forall i in V:                 M*y(i) + x1(i) <= M        (3)
# forall i in V: 
#     - sum(j in delta-(i)) w(j,i)*y(j) + x1(i) <= 0        (4)
#
# Other constraints:
#                                             z <= N        (5)
# forall i in V:                           y(i) in {0, 1}   (6)
#
def createMasterILP(cpx, S, y, x1, z, inweights):
    # number of nodes
    numNodes = len(inweights)
    
    # define parameters
    M               = 100
    obj_master_y    = [1] * numNodes
    obj_master_x1   = [1] * numNodes
    obj_master_z    = [1] 
    ub_x1           = [100] * numNodes
    ub_z            = [numNodes]
    master_sense    = 'L' * (1 + numNodes + numNodes)
    master_rhs      = [S] + [M]*numNodes + [0]*numNodes
    # indices of coupled variables
    y.extend(range(numNodes))
    x1.extend(range(numNodes, 2*numNodes))
    z.extend([2*numNodes])

    # populate by nonzeros
    # decision variables: (y, x1, z)
    # constraint index                          number of nonzero index
    # (2) (0,0,1) (0,1,1) ... (0,N-1,1)         # 1*N (row*col)
    # (3) forall i in V: (i+1,i,M) (i+1,I+N,1)  # N*2
    # (4) forall i in V: 
    #       {(N+1+i,j,-w(j,i)), j in delta-(i)} # N*(|delta-(i)|+1)
    #
    coefficients = []
    # nonzeros of (2)
    coefficients.extend([(0,i,1) for i in xrange(numNodes)])
    # nonzeros of (3)
    coefficients.extend([(i+1,i,M) for i in xrange(numNodes)])
    coefficients.extend([(i+1,i+numNodes,1) for i in xrange(numNodes)])
    # nonzeros of (4)
    for i in xrange(numNodes):
        coefficients.extend([(numNodes+1+i,) + (nw[0],) + (-nw[1],) for nw in inweights[i]])
        coefficients.extend([(numNodes+1+i,numNodes+i,1)])

    # define objective
    cpx.objective.set_sense(cpx.objective.sense.maximize)
    # define variables
    cpx.variables.add(obj = obj_master_y, types = cpx.variables.type.binary * numNodes)
    cpx.variables.add(obj = obj_master_x1, ub = ub_x1)
    cpx.variables.add(obj = obj_master_z, ub = ub_z)
    # define constraints
    cpx.linear_constraints.add(senses = master_sense, rhs = master_rhs)
    cpx.linear_constraints.set_coefficients(coefficients)


def optimize(S, T, sepFracSols, inweights, outweights):
    print '*****************************************************************************************'
    print 'Solve the MIP problem using Benders Decomposition'
    try:
        print "Benders' cuts separated to cut off: " , 
        if sepFracSols == "1":
            print "Integer and fractional infeasible solutions."
        else:
            print "Only integer infeasible solutions."

        # Create master ILP
        numNodes = len(inweights)
        y   = []
        x1  = []    
        z   = []
        cpx = cplex.Cplex()
        createMasterILP(cpx, S, y, x1, z, inweights)

        # Create workerLP for Benders' cuts separation 
        workerLP = WorkerLP(inweights, outweights, T);

        # Set up cplex parameters to use the cut callback for separating Benders' cuts
        cpx.parameters.preprocessing.presolve.set(cpx.parameters.preprocessing.presolve.values.off) 
                                        
        # Set the maximum number of threads to 1. 
        # This instruction is redundant: If MIP control callbacks are registered, 
        # then by default CPLEX uses 1 (one) thread only.
        # Note that the current example may not work properly if more than 1 threads 
        # are used, because the callback functions modify shared global data.
        # We refer the user to the documentation to see how to deal with multi-thread 
        # runs in presence of MIP control callbacks. 
        cpx.parameters.threads.set(1) 

        # Turn on traditional search for use with control callbacks
        cpx.parameters.mip.strategy.search.set(cpx.parameters.mip.strategy.search.values.traditional)
        
        lazyBenders     = cpx.register_callback(BendersLazyConsCallback) 
        lazyBenders.y   = y
        lazyBenders.x1  = x1
        lazyBenders.z   = z
        lazyBenders.workerLP = workerLP 
        if sepFracSols == "1":
            userBenders     = cpx.register_callback(BendersUserCutCallback) 
            userBenders.y   = y
            userBenders.x1  = x1
            userBenders.z   = z
            userBenders.workerLP = workerLP 
    
        # Solve the model
        cpx.solve()
        
    except CplexError, exc:
        print exc
        return
        
    solution = cpx.solution
    print
    print "Solution status: " , solution.get_status()
    print "Objective value: " , solution.get_objective_value()
        
    if solution.get_status() == solution.status.MIP_optimal:
        # Write out the optimal tour
        print 'solution of y:'
        for i in range(numNodes):
            sol = solution.get_values(i)
            if sol > 1e-03:
                print i, sol 
        print 'solution of z:'
        print 2*numNodes, solution.get_values(2*numNodes)
    else:
        print "Solution status is not optimal"
        
