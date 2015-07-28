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
        print 'Enter lazy constraint callback'
        print 'Objective value =', self.get_objective_value() 
        print 'Best objective value =', self.get_best_objective_value() 
        print 'Incumbent objective value =', self.get_incumbent_objective_value() 
        # Benders' cut separation
        LB = self.get_incumbent_objective_value()
        if workerLP.separate(ySol, y, x1Sol, x1, zSol, z, LB):
            for i in xrange(len(workerLP.sense)):
                self.add(constraint = workerLP.cutLhs[i], sense = workerLP.sense[i], rhs = workerLP.cutRhs[i])
        print 'Left lazy constraint callback'
        print '#############################'


# The class BendersUserCutCallback 
# allows to add Benders' cuts as user cuts.
# 
class BendersUserCutCallback(UserCutCallback):
        
    def __call__(self):  
        y        = self.y
        x1       = self.x1
        z        = self.z
        workerLP = self.workerLP

        # Skip the separation if not at the end of the cut loop
        if self.is_after_cut_loop() == False:
            return
  
        # Get the current y, x1 and z solution
        ySol    = self.get_values(y)
        x1Sol   = self.get_values(x1) 
        zSol    = self.get_values(z)
        print 'Enter user cut callback'
        print 'user cut, y =', filter(lambda yi: yi[1] > 1e-03, enumerate(ySol))
        print 'user cut, sum(x1) =', sum(x1Sol)
        print 'user cut, z =', zSol
        print 'user cut, sum(y,x1,z) =', sum(ySol)+sum(x1Sol)+sum(zSol)
        
        # Benders' cut separation
        if workerLP.separate(ySol, y, x1Sol, x1, zSol, z):
            self.add(cut = workerLP.cutLhs, sense = workerLP.sense, rhs = workerLP.cutRhs)
      

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
        self.M          = 1 
        self.numNodes   = numNodes
        self.inweights  = inweights
        self.outweights = outweights

    def generate_combinatorial_cut(self, y, ySol, LB):
        # parameters
        inweights       = self.inweights
        T               = self.T
        numNodes        = len(inweights)
        obj_subprob_xt  = [1] * ((T+1)*numNodes)
        ub_xt           = [1] * ((T+1)*numNodes)

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
        cpx.variables.add(obj = obj_subprob_xt, ub = ub_xt)
                                                   
        # This method separates Benders' cuts violated by the current z (and x1) solution.
        # Violated cuts are found by solving the worker LP
        
        # parameters
        seed_set        = map(lambda yi: yi[0], filter(lambda yi: yi[1] > 1e-03, enumerate(ySol)))
        S               = len(seed_set)
        senses_subprob  = 'G' + 'L'*(T*numNodes) + 'E'*(numNodes + T*S)
        rhsa            = [LB]
        rhsb            = [0] * (T*numNodes)                    
        rhsc            = ySol
        rhsd            = [0] * (T*S)
        rhs_subprob     = rhsa + rhsb + rhsc + rhsd                    
        # coefficients
        coefficientsa   = map(lambda i: (0, i, 1), xrange((T+1)*numNodes))
        coefficientsb   = []
        for t in xrange(1, T+1):
            for i in xrange(numNodes):
                coefficientsb.extend(map(lambda j_wji: (1 + (t-1)*numNodes + i, (t-1)*numNodes + j_wji[0], -j_wji[1]), inweights[i]))
                coefficientsb.extend([(1 + (t-1)*numNodes + i, t*numNodes + i, 1)])
        coefficientsc   = map(lambda i: (1 + T*numNodes + i, i, 1), xrange(numNodes))
        coefficientsd   = []
        for t in xrange(1, T+1):
            coefficientsd.extend(map(lambda si_i: (1 + (T+1)*numNodes +(t-1)*S + si_i[0], t*numNodes + si_i[1], 1), enumerate(seed_set)))
        # all coefficients
        coefficients    = coefficientsa + coefficientsb + coefficientsc + coefficientsd

        # Update constraints in the worker LP
        cpx.linear_constraints.delete()
        cpx.linear_constraints.add(senses = senses_subprob, rhs = rhs_subprob)
        cpx.linear_constraints.set_coefficients(coefficients)
      
        # Solve the worker LP
        cpx.solve()
      
        # A violated cut is available iff the subproblem is infeasible
        print cpx.solution.get_status(), cpx.solution.get_status_string(cpx.solution.get_status())
        print 'seed set: ', seed_set
        print 'ySol: ', ySol
        print 'Objective value: ', cpx.solution.get_objective_value(), 'LB: ', LB
        if cpx.solution.get_status() == 3:
            print 'Generating combinatorial Benders cut'

            cpx.conflict.refine(cpx.conflict.linear_constraints(0, 0, T*numNodes), cpx.conflict.linear_constraints(-1, 1+T*numNodes, T*numNodes+numNodes+T*S), cpx.conflict.upper_bound_constraints(0))    
            status = cpx.conflict.get()
            groups = cpx.conflict.get_groups()
            for i,s in enumerate(status):
                print i, s, groups[i], cpx.conflict.group_status[s]
            print 'I am a bug' + 0

            self.cutLhs.append(cplex.SparsePair(ind = xrange(numNodes), val = [1]*numNodes))
            self.cutRhs.append(1+S)
            self.sense.append('G')

            combinatorialCutFound = True
            
    
    # This method separates Benders' cuts violated by the current z (and x1) solution.
    # Violated cuts are found by solving the worker LP
    #
    def separate(self, ySol, y, x1Sol, x1, zSol, z, LB): 
        cpx              = self.cpx
        T                = self.T
        M                = self.M
        numNodes         = self.numNodes
        inweights        = self.inweights
        outweights       = self.outweights
        violatedCutFound = False
        self.cutLhs      = []
        self.cutRhs      = []
        self.sense       = []
        
        # parameters
        seed_set        = map(lambda yi: yi[0], filter(lambda yi: yi[1] > 1e-03, enumerate(ySol)))
        S               = len(seed_set)
        senses_subprob  = 'L' * (numNodes + (T-2)*numNodes + (T-1)*numNodes)
        rhs9            = [sum([nw[1] * x1Sol[nw[0]] for nw in inweights[i]]) for i in xrange(numNodes)]
        rhs10           = [0] * ((T-2)*numNodes)                    # rhs of c(10)
        rhs11           = map(lambda yi: M*(1-yi), ySol) * (T-1)    # rhs of c(11)
        rhs_subprob     = rhs9 + rhs10 + rhs11                      # rhs of constraints
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
            coefficients11.extend(map(lambda i: ((T-1)*numNodes + (t-2)*numNodes + i, (t-2)*numNodes + i, 1), xrange(numNodes)))
        # all coefficients
        coefficients    = coefficients9 + coefficients10 + coefficients11

        # Update constraints in the worker LP
        cpx.linear_constraints.delete()
        cpx.linear_constraints.add(senses = senses_subprob, rhs = rhs_subprob)
        cpx.linear_constraints.set_coefficients(coefficients)
      
        # Solve the worker LP
        cpx.solve()
      
        print 'zSol =', zSol[0], 'optimal_value=', cpx.solution.get_objective_value()
        print 'seed set: ', seed_set
        print 'Expected spread: ', cpx.solution.get_objective_value() + sum(ySol) + sum(x1Sol), 'LB: ', LB
        if abs(cpx.solution.get_objective_value() - zSol[0]) > 1e-03:
            print 'Generating optimality cut'

            # create violated cut with dual variables
            # violated cut:
            # sum(i in V)(sum(t>=2) M * u(i,t)) * y(i) 
            #   - sum(j in V) (sum(i in V) u(i)*w(j,i)) * x1(j) 
            #   + z <= sum(i in V)(sum(t>=2) M * u(i,t))
            # where u is dual variables
            u = cpx.solution.get_dual_values()
            cutVarsList = y + x1 + z
            cutCoefsList = []
            # coefficients for y
            su = map(lambda i: M*sum(u[(T-1)*numNodes+i::numNodes]), xrange(numNodes))
            cutCoefsList.extend(su)
            # coefficients for x1
            for j in xrange(numNodes):
                suw = sum(map(lambda iw: u[iw[0]] * iw[1], outweights[j]))
                cutCoefsList.append(-suw)
            # coefficients for z
            cutCoefsList.append(1)
            
            self.cutLhs.append(cplex.SparsePair(ind = cutVarsList, val = cutCoefsList))
            self.cutRhs.append(sum(su))
            self.sense.append('L')

            violatedCutFound = True

        # A combinatorial cut is considered to be generated if the optimal value equals to zSol
        # and the bound inquality is violated
        if cpx.solution.get_objective_value() < LB - sum(ySol) - sum(x1Sol):
            print 'Bound inequality violated !!!'
            print 'Generating combinatorial Benders cuts!!!'
            self.generate_combinatorial_cut(y, ySol, LB)

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
    # force to a fixed solution
    #rows = [[[1], [1]], [[3], [1]], [[5], [1]], [[6], [1]]]
    #cpx.linear_constraints.add(lin_expr = rows, senses = 'E'*len(rows), rhs = [1.0]*len(rows))


