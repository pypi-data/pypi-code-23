"""Program to make power network model from transformer information and connections.
    Author: Sean Blake (blakese@tcd.ie)
    GitHub: https://github.com/TerminusEst/Power_Network

    Example data for the Horton (2012) network can be found here:
    https://github.com/TerminusEst/Power_Network/tree/master/Data

    These data files are also included with this package.

    *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=

    Required for this program is 2 inputs:

    1) csv file containing transformer info. The columns should be:

        SS_NAME = Subsation name (important to keep spelling uniform)
        SS_SYM = Substation symbol
        TF_SYM = Transformer symbol (or code: e.g, T1432)
        VOLTAGE = Highest operating voltage of the substation
        LAT = Latitude
        LON = Longitude
        TYPE = Type of transformer: 'A' = autotransformer, "YY" = Wye-Wye, "G" = grounded, "T" = Tee connection station.
        RES1 = High voltage resistance winding
        RES2 = Low voltage resistance winding
        GROUND = Ground resistance at substation
        SWITCH = Transformer ground switch: 0 = None, 1 = Open, 2 = Closed

    2) csv file containing substation connection info. The columns should be:
        FROM = Substation name from
        TO = Substation name to
        VOLTAGE = Voltage of connection
        CIRCUIT = To denote multiple lines per connection
        RES = Resistance of line.

    An example of the code running for the Horton et al 2012 test case paper is outlined below:


    import power_network_model as PNG
    ################################################################################

    # read in transformer file, generate substation data:
    filename = "Data/Horton_Trafo_Info.csv"
    ss_trafos, ss_connections, ss_meta = PNG.make_substations2(filename)

    # Generate connections between substations:
    filename = "Data/Horton_Connection_Info.csv"
    connections_twixt_stations = PNG.connections_adder(filename, ss_meta)

    ################################################################################
    # Write out the output file
    filename = "Data/Horton_Model_Output.txt"
    PNG.write_out(filename, ss_trafos, ss_connections, connections_twixt_stations)

"""

################################################################################
################################################################################
################################################################################

def make_substations2(filename):
    """ Read in file of transformer data, get each substation in correct form.

            Follows the conventions of:
            http://onlinelibrary.wiley.com/doi/10.1002/2016SW001499/full

            Parameters
            -----------
            filename = file which contains the transformer data with the headings:
              -> SS_NAME, SS_SYM, TF_SYM, CODE, VOLTAGE, LAT, LON, TYPE, RES1, 
                 RES2, GROUND, SWITCHABLE

            Returns
            -----------
            ss_trafos = transformer data in output format
              -> number, lat, lon, trans_resist, earth_resist, voltage, 
                 substation symbol, transformer code

            ss_connections = list of output data for internal connections
              -> nodefrom, nodeto, resistance, nan, nan, nan, voltage

            ss_meta = list of meta data for the substation
              -> Substation name, substation symbol, lat, lon, voltage, ground 
                 nodes, HV and LV busbar nodes
            
            -----------------------------------------------------------------

    """
    f = open(filename, 'r')
    data = f.readlines()
    f.close()

    # Read in data, skip first row (headings), skip last row (if empty)
    if data[-1] == "\n":
        master = [x.split(",") for x in data[1:-1]]
    else:
        master = [x.split(",") for x in data[1:]]

    substation_names, substation_volt, substation_sym = [], [], []

    for j in master:
        if j[0] not in substation_names:
            substation_names.append(j[0])
            substation_volt.append(j[2])
            substation_sym.append(j[1])

    master_substations = substation_sym

    ################################################################################
    # 2
    # Loop through trafos, add each to respective substation.

    master_raw = []
    for i in master_substations:
        temp_list = []

        for index, value in enumerate(master):
            if i == value[1]:
                temp_list.append(value)

        master_raw.append(temp_list)

    ################################################################################
    # 3
    # For each substation, calculate internal configuration

    ss_trafos, ss_connections, ss_meta = [], [], []
    count = 0
    for index, i in enumerate(master_raw):
        a, b, c, count = substation_internals(i, count)

        ss_trafos.append(a)
        ss_connections.append(b)
        ss_meta.append(c)

    return ss_trafos, ss_connections, ss_meta

