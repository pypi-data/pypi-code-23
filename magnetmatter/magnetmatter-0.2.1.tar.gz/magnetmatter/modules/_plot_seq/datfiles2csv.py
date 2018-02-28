# datfiles2csv.py

""" attempt to rewrite code to plot dioptas dat frames. It turned out that
already written code (that was working!) was easier to modify to rewrite. """
# import sys, os, numpy as np, pandas as pd, matplotlib.pyplot as plt
# sys.path.append(r"C:\AU-PHD\General_Data\_python\PyPi\magnetmatter\magnetmatter\modules")
# from find_tools import findfiles
# from auxiliary import natural_keys
#
# if 0:
#   """ this was rework of already almost working code. see below """
#   workingdir = r"C:\AU-PHD\General_Data\Report Petra\good_folder\good_work\done_refined\400oC_a"
#   os.chdir(workingdir)
#   dats = findfiles(".dat")
#   dats.sort(key=natural_keys)
#   print(len(dats), dats[0],dats[-1])
#
#   mylist = []
#   mymax = 0
#   mymax_index = 0
#   print("checking the maximum number of lines. "
#     "This varies due to internals of Dioptas")
#   dats = dats[0:len(dats)//10]
#   for num, dat in enumerate(dats):
#     tmp_max = 0
#     with open(dat, "r") as reading:
#       for line in reading:
#         if line[0] == "#":
#           continue
#         else:
#           tmp_max += 1
#       (mymax, mymax_index) = (mymax, mymax_index) if tmp_max < mymax else (tmp_max, num)
#
#   myzeros = np.zeros( shape=(mymax, len(dats)) )
#   for num,dat in enumerate(dats):
#     myload = np.loadtxt(
#       dat,
#       comments="#",
#       # dtype = {"names": ("2th_deg","I"), "formats": (np.float64, np.float64)},
#       )
#     myzeros[0:myload.shape[0],num] = myload[:,1]
#     if num == mymax_index:
#       angles = myload[:,0]
#     # print("myload.shape =",myload.shape)
#
#
#
#   frames = [num for num,dat in enumerate(dats)]
#   angles = myzeros[:,mymax_index]
#   """prepare meshgrids and plotting parameters"""
#   # angles = df.index.values
#   angle_mesh,time_mesh=np.meshgrid(angles, frames)
#   import pdb; pdb.set_trace();
#   # styles = [style for style in 'jet'.split()]
#
#   CS = plt.contourf(angle_mesh, time_mesh, signals)



""" working code! """

import os, numpy as np, pandas as pd, sys, re
import numpy as np, pandas as pd, re, os




sys.path.append(r"C:\AU-PHD\General_Data\_python\PyPi\magnetmatter\magnetmatter\modules")
from wrappers import time_response

@time_response
def genereate_CSV_from_dioptas_dat(workingdir = "", skipping = 10):
    """ generate CSV from dioptas .dat files.

    last edit: 2018-01-31

    Function is written to extract 2th values and Intensities from
    2D plots transformed to line diffractograms by the software Dioptas.

    OUTPUT:
        Saves a pd.DataFrame to "mycsv.csv" at "path/python_output".
    NOTE:
        if two frames have different number of angles, NaNs will be present.
        NaNs are replaced with zeroes.
    Note to Pelle:
        DO NOT TRY TO EXTRACT ERRORS. THERE ARE NONE GENERATED FROM DIOPTAS.
    """

    workingdir = workingdir if workingdir != "" else os.getcwd()
    os.chdir(workingdir)

    """get all dat files"""
    files = [d for d in os.listdir() if d.endswith(".dat")]

    """ skipping treatment if no dat files are found """
    if len(files) == 0:
      return pd.DataFrame

    """sorting the frames"""
    files.sort(key = natural_keys)

    """ only take every skipping'th frame to plot
    the higher number for skipping, the faster (but cruder)
    the visualization of the data frames will be. """
    files = files[::skipping]

    """extacting 2th and counts"""
    df = 0
    index = "angle"
    i = 0; imax = len(files)

    """ loops through all .dat files"""
    for dat in files:
      i += 1
      # if i-1 == imax:
      #     break
      frame = dat.strip(r".dat")
      """friendly output to user"""
      if i % 100 == 0:
        print(i, "of", imax,". df.shape =",df.shape)

      with open(dat) as f:
        """loads in data and merge on angles"""

        """ the dioptas generated dat files are created with numpy's
        .savetxt function. Therefore loadtxt is used without hesitation """
        loaded = np.loadtxt(f)

        """ transforming loaded numpy array to pandas dataframe """
        df_tmp = pd.DataFrame(loaded, columns = [index, frame])

        """ checking if df is a pandas.DataFrame """
        if type(df) != type(df_tmp):
          df = df_tmp
        else:
          """ legacy code... """
          # if df.shape[0] != df_tmp.shape[0]:
          #   # print("Uuuups, debugging time!")
          #   print("df.shape =", df.shape, " df_tmp.shape =", df_tmp.shape, "frame =", frame)

          """ merges dataframes by filling nonmatching dimensions with NaNs """
          df = df.merge(df_tmp, on = index, how = "outer")

    """ fills all NaN with zeroes """
    df = df.fillna(0)

    """ saves pd.DataFrame to .csv"""
    df.to_csv(os.path.join("_dats.csv"), index = False)

    return df



#
#
#




# mypath = r"C:\AU-PHD\General_Data\Report Petra\good_folder\good_work\done_refined\400oC_a"
#
# genereate_CSV_from_dioptas_dat(mypath)
# plotting_PETRApredata(mypath, minute_range = "tuple_of_low_high")

















  # end
