#!/usr/bin/python

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
        workerLP = self.workerLP

        # Get the current y solution
        ySol    = self.get_values(y)
        print 'Enter lazy constraint callback'
        print 'Objective value =', self.get_objective_value() 
        print 'Best objective value =', self.get_best_objective_value() 
        print 'Incumbent objective value =', self.get_incumbent_objective_value() 
        # Benders' cut separation
        LB = self.get_incumbent_objective_value()
        if workerLP.separate(ySol, y, LB):
            print 'Add combinatorial Benders cut!!!'
            self.add(constraint = workerLP.cutLhs, sense = "G", rhs = workerLP.cutRhs)
        print 'Left lazy constraint callback'
        print '#############################'


# This class builds the (primal) worker LP and allows to separate 
# violated Benders' cuts.
# 
class WorkerLP:
    
    def __init__(self, inweights, outweights, T): 
        
        # parameters
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
                                                   
        self.cpx        = cpx
        self.T          = T
        self.numNodes   = numNodes
        self.inweights  = inweights
        self.outweights = outweights

    # This method separates Benders' cuts violated by the current z (and x1) solution.
    # Violated cuts are found by solving the worker LP
    #
    def separate(self, ySol, y, LB): 
        cpx              = self.cpx
        T                = self.T
        numNodes         = self.numNodes
        inweights        = self.inweights
        outweights       = self.outweights
        combinatorialCutFound = False
        
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
        if cpx.solution.get_status() == 3:
            print 'Generating combinatorial Benders cut'

            
            self.cutLhs = cplex.SparsePair(ind = cutVarsList, val = cutCoefsList)
            self.cutRhs = sum(su)

            combinatorialCutFound = True
            
        return combinatorialCutFound


def createMasterILP(cpx, S, y, numNodes):
    # define parameters
    obj_master_y    = [1] * numNodes
    master_sense    = 'L'  
    master_rhs      = [S] 
    # indices of coupled variables
    y.extend(range(numNodes))

    coefficients = []
    # nonzeros of (2)
    coefficients.extend([(0,i,1) for i in xrange(numNodes)])

    # define objective
    cpx.objective.set_sense(cpx.objective.sense.maximize)
    # define variables
    cpx.variables.add(obj = obj_master_y, types = cpx.variables.type.binary * numNodes)
    # define constraints
    cpx.linear_constraints.add(senses = master_sense, rhs = master_rhs)
    cpx.linear_constraints.set_coefficients(coefficients)


def optimize(S, T, sepFracSols, inweights, outweights):
    print '*****************************************************************************************'
    print 'Solve the MIP problem using Pure Combinatorial Benders cuts'
    try:
        print "Benders' cuts separated to cut off: " , 
        if sepFracSols == 1:
            print "Integer and fractional infeasible solutions."
        else:
            print "Only integer infeasible solutions."

        # Create master ILP
        numNodes = len(inweights)
        y   = []
        cpx = cplex.Cplex()
        createMasterILP(cpx, S, y, numNodes)

        # Create workerLP for Benders' cuts separation 
        workerLP = WorkerLP(inweights, outweights, T);

        # Set up cplex parameters to use the cut callback for separating Benders' cuts
        cpx.parameters.preprocessing.presolve.set(cpx.parameters.preprocessing.presolve.values.off) 
        cpx.parameters.threads.set(1) 

        # Turn on traditional search for use with control callbacks
        cpx.parameters.mip.strategy.search.set(cpx.parameters.mip.strategy.search.values.traditional)
        
        lazyBenders     = cpx.register_callback(BendersLazyConsCallback) 
        lazyBenders.y   = y
        lazyBenders.workerLP = workerLP 
    
        # Solve the model
        cpx.solve()
        
    except CplexError, exc:
        print exc
        return
        
    solution = cpx.solution
    print
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
        workerLP.separate(ySol, y, x1Sol, x1, zSol, z)
        print 'Objective value of workerLP: ', workerLP.cpx.solution.get_objective_value()
        print "Influence maximization with Benders' Decomposition with EXACT workerLP:"
        print 'Expected spread = ', solution.get_objective_value() + workerLP.cpx.solution.get_objective_value() - zSol[0]
    else:
        print "Solution status is not optimal"
    
    return seedSet 
