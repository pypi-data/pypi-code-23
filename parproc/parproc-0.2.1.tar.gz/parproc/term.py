import sys, time
from parproc.par import Proc
from collections import OrderedDict

class Displayable:
    def __init__(self, proc):
        self.proc = proc
        self.text = []    #Additional lines of text to display for proc
        self.completed = False

    #Get number of lines to display for item
    def height(self):
        return 1 + len(self.text)


#Manages terminal session.
class Term:

    procStatus = {
        Proc.STATE_IDLE:       'IDLE   ',
        Proc.STATE_WANTED:     'WANT   ',
        Proc.STATE_RUNNING:    'RUNNING',
        Proc.STATE_SUCCEEDED:  '  OK!  ',
        Proc.STATE_FAILED:     'FAILED ',
    }
    procStateAnim = [
        '*      ',
        ' *     ',
        '  *    ',
        '   *   ',
        '    *  ',
        '     * ',
        '      *',
        '     * ',
        '    *  ',
        '   *   ',
        '  *    ',
        ' *     ',
    ]
        
    procStatusWidth = 7
    
    updatePeriod = 0.1 #Seconds between each update

    def __init__(self, dynamic=True):
        #Keep track of active lines in terminal, i.e. lines we will go back and change
        self.active = OrderedDict()
        self.dynamic = dynamic #True to dynamically update shell
        self.lastUpdate = 0 #To limit update rate
        self.animState = 0

        #self.extraLines = 0 #Set to number of extra lines output to shell whenever printing something custom
        self.height = 0 #Number of lines currently active

        
    def startProc(self, p):
        disp = Displayable(p) #TODO: Will give issues if multiple instances of same proc
        self.active[p] = disp
        
        if not self.dynamic:
            print('[{}] {} started'.format('*' * Term.procStatusWidth, p.name))
        else:
            #Add line to active lines, and print it
            self._printLine(self._procLines(disp))

    def endProc(self, p):
        disp = self.active[p]
        disp.completed = True

        #On failure show N last lines of log
        if disp.proc.state == Proc.STATE_FAILED and disp.proc.logFilename != '':
            with open(disp.proc.logFilename) as f:
                disp.text = f.read().splitlines()[-8:]

        if not self.dynamic:
            print(self._procLines(self.active[p]))
            del self.active[p]
        else:
            #No need to make any changes, as 'update' will take care of it
            pass

    #Call to notify of proc e.g. being canceled. Will show up as completed with message depending
    #on the state of the proc
    def completedProc(self, p):
        self.startProc(p)
        self.endProc(p)



    #force: force update
    def update(self, force=False):
        if len(self.active) == 0:
            return
        
        #Only make updates every so often
        if self.dynamic and (force or time.time() - self.lastUpdate > Term.updatePeriod):
            self.lastUpdate = time.time()
            oldHeight = self.height
            delHeight = 0
            self.height = 0

            
            #Move cursor up, to get ready for update
            self._moveCursorVerticalOffset(-oldHeight)

            #Find all completed processes. Draw these first, and delete them
            for proc, disp in [(proc, disp) for proc, disp in self.active.items() if disp.completed]:
                self._printLines(self._procLines(disp))
                delHeight += disp.height()
                del self.active[proc]

            #Redraw all active procs
            for proc, disp in self.active.items():
                self._printLines(self._procLines(disp))

            #Draw over any extra lines
            while self.height < oldHeight:
                self._printLine('')

            #Deleted items are now static, and can be removed from active height
            self.height -= delHeight

            #Progress animation
            self.animState += 1


        sys.stdout.flush()


    def getInput(self, message, password):
        self.height += 3
        
        print(message)
        if password:
            import getpass
            return getpass.getpass()
        else:
            return sys.stdin.readline()

    
    #Returns status line for a process
    def _procLines(self, disp):
        #Main status line
        if disp.proc.state == Proc.STATE_RUNNING and self.dynamic:
            status = Term.procStateAnim[self.animState % len(Term.procStateAnim)]
        else:
            status = Term.procStatus[disp.proc.state]

        moreInfo = disp.proc.moreInfo
        if disp.proc.state == Proc.STATE_FAILED:
            if moreInfo == '':
                moreInfo = 'logfile: {}'.format(disp.proc.logFilename)

        if moreInfo != '':
            moreInfo = ' - ' + moreInfo

        statusLine = '[{}] {}{}'.format(status, disp.proc.name, moreInfo)

        return  [statusLine] + ['   # {}'.format(l) for l in disp.text]

    #Move cursor up or down with an offset
    def _moveCursorVerticalOffset(self, dy):
        if dy < 0:
            print('\033[{}A'.format(-dy), end='') #Move cursor up
        else:
            print('\033[{}B'.format(dy), end='') #Move cursor down

    #Print a line, covering up whatever was on that line before
    def _printLine(self, text):
        print('\033[0K\r{}'.format(text))
        self.height += 1

    def _printLines(self, lines):
        for l in lines:
            self._printLine(l)
        
