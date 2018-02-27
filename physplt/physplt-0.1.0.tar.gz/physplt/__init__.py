import matplotlib.pyplot as plt

def dist_2d(x,y,line='',label='what are we plotting today?', title='what do we call this plot?'):
    '''
    dist_2d() takes an array/list of the coordinates in meters and plots them. Contains optional kwargs
    for label and title.
    '''
    plt.figure()
    if line != '':
        plt.plot(x,y, line, label=label)
    else:
        plt.plot(x,y, label=label)
    plt.xlabel('Horizontal Distance (m)')
    plt.ylabel('Vertical Distance (m)')
    plt.title(title)
    plt.legend()
            
def dist_1d(t,y,line='',label='what are we plotting today?', title='what do we call this plot?'):
    '''
    dist_1d() takes an array/list of the coordinates in meters and time in seconds and plots them.
    Contains optional kwargs for label and title.
    '''
    plt.figure()
    if line != '':
        plt.plot(t,y, line, label=label)
    else:
        plt.plot(t,y, label=label)
    plt.xlabel('Time (s)')
    plt.ylabel('Distance (m)')
    plt.title(title)
    plt.legend()
    
def vel(t,v,line='',label='what are we plotting today?', title='what do we call this plot?'):
    '''
    vel() takes an array/list of the time in seconds and velocity in meters/seconds and plots them.
    Contains optional kwargs for label and title.
    '''
    plt.figure()
    if line != '':
        plt.plot(t,v, line, label=label)
    else:
        plt.plot(t,v, label=label)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.title(title)
    plt.legend()

