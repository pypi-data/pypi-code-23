#-*-coding:iso-8859-1-*-

import sys, time

from maestro import *


#############################################################################
# exemple de fonction
#############################################################################
class calcul_f(Calcul):

    def __init__(self):
        Calcul.__init__(self,"f")

        self.set_saved_files([".txt"])
        

    def result_dir_name(self,x,y,z):
        return "%s%s%s" % (z,y,x)
        return "x%s/y%s_z%s" % (x,y,z)

    def run(self,x,y,z):
        if z==9 and y==0 and x==0:
            signal(CRITICAL,"error z==9 and y==2 and x==1")
        if z==0 and y==0 and x==1:
            signal(CRITICAL,"error z==9 and y==3 and x==1")
        if z==0 and y==0 and x==2:
           s='xxxxx'
           res=float(s)

            
        #time.sleep(2)
        answer=1000+100*int(x)+10*int(y)+int(z)
        print answer
        #send_message("res","%s"%answer,"G")
        #send_message("loc","%s"%answer * 1000)
        time.sleep(1)
        return answer


    def rangeZ(self,x,y):
        return range(1)
        return [1]

#############################################################################
#
#############################################################################


if __name__ == "__main__":

        CALC=calcul_f()
    
        ETUDE=Job("sweepa","SWEEPING",CALC)

        ETUDE.add_set("x",range(10))
        ETUDE.add_set("y",range(10))
#        ETUDE.add_set("x",[1])
#        ETUDE.add_set("y",[2,3])
        ETUDE.add_set("z",CALC.range(4))
        
        out=ETUDE.sweep_domain()
        
