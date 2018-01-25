import velplot

def fit_fort(fortfile):
    '''
    Do Voigt fitting and update model.
    '''
    opfile = open('fitcommands','w')
    if '--error' in sys.argv:
        opfile.write('e\n')             # Run fit command + enter
    else:
        opfile.write('f\n')             # Run fit command + enter
    if setup.pcvals=='yes':             # If development tools called...
        if '--illcond' in sys.argv:
            opfile.write('il\n')
        opfile.write('\n')              # ...used default setup -> enter only
    opfile.write('\n')                  # Used default parameter (logN) -> enter only
    opfile.write(fortfile+'\n')   # Insert fort file name + enter
    opfile.write('n\n')                 # Do not plot the region + enter
    opfile.write('\n')                  # Do not fit more line and exit VPFIT -> enter only
    opfile.close()

    os.system(velplot.vpversion+' < fitcommands')

    if '--fit' in sys.argv or '--illcond' in sys.argv:
    
        ''' Read fort.13 and store header and first guesses '''
    
        i,flag,header,guesses = 0,0,[],[]
        line13 = [line.replace('\n','') for line in open(fortfile,'r')]
        while i < len(line13):
            if '*' in line13[i]:
                flag = flag+1
            if '*' not in line13[i] and flag==1:
                header.append(line13[i]+'\n')
            guesses.append(line13[i]+'\n')
            i = i + 1
    
        ''' Take results from fort.18 '''
    
        i,results = 0,[]
        line18 = np.loadtxt('fort.18',dtype='str',delimiter='\n')
        for i in range(len(line18)-1,0,-1):
            if 'chi-squared' in line18[i]:
                a = i + 2
                break
        for i in range(a,len(line18)):
            results.append(line18[i]+'\n')
            if len(line18[i])==1:
                break
                
        ''' Update fort.13 and embed results from fort.18 '''
    
        fort = open(fortfile,'w')
        for line in ['*\n']+header+['*\n']+results+guesses:
            fort.write(line)
        fort.close()
        
