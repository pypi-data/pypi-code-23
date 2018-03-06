import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import curve_shortening_flow

def update_line(num,vertex,line,line_cm):
    """
    Update method for the matplotlib animator class

    This function purely serves as a method for inputting the new data into 
    the animation.

    Parameters
    ----------
    num: int
        Position in the animation frame counter
    vertex: dictionary
        Dictionary of all the vertices.
    line: plot line
        Line of the vertices which are updated
    line_cm: plot line
        Line of the CM, that is updated.

    Returns
    -------
    line: plot line
        Line of the vertices, which was handed to the method
    line_cm: plot line
        Line of the CM, which was handed to the method
    """
    line.set_data(
        np.append(vertex[num][:,0],np.array([vertex[num][0,0]]),axis=0),
        np.append(vertex[num][:,1],np.array([vertex[num][0,1]]),axis=0))
    #line.set_data(vertex[num][:,0],vertex[num][:,1])
    cm = curve_shortening_flow.evaluation.center_mass(vertex[num])
    n,_ = vertex[num].shape
    line_cm.set_data(cm[0],cm[1])
    return line, line_cm, 

