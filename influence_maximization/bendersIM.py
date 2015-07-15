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
        x        = self.x
        workerLP = self.workerLP
        numNodes = len(x)
      
        # Get the current x solution
        sol = []
        for i in range(numNodes):
            sol.append([])
            sol[i] = self.get_values(x[i]); 
         
        # Benders' cut separation
        if workerLP.separate(sol, x):
            self.add(constraint = workerLP.cutLhs, sense = "G", rhs = workerLP.cutRhs)


# The class BendersUserCutCallback 
# allows to add Benders' cuts as user cuts.
# 
class BendersUserCutCallback(UserCutCallback):
        
    def __call__(self):  
        x        = self.x
        workerLP = self.workerLP
        numNodes = len(x)

        # Skip the separation if not at the end of the cut loop
        if self.is_after_cut_loop() == False:
            return
  
        # Get the current x solution
        sol = []
        for i in range(numNodes):
            sol.append([])
            sol[i] = self.get_values(x[i]); 
         
        # Benders' cut separation
        if workerLP.separate(sol, x):
            self.add(cut = workerLP.cutLhs, sense = "G", rhs = workerLP.cutRhs)
      

# Data class to read an ATSP instance from an input file 
class ProbData:

    def __init__(self, filename):
        
        # read the data in filename
        self.arcCost = read_dat_file(filename)[0]
        self.numNodes = len(self.arcCost)

        # check data consistency
        for i in range(self.numNodes):
            if len(self.arcCost[i]) != self.numNodes:
                print "ERROR: Data file '%s' contains inconsistent data\n" % filename
                raise Exception("data file error")
            self.arcCost[i][i] = 0.0

   
