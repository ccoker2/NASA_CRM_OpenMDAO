'''
Definition of the wing_code.m black-box model for OpenMDAO use
'''
from __future__ import division, print_function
from openmdao.core.explicitcomponent import ExplicitComponent
from openmdao.api import ScipyOptimizeDriver
import numpy as np
import csv
import matlab.engine
eng = matlab.engine.start_matlab()

class wingSizing(ExplicitComponent):
    """
    Evaluates the equation wing_code.m as a black box.
    """
    # #class variables
    # dfdx = None
    # dgdx = None

    def setup(self):

        #instance variables
        # self.dfdx = None
        # self.dgdx = None

        #inputs
        self.add_input('xSizing', shape=(75,1))

        #ouputs
        self.add_output('f', shape=(1,1))
        self.add_output('g', shape=(22,1))

        self.declare_partials('f', 'xSizing')#,value=dfdx)
        self.declare_partials('g', 'xSizing')#,value=dgdx)

    def compute(self, inputs, outputs):

        #run wing_code.m without adjoints
        print("\n\nComputing Objective and Constraints...\n")
        xSizing = inputs['xSizing']
        [obj,con]  = eng.home_fun(matlab.double(xSizing.tolist()),0,nargout=2)
        outputs['f'] = obj
        outputs['g'] = con


    def compute_partials(self, inputs, J):
        print("Computing Partials...")
        #run wing_code.m with adjoints
        xSizing = inputs['xSizing']
        # [obj,con, wingSizing.dfdx, wingSizing.dgdx]  = eng.home_fun(matlab.double(xSizing.tolist()),1,nargout=4)
        [obj,con, dfdx, dgdx]  = eng.home_fun(matlab.double(xSizing.tolist()),1,nargout=4)
        # outputs['dfdx'] = obj
        # outputs['dgdx'] = con

        #run wing_code.m with adjoints
        J['f','xSizing'] = np.reshape(dfdx,(-1,75))
        J['g','xSizing'] = np.reshape(dgdx,(-1,75))



if __name__ == "__main__":
    from openmdao.core.problem import Problem
    from openmdao.core.group import Group
    from openmdao.core.indepvarcomp import IndepVarComp

    model = Group()
    ivc = IndepVarComp()
    ivc.add_output('xSizing',shape=(75,1))
    # model.add_subsystem('des_vars', ivc)
    model.add_subsystem('sizingComp', wingSizing())
    # model.connect('des_vars.xSizing', 'sizingComp.xSizing')

    prob = Problem(model)
    # prob.driver = ScipyOptimizeDriver()  # so 'openmdao cite' will report it for cite docs
    prob.setup()
    prob.run_model()

    # # print(prob['parab_comp.f_xy'])
    print(prob['sizingComp.f'])
    print(prob['sizingComp.g'])
    #
    # # prob['des_vars.x'] = 5.0
    # # prob['des_vars.y'] = -2.0
    # prob['des_vars.xSizing'] = np.ones(75)
    # prob.run_model()
    # # print(prob['parab_comp.f_xy'])
#     # print(prob['wingSizing.obj_xSizing'])
