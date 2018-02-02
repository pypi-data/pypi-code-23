# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:29:18 2018

@author: jaredmt
"""

'''=================sympy===================='''
'''
import sympy as sp
x,y,z=sp.symbols('x y z')
sp.lambdify(x,x**2)(5)#output 25
sp.lambdify(x,sp.solve(y-x*(-1)**.5,y)[0])(1)#output (6.12323399573677e-17+1j)
f=sp.Function('f')
sp.dsolve(sp.Derivative(f(x),x)+f(x),f(x))#output Eq(f(x), C1*exp(-x))

'''
def evalT(str1,cmd=""):
    '''import str as TI-89 sintax and convert for calculation
    prerequisites: type in the following before calling this function:
        from sympy import *
        from numpy import *
        x,y,z,a,b,c=symbols('x y z a b c')
        f=Function('f')
        g=Function('g')
        h=Function('h')
        
    examples:
        answer = evalT("3*x+1/x-4","solve")
        answer = evalT("x^2+5*x+x")
        answer = evalT("3*7+5^2")
        '''
    from sympy import sympify
    if checkEval(str1)==False:
        error("command not understood")
    str1=str(str1)
    str1=str1.replace("^","**")
    pretext=cmd+"("
    posttext=")"
    output=""
    evaltext = str(pretext+str1+posttext)
    answer=sympify(evaltext)
    #answer = eval(evaltext)
    
    if type(answer)==type([]):
        if len(answer)==1:
            answer = str(answer[0])

        else:
            for i in range(len(answer)-1):
                output=output+str(answer[i])+", "
            output=output+str(answer[len(answer)-1])
            answer=output
    else:
        answer = str(answer)
    answer=answer.replace("**","^")
    return answer

