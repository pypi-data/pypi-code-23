#-*-coding:iso-8859-1-*-

import sys, time

from maestro import *


#############################################################################
# elementary job definition
#############################################################################
class job_template(Maestro):

    def __init__(self):
        # initialization of  the framework
        Maestro.__init__(self)
        
        # details which files to copy to the study directory if the job
        # is successful. If not, every file will be copied
        self.set_saved_files(["output","input"])
        
    # set the name of the directory where job results will be copied
    # !!! as much as parameter as dimensions of the sweeping domain
    # directory will be <STUDY_DIRECTORY>/<result of this function>
    def result_dir_name(self,x,y):
        return "%02d%02d" % (int(x),int(y))

    # main part of the job
    # !!! as much as parameter as dimensions of the sweeping domain
    def run(self,x,y):

        b = (int(x)+int(y))/10.
        
        f = open("input","w")
        f.write("%f" % b)
        f.close()
        
        os.system("/home/sam/TEST_MAESTRO/a.exe")
            

        # greping value from a file
        #   grep(<pattern to be found>,<name of the file>,<columns to extract>)
        result = grep("result :","output",[2])

        to_print = "%02d%02d : %s"%(int(x),int(y),result)
        print "result=",to_print
        # sending message to centralized log 
        # result will appear in <STUDY_DIRECTORY>/LOGS/res
        send_message("res",to_print,"G")

        time.sleep(1)
        return result



#############################################################################
# Main Study resulting of sweeping the domain with respect to all dimensions 
#############################################################################


if __name__ == "__main__":
    
    # Step 1) Initializing the study 
    #   1st parameter : name to be given to the job submitted to the cluster
    #   2nd parameter : directory to store the result of the study
    #   3rd parameter : job template
    S=Study("param","STUDY",job_template())

    # Step 2) defining how to sweep the domain by describing successive dimension
    #   1st parameter : name of the dimension (used in error message)
    #   2nd parameter : range 
    S.add_sweep_dimension("x",range(1,6))
    S.add_sweep_dimension("y",range(1,6))
        
    # Step 3) launching the study
    S.sweep_domain()
        
