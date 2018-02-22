#!/usr/bin/env python3

import math
import numpy as np
import spiceypy as spice
import matplotlib as mpl

# Fix for using matplotlib.pyplot on a Mac OS X system (untested on other OS)
mpl.use('TkAgg')
import matplotlib.pyplot as plt


def tconst(time_lower, time_upper, resolution=3600):
    """
    Returns the start_date and end_date in et format,
    the number of intervals for the given resolution
    and the array of et time values with given
    resolution and length = num_interval

    :param time_lower: lower boundary of time window
    :param time_upper: upper boundary of time window
    :param resolution: Step size between time array elements [seconds]
    :return:
    converts time_lower and time_upper into et format (if not already),
    returns the number of elements in the time array, and returns an
    array of et elements with step size = resolution and length = num_intervals+1
    """

    if isinstance(time_lower, str):
        et1 = spice.str2et(time_lower)
        et2 = spice.str2et(time_upper)
    else:
        et1 = time_lower
        et2 = time_upper

    num_intervals = math.ceil((et2 - et1)/resolution)
    times = np.arange(0, num_intervals) * (et2 - et1) / num_intervals + et1

    return et1, et2, num_intervals, times


def geometry(time_lower, time_upper, main_body, observer,
             other_bodies=[], aberration_correction="LT+S", resolution=3600):
    """
    :param time_lower: lower boundary of time window
    :type time_lower: int [in et format]
    :param time_upper: upper boundary of time window
    :type time_lower: int [in et format]
    :param main_body: The central body of the function i.e. Jupiter
    :type main_body: str
    :param observer: The spacecraft or observing body i.e. JUICE
    :type observer: str
    :param other_bodies: Additional bodies to be calculated from observer i.e. Europa
    :type other_bodies: str [i.e. other_bodies = 'Europa', 'Ganymede', 'Callisto']
    :param aberration_correction: The type of aberration correction to use, the default is 'LT+S'
    :param resolution: The resolution (step size) of the time array
    :type resolution: int
    :return:
    Returns the phase_angle, distance, angular_diameter, solar_elongation,
    body_separation as arrays of size (len(bodies), num_intervals (see tconst))
    And returns the main_body's radius in km
    """

    if len(other_bodies) == 0:
        bodies = [main_body]
    else:
        bodies = [main_body]
        for i in range(0,len(other_bodies)):
            bodies.append(other_bodies[i])

    [et1, et2, num_intervals, times] = tconst(time_lower, time_upper, resolution)

    phase_angle = np.zeros((len(bodies), num_intervals))
    distance = np.zeros((len(bodies), num_intervals))
    angular_diameter = np.zeros((len(bodies), num_intervals))
    solar_elongation = np.zeros((len(bodies), num_intervals))
    body_separation = np.zeros((len(bodies), num_intervals))
    main_body_radius = spice.bodvrd( bodies[0], 'RADII', 3 )
    ilumth = 'Ellipsoid'
    submth = 'Near Point/Ellipsoid'

    for i in range(0,len(bodies)):

        target = bodies[i]

        print(bodies)

        target_radius = spice.bodvrd(target, 'RADII', 3)
        reference_frame   = 'iau_' + target

        for j in range(0, num_intervals):

            [ssolpt, xxx, yyy] = spice.subslr(submth, target, times[j], reference_frame,
                                  aberration_correction, observer)

            [sscpt, trgepc, srfvec_sc] = spice.subpnt(submth, target, times[j],
                                            reference_frame, aberration_correction,
                                            observer)

            [trgepc, srfvec, sslphs, slinc, emissn] = spice.ilumin(ilumth, target, times[j],
                                                    reference_frame, aberration_correction, observer,
                                                    ssolpt)

            sslphs = sslphs * spice.dpr()

            [pos_obs, ltime] = spice.spkpos(observer, times[j], reference_frame,
                                   aberration_correction, 'Sun')

            [pos_bdy, ltime] = spice.spkpos(target, times[j], reference_frame,
                                   aberration_correction, 'Sun')

            phase_angle[i, j] = sslphs

            distance[i, j] = math.sqrt(srfvec_sc[0] ** 2 + srfvec_sc[1] ** 2
                                      + srfvec_sc[2] ** 2) / main_body_radius[0]

            angular_diameter[i, j] = spice.dpr() * 4 * target_radius[0] /   \
                                    ((distance[i, j] * main_body_radius[0]) + target_radius[0])

            body_separation[i, j] = spice.vsep(pos_obs, pos_bdy) * spice.dpr()

            solar_elongation[i, j] = 180 - (phase_angle[i, j] + body_separation[i, j])

    return phase_angle, distance, angular_diameter, \
           solar_elongation, body_separation,       \
           main_body_radius[0]


