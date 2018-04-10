from openmdao.api import Problem, ScipyOptimizeDriver, pyOptSparseDriver, ExecComp, IndepVarComp, Group
import numpy as np
from NASA_CRM_sizing import wingSizing

# build the model
prob = Problem()
indeps = prob.model.add_subsystem('indeps', IndepVarComp())


indeps = indeps.add_output('xSizing', val=[0.27333,0.38934,0.32166,0.34513,0.10693,
0.29485,0.46206,0.46209,0.38434,0.016383,0.0084058,0.13495,0.15928,0.11366,
3.4438e-05,4.8604e-07,0.055954,0.074893,0.14461,0.027699,5.0358e-08,7.2364e-08,
1.3258e-07,2.3962e-07,4.6716e-07,0.35372,0.50207,0.21739,0.26332,0.03554,
0.22018,0.37993,0.39585,0.30358,1.6764e-06,0.060021,0.064906,0.079196,0.069447,
0.078715,0.068255,0.063453,0.068168,0.070863,0.07654,0.044548,0.053766,0.054088,
0.060702,0.065944,1,1,1,0.845,0.36588,1,0.62285,5.1545e-06,9.953e-06,0.30544,
1.8339e-06,2.2218e-06,4.3283e-06,4.5355e-06,8.0854e-06,3.2776e-06,2.246e-06,
3.15e-06,4.1738e-06,7.3781e-06,4.5671e-07,7.2823e-07,9.6091e-07,1.4276e-06,
2.5897e-06
])

# Hot Start
# M = np.loadtxt(open("SNOPTsizingHistory.csv", "rb"), delimiter=",", usecols=np.arange(75))[-1,:]
# indeps.add_output('xSizing', val=np.reshape(M,(75,1)))

prob.model.add_subsystem('wing',wingSizing())

prob.model.connect('indeps.xSizing', 'wing.xSizing')


# setup the optimization
prob.driver = pyOptSparseDriver()
# prob.driver = ScipyOptimizeDriver()

# prob.driver.options['optimizer'] = "SLSQP"
# prob.driver.opt_settings['MAXIT'] = 200


prob.driver.options['optimizer'] = "SNOPT"
prob.driver.opt_settings['Major iterations limit'] = 200


prob.model.add_design_var('indeps.xSizing', lower=0, upper=1)
prob.model.add_objective('wing.f')
prob.model.add_constraint('wing.g')

prob.setup()

print(prob)

# run the optimization
prob.run_driver()


# minimum value
# print(prob['objfn.f'])
# location of the minimum
print(prob['indeps.xSizing'])
# print(prob['indeps.y'])
