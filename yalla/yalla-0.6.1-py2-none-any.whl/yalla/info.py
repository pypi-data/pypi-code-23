#-*-coding:iso-8859-1-*-
#!/logiciels/public/bin/python-2.4
"""
module managing stat and info about one ongoing calculation
"""

# respond to a key without the need to press enter



import os,  time, sys

from fichiers  import grep, greps
from env import MY_MACHINE_FULL_NAME
from messages  import \
     signal, set_flag, get_flag, \
     MSG, CRITICAL, ERROR, send_message, \
     get_tab_val, set_tab_val, Timer, \
     load_env, save_env, \
     get_tab_list, get_tab_keys, get_tab_dim, \
     MyError, GV


from threading import Thread

if os.name == "nt":
    import Tkinter as tk
    set_flag('tk',True)
else:
    import termios, sys, os
    TERMIOS = termios
    
    def getkey():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            new = termios.tcgetattr(fd)
            new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
            new[6][TERMIOS.VMIN] = 1
            new[6][TERMIOS.VTIME] = 0
            termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
            c = None
            try:
                    c = os.read(fd, 1)
            finally:
                    termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
            return c
    
    # if __name__ == '__main__':
    #         print 'type something'
    #         s = ''
    #         while 1:
    #                 c = getkey()
    #                 if c == '\n':     ## break on a Return/Enter keypress
    #                         break
    #                 print 'got', c
    #                 s = s + c
    
    #         print s


def get_bilan(keep_probing=False):
    """
    lists errors encountered
    """
#     current = {}

#     # getting job_running
#     if get_flag('debug'):
#         print "\n\n\t jobs Running"

#     done=greps("Doing","%s/status.log" % get_flag("results_directory"),(0, 7, 9) )
#     for job in done:
#         current[job[0]]="%s-XXX-%s" % (job[1], job[2])
#         if get_flag['debug']:
#             print "\t\t %s \t %s \t %s" % (job[0], job[1], job[2])

#     # getting job_Done
#     done=greps("Done","%s/status.log" % get_flag("results_directory"),(0, 6, 8) )
#     if get_flag('debug'):
#         print "\n\n\t jobs done"
#     for job in done:
#         current[job[0]]="%s-XXX-%s" % (job[1], job[2])
#         if get_flag('debug'):
#             print "\t\t %s \t %s \t %s" % (job[0], job[1], job[2])



    
    # getting errors
    errors=greps("CRITICAL","%s/status.log" % get_flag("results_directory"),(0, 6, 4) )
    print "\n\t Errors were encountered for : \n\n\t\t Jobs \t Contexte \t Type \n"
    for err in errors:
        print "\t\t %s \t %s \t %s" % (err[0], err[1], err[2])
                


class interactive_info(Thread):

    def __init__ (self,nb):
        Thread.__init__(self)
        self.nb = nb
      
    def keypress(self,event):
        if event.keysym == 'Escape':
            self.quit()
        x = event.char
        self.react_on_key(x)
        
    def react_on_key(self,x):
        if x == "b":
            get_bilan()
        elif x == "j":
            get_bilan()
            try :
                print "\n\t current job is ",self.nb
                nb = int(raw_input('\t New Job Nb ? '))
                self.nb = nb
                print 
            except:
                print "\t Job unknown --> job stays ",self.nb
            self.general_info()
        elif x == "w":
            self.ls_work_dir()
        elif x == "r":
            self.ls_res_dir()
        elif x == "W":
            self.cd_work_dir()
        elif x == "R":
            self.cd_res_dir()
        elif x == "e":
            self.get_log("%s/error.log" % self.res_dir)
        elif x == "o":
            self.get_log("%s/output.log" % self.res_dir)
        elif x == "E":
            self.get_log("%s/error.log" % self.work_dir)
        elif x == "O":
            self.get_log("%s/output.log" % self.work_dir)
        elif x == "h":
            self.general_info()
        elif x == "x" or x=="q":
            self.quit()
        else:
            return

        print "\n\t ------                Current job is %05d                      ----" % self.nb
        print "\t ------ Press b,j  w,W, r,R, o,O, e,E, x to exit, h to get help ---- \n"

        sys.stdout.flush()

        
    def general_info(self):
        """
        print info about job
        """
        job=self.nb
        infos=greps("%05d"%job,"%s/status.log" % get_flag("results_directory"),(0, 6, 4, 8) )

        print "\n\t Information available for job %05d : "%job
        
        print "\n\t\t Status      : \t",
        if not(infos):
            print "Undone yet"
            return
        elif len(infos)==1:
            print "Currently running..."
        elif len(infos)==2:
            print "Done"
            res = infos[1][2]
            print "\t\t Result      : \t %s" % res


        if len(infos)>0:
            print "\t\t Parameters  : \t %s" % infos[1][1]
            self.work_dir = infos[1][3]
            print "\t\t Working Dir : \t %s" % self.work_dir
            self.res_dir = "%s/RESULTS/%s" % (get_flag('results_directory'),infos[1][1])
            print "\t\t Results Dir : \t %s"%self.res_dir

        print "\n\t --------------- Press a key ----------------\n"
        print "\t b) bilan            \t j) change job number"
        print "\t w) ls working dir   \t W) cd working dir "
        print "\t r) ls result  dir   \t R) cd result dir "
        print "\t o) print output.log  in result dir"
        print "\t O) print output.log  in working dir"
        print "\t e) print error.log  in result dir"        
        print "\t E) print error.log  in working dir"        
        print "\t h) print this screen\t x) quit"
        print 


        
    def get_log(self,ficname):
        #print ficname
        par = ficname.split(":")
        if len(par)>1:
            user,machine = par[0][1:].split("@")
            remote_file = par[1]
            command = "ssh %s more %s" % (par[0][1:],par[1])
            if get_flag('debug'):
                print machine,user,remote_file
                print command
            if not (machine==MY_MACHINE_FULL_NAME):
                os.system(command)
                return
            else:
                ficname = remote_file
        try:
            fic = open(ficname)
            lines = fic.readlines()
            fic.close()
            print "".join(lines)
        except:
            print "\n\t--> File does not exist!\n"

    def ls_work_dir(self):
        par = self.work_dir.split(":")
        command = "ssh %s ls -l %s" % (par[0][1:],par[1])
        if get_flag('debug'):
            print command
        os.system(command)

    def ls_res_dir(self):
        command = "cd %s; ls -la . " % (self.res_dir)
        if get_flag('debug'):
            print command
        os.system(command)
 
    def cd_res_dir(self):
        command = "cd %s; nohup xterm > /dev/null &" % (self.res_dir)
        if get_flag('debug'):
            print command
        os.system(command)

    def cd_work_dir(self):
        par = self.work_dir.split(":")
        command = "nohup xterm -e 'echo cd %s; ssh %s ' & > /dev/null " % (par[1], par[0][1:])
        if get_flag('debug'):
            print command
        os.system(command)

    def quit(self):
        if get_flag('tk'):
            self.root.destroy()        
#        self.kill_myself()

  
    def run(self):
        self.general_info()
        if get_flag('tk'):
            self.root = tk.Tk()
            self.root.bind_all('<Key>', self.keypress)
            # don't show the tk window
            self.root.withdraw()
            self.root.mainloop()
        else:
            x = ''
            while not(x=="x" or x=="q"):
                x = getkey()
                self.react_on_key(x)
    

       

def get_info(nb_job):
    win = interactive_info(nb_job)
    win.run()
#    win.join()

print time.ctime()

    