def tickset(winl, winh):
    """
    :param winl: et of lower boundary in seconds before CA (winl > 0)
    :param winh: et of upper boundary in seconds after CA
    :return:
    Returns the interval (step size) between x ticks,
        the lower boundary (bndl), the upper boundary (bndh),
        the units of the ticks (str) and the unit conversion
        to seconds (if units == hours, unit == 3600)
    """

    if math.ceil(winl/3600) <= 4 and math.ceil(winh/3600) <= 4:
        interval = 20
        bndl = 20 * math.ceil((winl/60)/20)
        bndh = 20 * math.ceil((winh/60)/20)
        units = 'minutes'
        unit = 60
    elif math.ceil(winl / 3600) <= 12 and math.ceil(winh / 3600) <= 12:
        interval = 1
        bndl = interval * math.ceil((winl / 3600) / interval)
        bndh = interval * math.ceil((winh / 3600) / interval)
        units = 'hours'
        unit = 3600
    elif math.ceil(winl / 3600) <= 24 and math.ceil(winh / 3600) <= 24:
        interval = 2
        bndl = interval * math.ceil((winl / 3600) / interval)
        bndh = interval * math.ceil((winh / 3600) / interval)
        units = 'hours'
        unit = 3600
    elif math.ceil(winl / 3600) <= 48 and math.ceil(winh / 3600) <= 48:
        interval = 6
        bndl = interval * math.ceil((winl / 3600) / interval)
        bndh = interval * math.ceil((winh / 3600) / interval)
        units = 'hours'
        unit = 3600
    elif math.ceil(winl / spice.spd()) <= 10 and math.ceil(winh / spice.spd()) <= 10:
        interval = 1
        bndl = interval * math.ceil((winl / 3600) / interval)
        bndh = interval * math.ceil((winh / 3600) / interval)
        units = 'days'
        unit = spice.spd()
    elif math.ceil(winl / spice.spd()) <= 30 and math.ceil(winh / spice.spd()) <= 30:
        interval = 2
        bndl = interval * math.ceil((winl / 3600) / interval)
        bndh = interval * math.ceil((winh / 3600) / interval)
        units = 'days'
        unit = spice.spd()
    else:
        interval = round((((winh + winl) / spice.spd()) / 30) / 20) * 20

        if interval == 0:
            interval = 20

        bndl = interval * math.ceil(winl/spice.spd() / interval)
        bndh = interval * math.ceil(winh / spice.spd() / interval)
        units = 'days'
        unit = spice.spd()

    return interval, bndl, bndh, units, unit


def plot(xData, yData, main_body, bodyRadius,
         other_bodies=[], Closest_Approach=0,
         ptype='distlog', xLabel='', y1Label='',
         y2Label='', title='', resolution=3600):
    """
    :param xData: Data to be plotted on the x axis
    :type xData: array(1,N) where N = num_intervals (see tconst)
    :param yData: Data to be plot on the y axis
    :type yData: array(x,N) where x = len(bodies) and N = num_intervals (see tconst)
    :param main_body: The central body of the function i.e. Jupiter
    :type main_body: str
    :param bodyRadius: The central body's radius [km]
    :param other_bodies: Additional bodies to be calculated from observer i.e. Europa
    :type other_bodies: str [i.e. other_bodies = 'Europa', 'Ganymede', 'Callisto']
    :param Closest_Approach: The time of closest approach to the central body
    :type Closest_Approach: str [e.g. CA = '2025 FEB 10 18:00:00']
    :param ptype: The type of plot to be plotted. Current option are:
            'distlog'
    :type ptype: str
    :param xLabel: Label for the x axis; if no input a default label is used
    :param y1Label: Label for the LHS y axis; if no input a default label is used
    :param y2Label:
        Label for the RHS y axis (only applicable for certain types
        of plot [ptype]): if no input a default label is used
    :param title: Title for the plot; if no input a default title is used
    :param resolution: The resolution (step size) of the time array
    :type resolution: int
    :return: Displays a plot for the input parameter type. No variables are returned
    """

    if len(other_bodies) == 0:
        bodies = [main_body]
    else:
        bodies = [main_body]
        for i in range(0,len(other_bodies)):
            bodies.append(other_bodies[i])

    xDatast = list()

    if Closest_Approach == 0:
        for i in range(0, len(xData)):
            holder = spice.et2utc(xData[i], 'ISOC', 0)
            xDatast.append(holder)

        if ptype == 'distlog':
            plotdistlog_s(xDatast, yData, bodies, bodyRadius,
                        xLabel, y1Label, title, deg_rotate=90)

    else:
        if isinstance(Closest_Approach, str):
            Closest_Approach = spice.str2et(Closest_Approach)

        try:
            winl = Closest_Approach - xData[0]
        except:
            print(' ')
            print(['No dimension for either CA or x axis data during event '
                   + spice.et2utc(Closest_Approach, 'C', 0)])
            print(' ')
            return

        winh = xData[len(xData)-1] - Closest_Approach

        [interval, bndl, bndh, units, unit] = tickset(winl, winh)

        for i in range(0, len(xData)):
            xData[i] = (xData[i] - Closest_Approach) / unit

        if ptype == 'distlog':
            plotdistlog(xData, yData, bodies, bodyRadius,
                        xLabel, y1Label, title, unit, units,
                        resolution, interval)

    return