################################################################################
################################################################################
################################################################################

def substation_internals(substation, count):
    """ Generate sinlge internal substation configuration with nodes and internal 
        connections.

            Follows the conventions of:
            http://onlinelibrary.wiley.com/doi/10.1002/2016SW001499/full

            Parameters
            -----------
            substation = list of transformers for one substation
            count = the node count before this substation

            Returns
            -----------
            transformers = list of output data for each node:
              -> number, lat, lon, trans_resist, earth_resist, voltage, 
                 substation symbol, transformer code

            connections = list of output data for internal connections
              -> nodefrom, nodeto, resistance, nan, nan, nan, voltage

            meta_info = list of meta data for the substation
              -> Substation name, substation symbol, lat, lon, voltage, ground 
                 nodes, HV and LV busbar nodes
            
            number = the node number after this substation
            -----------------------------------------------------------------

    """
    count += 1          # transformer count
    infsmall = 1e-10    # 0 resistance equivalent
    infbig = 1e10       # inf resistance equivalent
    dist_incr = 0.00001 # distance increment

    # Substation info from first trafo
    ss_name, ss_sym, tf_sym, ss_voltage = substation[0][:4]

    trafo_number = len(substation)  # number of transformers
    lat = float(substation[0][4])  # baditude
    lon = float(substation[0][5])  # longitude
    ground_res = float(substation[0][9])    # grounding resistance for substation

    transformers, connections, real_grounds = [], [], []
    meta_info = [ss_name, ss_sym, lat, lon, ss_voltage] 

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
    # some terminology:
    # HVss, LVss = HV and LV substation buses
    # Gt = Grounded transformer    
    # Gt_HVss = Connection between Gt and HVss

    # In the case that there is a single transformer at the substation:
    if trafo_number == 1:
        res1 = float(substation[0][7])     # high winding res
        res2 = float(substation[0][8])     # low winding res
        tf_type = substation[0][6]
        switch = int(substation[0][-1])

        if switch == 2:     # if the switch is open
            ground_res = infbig
        #-----------------------------------------------------------------------

        if tf_type == "YY":    # Single YY transformer
            HVss = [count, lat + dist_incr, lon, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            LVss = [count+1, lat - dist_incr, lon, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            Gt = [count+2, lat, lon, infsmall, ground_res, ss_voltage, ss_name, tf_sym, switch]

            Gt_HVss = [count, count+2, res1, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            Gt_LVss = [count+1, count+2, res2, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]

            transformers.extend([HVss, LVss, Gt])
            connections.extend([Gt_HVss, Gt_LVss])
            real_grounds.append(count+2)
            hilo = [count, count+1]
            number = int(count+2)

        #-----------------------------------------------------------------------

        if tf_type == "A":    # auto
            res1 = float(substation[0][7])*0.75     # high winding res
            res2 = float(substation[0][7])*0.25

            HVss = [count, lat + dist_incr, lon, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            Gt = [count+1, lat, lon, infsmall, ground_res + res2, ss_voltage, ss_name, tf_sym, switch]

            Gt_HVss = [count, count+1, res1, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]

            transformers.extend([HVss, Gt])
            connections.extend([Gt_HVss])
            real_grounds.append(count+1)
            hilo = [count, count+1]
            number = int(count+1)

        #-----------------------------------------------------------------------

        if tf_type == "G":    # "end" or "grounded" trafo
            transformers.append([count, lat, lon, res1, ground_res, ss_voltage, ss_name, tf_sym, switch])
            real_grounds.append(count)
            hilo = [count, count]
            number = int(count)

        #-----------------------------------------------------------------------

        if tf_type == "T":    # TEE
            transformers.append([count, lat, lon, infsmall, ground_res, ss_voltage, ss_name, tf_sym, 'nan'])
            real_grounds.append(count)
            hilo = [count, count]
            number = int(count)
    
        count = int(number)
        meta_info.append(real_grounds)
        meta_info.append(hilo)
        return transformers, connections, meta_info, count

    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
    # If there are multiple trafos, need HV and LV buses
    HVss = [count, lat + 2*dist_incr, lon - 0.5*dist_incr, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
    LVss = [count+1, lat - 2*dist_incr, lon + 0.5*dist_incr, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
    transformers.extend([HVss, LVss])
    substation_ground = float(substation[0][9])

    number = int(count)+2  # we start with number 2: 0 = HVss, 1 = LVss...
    for index, trafo in enumerate(substation):
        res1 = float(trafo[7])     # high winding res
        res2 = float(trafo[8])     # low winding res
        tf_type = trafo[6]
        tf_sym = trafo[2]
        switch = int(trafo[-1])

        if switch == 2:  # if the ground is open
            ground_res = infbig
        else:
            ground_res = substation_ground

        #-----------------------------------------------------------------------

        if tf_type == "YY":    # YY
            HVt = [number, lat + dist_incr, lon - index*dist_incr, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            HVt_HVss = [count, number, infsmall, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            number += 1

            Gt = [number, lat, lon - index*dist_incr, infsmall, ground_res * trafo_number, ss_voltage, ss_name, tf_sym, switch]
            real_grounds.append(number)
            Gt_HVt = [number-1, number, res1, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            number += 1

            LVt = [number, lat - dist_incr, lon - index*dist_incr, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            LVt_Gt = [number-1, number, res2, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            LVt_LVss = [count+1, number, infsmall, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            number += 1

            transformers.extend([HVt, Gt, LVt])
            connections.extend([HVt_HVss, Gt_HVt, LVt_Gt, LVt_LVss])

        #-----------------------------------------------------------------------

        if tf_type == "A":    # autotransformer

            res1 = float(trafo[7])*0.75     # high winding res
            res2 = float(trafo[7])*0.25

            HVt = [number, lat + dist_incr, lon - index*dist_incr, infsmall, infbig, ss_voltage, ss_name, "--", 'nan']
            HVt_HVss = [count, number, infsmall, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            number += 1

            Gt = [number, lat, lon - index*dist_incr, res2, (ground_res * trafo_number), 
                    ss_voltage, ss_name, tf_sym, switch]

            Gt_HVt = [number-1, number, res1, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            Gt_LVss = [count+1, number, infsmall, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            real_grounds.append(number)
            number += 1

            transformers.extend([HVt, Gt])
            connections.extend([HVt_HVss, Gt_HVt, Gt_LVss])

        #-----------------------------------------------------------------------

        if tf_type == "G":   # "end" or "grounded" trafo
            Gt = [number, lat, lon - index*dist_incr, res1, ground_res * trafo_number, ss_voltage, ss_name, tf_sym, switch]
            print(res1, ground_res * trafo_number, ss_voltage, ss_name, tf_sym)
            real_grounds.append(number)
            Gt_HVss = [number, count, infsmall, 'nan', 'nan', 'nan', 'nan', 'nan', ss_voltage]
            number += 1

            transformers.extend([Gt])
            connections.extend([Gt_HVss])#, Gt_tGt])

    meta_info.append(real_grounds)
    meta_info.append([count, count+1])

    return transformers, connections, meta_info, number-1

################################################################################
################################################################################
################################################################################

def resistance_parallel(resistances):
    """ Dirty wee function to calculate parallel resistances"""

    res = 0
    for i in resistances:
        res += 1./i

    return 1./res

################################################################################
################################################################################
################################################################################

def connections_adder(filename, substation_meta):

    """Creates the connections between substations with correct nodes.

            Parameters
            -----------
            filename = location of file with connection info. Must be in format:
              -> SS_NAME, SS_SYM, TF_SYM, VOLTAGE, LAT, LON, TYPE, RES1, RES2, GROUND, SWITCHABLE

            substation_meta = list of meta-info for substations. Generated from
                              substation_internals function

            Returns
            -----------
            ouput = list of output data for connections. In the form:
              -> nodefrom, nodeto, resistance, lonfrom, latfrom, lonto, latto, 
                 nan, line voltage

            -----------------------------------------------------------------
    """
    # read in the file
    #-----------------------------------------------------------------------
    f = open(filename, 'r')
    data = f.readlines()
    f.close()

    if data[-1] == "\n":
        raw = [x.split(",") for x in data[1:-1]]
    else:
        raw = [x.split(",") for x in data[1:]]

    #-----------------------------------------------------------------------
    # work out resistances (incl. parallel lines)

    line_ids, resistances = [], []  # from, to, volt

    for i in raw:
        namefrom, nameto, volt, circuit, res = i
        
        idd = [namefrom, nameto, volt]

        if idd not in line_ids:
            line_ids.append(idd)
            resistances.append([float(res)])
        else:
            resistances[line_ids.index(idd)].append(float(res))

    for index, value in enumerate(resistances):
        if len(value) == 1:
            line_ids[index].append(value[0])
        else:
            line_ids[index].append(resistance_parallel(value))

    #-----------------------------------------------------------------------
    # now to work out the connections between nodes
    
    ss_meta = [x[0] for x in substation_meta]
    output = []

    for j in line_ids:
        namefrom, nameto, volt, res = j

        index1 = ss_meta.index(namefrom)
        volt1 = int(substation_meta[index1][4])
        hi1, lo1 = substation_meta[index1][6]
        lonfrom = substation_meta[index1][2]
        latfrom = substation_meta[index1][3]
        
        index2 = ss_meta.index(nameto)
        volt2 = int(substation_meta[index2][4])
        hi2, lo2 = substation_meta[index2][6]
        lonto = substation_meta[index2][2]
        latto = substation_meta[index2][3]

        line_volt = int(volt)   # voltage of power line

        if volt1 == volt2: # if the substations are same voltage
            if line_volt < volt1:    # if voltage of line is < voltage of substation - LO to LO
                thingy = sorted([lo1, lo2])

            else:               # if voltage of line == voltage of substation - HI to HI
                thingy = sorted([hi1, hi2])

        elif volt1 > volt2:  # LO to HI
            thingy = sorted([lo1, hi2])

        else:  # HI to LO
            thingy = sorted([hi1, lo2])

        connection = [thingy[0], thingy[1], res, lonfrom, latfrom, lonto, latto, line_volt]

        output.append(connection)

    return output

################################################################################
################################################################################
################################################################################

def write_out(filename, ss_trafos, ss_connections, refined_connections2):
    """Write out model to file

            Parameters
            -----------
            filename = location of output file
              -> see readme for more info on this format.

            substation_meta = list of meta-info for substations. Generated from
                              substation_internals function

            Returns
            -----------
            ouput = list of output data for connections. In the form:
              -> nodefrom, nodeto, resistance, nan, nan, nan, line voltage

            -----------------------------------------------------------------
    """

    f = open(filename, 'w')

    for i in ss_trafos:
        for j in i:
            f.write(str(j[0]) + "\t" + str(j[1]) + "\t" + str(j[2]) + "\t" + str(j[3]) + "\t" + str(j[4]) + "\t" + str(j[5]) + "\t" + str(j[6]) + "\t" + str(j[7]) + "\t" + str(j[-1]) + "\n") 

    for i in ss_connections:
        for j in i:
          f.write(str(j[0]) + "\t" + str(j[1]) + "\t" + str(j[2]) + "\t" + str(j[3]) + "\t" + str(j[4]) + "\t" + str(j[5]) + "\t" + str(j[6]) + "\t" + str(j[7]) + "\tnan\n") 

    for j in refined_connections2:
        f.write(str(j[0]) + "\t" + str(j[1]) + "\t" + str(j[2]) + "\t" + str(j[3]) + "\t" + str(j[4]) + "\t" + str(j[5]) + "\t" + str(j[6]) + "\tnan\t" + str(j[7]) + "\n") 

    f.close()

    print("Successfully written output file!")

################################################################################
################################################################################
################################################################################















