def optimize(S, T, sepFracSols, inweights, outweights):
    print '*****************************************************************************************'
    print 'Solve the MIP problem using Benders Decomposition with EXACT workerLP'
    try:
        print "Benders' cuts separated to cut off: " , 
        if sepFracSols == 1:
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
        if sepFracSols == 1:
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
    print "Default epgap: ", cpx.parameters.mip.tolerances.mipgap.get()
    print "Solution status: " , solution.get_status(), solution.get_status_string(solution.get_status())
    print "Objective value: " , solution.get_objective_value()
        
    if solution.get_status() == 101 or solution.get_status() == 102: # solution.status.MIP_optimal:
        # get optimal solution of master problem
        ySol    = solution.get_values(y)
        x1Sol   = solution.get_values(x1)
        zSol    = solution.get_values(z)
        seedSet = []
        # Write out the optimal solution
        print 'seed set:'
        for i,sol in enumerate(ySol):
            if sol > 1e-03:
                print i, sol 
                seedSet.append(i)
        print 'zSol:'
        print 2*numNodes, zSol[0]
        # solve subproblem again with the optimal master solution
        # this is necessary since the latest subproblem objective value 
        # may not correspond to the optimal master solution
        #workerLP.separate(ySol, y, x1Sol, x1, zSol, z)
        #print 'Objective value of workerLP: ', workerLP.cpx.solution.get_objective_value()
        #print "Influence maximization with Benders' Decomposition with EXACT workerLP:"
        #print 'Expected spread = ', solution.get_objective_value() + workerLP.cpx.solution.get_objective_value() - zSol[0]
    else:
        print "Solution status is not optimal"
    
    return seedSet 