# This class builds the worker LP (i.e., the dual of flow constraints and
# capacity constraints of the flow MILP) and allows to separate violated
# Benders' cuts.
# 
class WorkerLP:
    
    # The constructor sets up the Cplex instance to solve the worker LP, 
    # and creates the worker LP (i.e., the dual of flow constraints and
    # capacity constraints of the flow MILP)
    #
    # Modeling variables:
    # forall k in V0, i in V:
    #    u(k,i) = dual variable associated with flow constraint (k,i)
    #
    # forall k in V0, forall (i,j) in A:
    #    v(k,i,j) = dual variable associated with capacity constraint (k,i,j)
    #
    # Objective:
    # minimize sum(k in V0) sum((i,j) in A) x(i,j) * v(k,i,j)
    #          - sum(k in V0) u(k,0) + sum(k in V0) u(k,k)
    #
    # Constraints:
    # forall k in V0, forall (i,j) in A: u(k,i) - u(k,j) <= v(k,i,j)
    #
    # Nonnegativity on variables v(k,i,j)
    # forall k in V0, forall (i,j) in A: v(k,i,j) >= 0
    #
    def __init__(self, numNodes): 

        # Set up Cplex instance to solve the worker LP
        cpx = cplex.Cplex()
        cpx.set_results_stream(None)
        cpx.set_log_stream(None) 
         
        # Turn off the presolve reductions and set the CPLEX optimizer
        # to solve the worker LP with primal simplex method.
        cpx.parameters.preprocessing.reduce.set(0) 
        cpx.parameters.lpmethod.set(cpx.parameters.lpmethod.values.primal)
        
        cpx.objective.set_sense(cpx.objective.sense.minimize)
        
        # Create variables v(k,i,j) forall k in V0, (i,j) in A
        # For simplicity, also dummy variables v(k,i,i) are created.
        # Those variables are fixed to 0 and do not contribute to 
        # the constraints.
        v = []
        for k in range(1, numNodes):
            v.append([])
            for i in range(numNodes):
                v[k-1].append([])
                for j in range(numNodes):
                    varName = "v."+str(k)+"."+str(i)+"."+str(j)
                    v[k-1][i].append(cpx.variables.get_num()) 
                    cpx.variables.add(obj = [0.0], 
                                      lb = [0.0], 
                                      ub = [cplex.infinity], 
                                      names = [varName])
                cpx.variables.set_upper_bounds(v[k-1][i][i], 0.0)
                
        # Create variables u(k,i) forall k in V0, i in V     
        u = []
        for k in range(1, numNodes):
            u.append([])
            for i in range(numNodes):
                varName = "u."+str(k)+"."+str(i)
                u[k-1].append(cpx.variables.get_num())
                obj = 0.0
                if i == 0:
                    obj = -1.0
                if i == k:
                    obj = 1.0;
                cpx.variables.add(obj = [obj], 
                                  lb = [-cplex.infinity], 
                                  ub = [cplex.infinity],  
                                  names = [varName])

        # Add constraints:
        # forall k in V0, forall (i,j) in A: u(k,i) - u(k,j) <= v(k,i,j)
        for k in range(1, numNodes):
            for i in range(numNodes):
                for j in range(0, numNodes):
                    if i != j:
                        thevars = []
                        thecoefs = []
                        thevars.append(v[k-1][i][j])
                        thecoefs.append(-1.0)
                        thevars.append(u[k-1][i])
                        thecoefs.append(1.0)
                        thevars.append(u[k-1][j])
                        thecoefs.append(-1.0)
                        cpx.linear_constraints.add(lin_expr = \
                                                   [cplex.SparsePair(thevars, thecoefs)],
                                                   senses = ["L"], rhs = [0.0])
                                                   
        self.cpx      = cpx
        self.v        = v
        self.u        = u
        self.numNodes = numNodes
                                 
      
    # This method separates Benders' cuts violated by the current x solution.
    # Violated cuts are found by solving the worker LP
    #
    def separate(self, xSol, x): 
        cpx              = self.cpx
        u                = self.u
        v                = self.v
        numNodes         = self.numNodes
        violatedCutFound = False
                
        # Update the objective function in the worker LP:
        # minimize sum(k in V0) sum((i,j) in A) x(i,j) * v(k,i,j)
        #          - sum(k in V0) u(k,0) + sum(k in V0) u(k,k)
        thevars = []
        thecoefs = []
        for k in range(1, numNodes):
            for i in range(numNodes):
                for j in range(numNodes):
                    thevars.append(v[k-1][i][j])
                    thecoefs.append(xSol[i][j])    
        cpx.objective.set_linear(zip(thevars, thecoefs))
      
        # Solve the worker LP
        cpx.solve()
      
        # A violated cut is available iff the solution status is unbounded     
        if cpx.solution.get_status() == cpx.solution.status.unbounded:
      
            # Get the violated cut as an unbounded ray of the worker LP
            ray = cpx.solution.advanced.get_ray()
           
            # Compute the cut from the unbounded ray. The cut is:
            # sum((i,j) in A) (sum(k in V0) v(k,i,j)) * x(i,j) >=
            # sum(k in V0) u(k,0) - u(k,k)
            numArcs = numNodes*numNodes
            cutVarsList  = []
            cutCoefsList = []
            for i in range(numNodes):
                for j in range(numNodes):
                    thecoef = 0.0
                    for k in range(1, numNodes):
                        v_k_i_j_index = (k-1)*numArcs + i*numNodes + j
                        if ray[v_k_i_j_index] > 1e-03:
                            thecoef = thecoef + ray[v_k_i_j_index]
                    if thecoef > 1e-03:
                        cutVarsList.append(x[i][j]) 
                        cutCoefsList.append(thecoef)
            cutLhs = cplex.SparsePair(ind = cutVarsList, val = cutCoefsList)
            
            vNumVars = (numNodes-1)*numArcs
            cutRhs = 0.0
            for k in range(1, numNodes):
                u_k_0_index = vNumVars + (k-1)*numNodes
                if fabs(ray[u_k_0_index]) > 1e-03:
                    cutRhs = cutRhs + ray[u_k_0_index]
                u_k_k_index = vNumVars + (k-1)*numNodes + k
                if fabs(ray[u_k_k_index]) > 1e-03:
                    cutRhs = cutRhs - ray[u_k_k_index]
            
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
def createMasterILP(cpx, S, inweights):
    # number of nodes
    numNodes = len(inweights)
    
    # define parameters
    M               = 100
    obj_master_y    = [1] * numNodes
    obj_master_x1   = [1] * numNodes
    obj_master_z    = [1] 
    ub_x1           = [100] * numNodes
    ub_z            = [numNodes]
    master_sense    = 'L' * (1 + N + N)
    master_rhs      = [S] + [M]*numNodes + [0]*numNodes

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
    coefficients.extend([(i+1,i+N,1) for i in xrange(numNodes)])
    # nonzeros of (4)
    for i in xrange(numNodes):
        coefficients.extend([(N+1+i,) + (nw[0],) + (-nw[1],) for nw in inweights[i]])
        coefficients.extend([(N+1+i,N+i,1)])

    # define objective
    cpx.objective.set_sense(prob.objective.sense.maximize)
    # define variables
    cpx.variables.add(obj = obj_master_y, types = cpx.variables.type.binary * numNodes)
    cpx.variables.add(obj = obj_master_x1, ub = ub_x1)
    cpx.variables.add(obj = obj_master_z, ub = ub_z)
    # define constraints
    cpx.linear_constraints.add(senses = master_sense, rhs = master_rhs)
    cpx.linear_constraints.set_coefficients(coefficients)


def bendersATSP(sepFracSols, inweights):
    try:
        print "Benders' cuts separated to cut off: " , 
        if sepFracSols == "1":
            print "Integer and fractional infeasible solutions."
        else:
            print "Only integer infeasible solutions."

        # Create master ILP
        cpx = cplex.Cplex()
        S   = 3
        createMasterILP(cpx, S, inweights)
        numNodes = len(inweights)

        # Create workerLP for Benders' cuts separation 
#        workerLP = WorkerLP(numNodes);

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
        
#        lazyBenders = cpx.register_callback(BendersLazyConsCallback) 
#        lazyBenders.x = x
#        lazyBenders.workerLP = workerLP 
#        if sepFracSols == "1":
#            userBenders = cpx.register_callback(BendersUserCutCallback) 
#            userBenders.x = x
#            userBenders.workerLP = workerLP 
    
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
        for i in range(numNodes):
            sol = solution.get_values(i)
                if sol > 1e-03:
                    print i, sol 
    else:
        print "Solution status is not optimal"
        