def plotdistlog(xData, yData, bodies, bodyRadius,
                xLabel, y1Label, title, unit, units,
                resolution, interval=1, deg_rotate=0):
    """
    :param xData: Data to be plotted on the x axis
    :type xData: array(1,N) where N = num_intervals (see tconst)
    :param yData: Data to be plot on the y axis
    :type yData: array(x,N) where x = len(bodies) and N = num_intervals (see tconst)
    :param bodies: list of bodies to be plotted, bodies = main_body + other_bodies
    :param bodyRadius: The central body's radius [km]
    :param xLabel: Label for the x axis; if no input a default label is used
    :param y1Label: Label for the LHS y axis; if no input a default label is used
    :param title: Title for the plot; if no input a default title is used
    :param unit: The unit conversion to seconds i.e. for hours unit = 3600
    :type unit: int
    :param units: The unit type i.e. 'hours'
    :type units: str
    :param resolution: The resolution (step size) of the time array
    :type resolution: int
    :param interval: number of intervals in the xTicks
    :param deg_rotate: roatation of x axis labels; default = 0
    :return:
    """

    yData = yData * bodyRadius

    yliml = np.zeros((len(bodies), 1))
    ylimh = np.zeros((len(bodies), 1))

    plt.figure(figsize=(8, 6.5))

    for i in range(0, len(bodies)):

        yliml[i] = np.min(yData[i, :])
        ylimh[i] = np.max(yData[i, :])

        [col] = plotcoltest(i)

        plt.semilogy(xData, yData[i, :])

    ticks = list()

    numel = math.ceil((interval * unit) / resolution)

    for i in range(0, math.ceil(len(xData)/numel)):
        if i * numel < len(xData):
            ticks.append(round(xData[i * numel]))

    plt.xticks(ticks)
    plt.xlabel(xLabel)
    plt.xticks(rotation=deg_rotate)

    miny = 10 ** (math.floor(math.log10(np.min(yliml))))
    maxy = 10 ** ( 1 + math.floor(math.log10(np.max(ylimh))))

    plt.ylim([miny, maxy])
    plt.ylabel(y1Label)
    plt.grid()
    plt.grid(b=True, which='minor', color='k', linestyle='-', alpha=0.25)

    if len(xLabel) == 0:
        xLabel = 'Time to Closest Approach [' + units + ']'

    if len(y1Label) == 0:
        y1Label = 'Altitude [km]'

    if len(title) == 0:
        title = 'Altitude of spacecraft during the given time window'

    plt.title(title)
    plt.ylabel(y1Label)
    plt.xlabel(xLabel)

    plt.tight_layout()
    plt.legend(bodies)
    plt.show()

    return

def plotdistlog_s(xData, yData, bodies, bodyRadius,
                  xLabel, y1Label, title, deg_rotate = 0):
    """
    :param xData: Data to be plotted on the x axis
    :type xData: array(1,N) where N = num_intervals (see tconst)
    :param yData: Data to be plot on the y axis
    :type yData: array(x,N) where x = len(bodies) and N = num_intervals (see tconst)
    :param bodies: list of bodies to be plotted, bodies = main_body + other_bodies
    :param bodyRadius: The central body's radius [km]
    :param xLabel: Label for the x axis; if no input a default label is used
    :param y1Label: Label for the LHS y axis; if no input a default label is used
    :param title: Title for the plot; if no input a default title is used
    :param deg_rotate: roatation of x axis labels; default = 0
    :return:
    """

    interval = math.ceil(len(xData)/20)

    ticks = list()

    for i in range(0, 20):
        if i * interval < len(xData):
            ticks.append(xData[i * interval])

    yData = yData * bodyRadius

    yliml = np.zeros((len(bodies), 1))
    ylimh = np.zeros((len(bodies), 1))

    plt.figure(figsize=(8, 8))

    for i in range(0, len(bodies)):

        yliml[i] = np.min(yData[i, :])
        ylimh[i] = np.max(yData[i, :])

        [col] = plotcoltest(i)

        plt.semilogy(xData, yData[i, :])

    plt.xticks(ticks, ticks)
    plt.xlabel(xLabel)
    plt.xticks(rotation=deg_rotate)

    miny = 10 ** (math.floor(math.log10(np.min(yliml))))
    maxy = 10 ** (1 + math.floor(math.log10(np.max(ylimh))))

    plt.ylim([miny, maxy])
    plt.ylabel(y1Label)
    plt.grid()
    plt.grid(b=True, which='minor', color='k', linestyle='-', alpha=0.25)

    if len(xLabel) == 0:
        xLabel = 'Date [YYYY-MM-DDTHH:MM:SS]'

    if len(y1Label) == 0:
        y1Label = 'Altitude [km]'

    if len(title) == 0:
        title = 'Altitude of spacecraft during the given time window'

    plt.title(title)
    plt.ylabel(y1Label)
    plt.xlabel(xLabel)

    plt.tight_layout()
    plt.legend(bodies)
    plt.show()

    return


def plotcoltest(i):
    """
    :param i: The counter for the number of bodies plotted (up to and including current plot)
    :return: col: The colour of the plot for the ith body
    """

    if i == 1:
        col = 'r'
    elif i == 2:
        col = 'b'
    elif i == 3:
        col = 'g'
    elif i == 4:
        col = 'm'
    else:
        col = 'c'

    return col
