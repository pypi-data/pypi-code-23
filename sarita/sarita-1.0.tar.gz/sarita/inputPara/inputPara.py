#coding:utf-8
import sys
class inputPara():
    dicts={'g':'gui','gui':'gui','GUI':'gui','Gui':'gui','gUi':'gui','-g':'gui',
            'h':'help','-h':'help','help':'help',
            'qiniu':'qiniu','qn':'qiniu','Qiniu':'qiniu','QINIU':'qiniu',
            'th':'theme','Theme':'theme','theme':'theme',
            'siteInfo':'siteInfo','siteinfo':'siteInfo','si':'siteInfo',
            'index':'index',
            'new':'new'
            }

    
    def whatCommand(self):
        a=''
        for command in sys.argv[1:]:
            try:
                a=a+self.dicts[command]+' '
            except:
                a=a+'0 '
        a=a.split()
        if '0'in a:
            print "Error: Unkown command\nplease enter the true parameters\nfor more information,please use -h "
            a=['error']
            sys.exit()
        elif 'help'in a:      
            print "g  run the GUI\nh  print this help message\nqiniu  update the qiniu Config File\nsiteInfo  update the site information"
            sys.exit()
        return a
if __name__=='__main__':
    thein=inputPara()
    print thein.whatCommand()

