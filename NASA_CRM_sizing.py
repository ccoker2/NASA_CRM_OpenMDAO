'''
Definition of the wing_code.m black-box model for OpenMDAO use
'''
from __future__ import division, print_function

import os.path

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

    def setup(self):

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
        print(xSizing)

        #check if xSizing has changed to avoid redundant computations

        if (os.path.exists("sizingHistory.csv")==1):
            xSizing_old = np.loadtxt(open("sizingHistory.csv", "rb"), delimiter=",")
            xSizing_old = np.matrix(xSizing_old)[-1,:]
            xSizing_old = np.reshape(xSizing_old,(75,-1))
            print(xSizing_old)

            difference = xSizing_old - xSizing
            print(difference)


            if (all(i<=0.0001 for i in difference)):
                print("Avoiding redundant computation!")
                con = np.loadtxt(open("conHistory.csv", "rb"), delimiter=",")
                con = np.matrix(con)[-1,:]
                con = np.reshape(con,(22,-1))

                obj = np.loadtxt(open("objHistory.csv", "rb"), delimiter=",")
                obj = np.matrix(obj)[-1,0]
                obj = np.reshape(obj,(1,-1))
            else:
                print("Performing new computation.")
                [obj,con]  = eng.home_fun(matlab.double(xSizing.tolist()),0,nargout=2)
        else:
            print("Performing first computation.")
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
