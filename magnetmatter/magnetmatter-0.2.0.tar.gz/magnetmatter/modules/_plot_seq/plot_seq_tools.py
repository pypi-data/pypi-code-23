# plot_seq_tools.py

import os, pandas as pd, matplotlib.pyplot as plt, numpy as np
from auxiliary import cm2inch



def plotphasevolumefractions(notebook, outpath):
  """ plotting the phase volume fractions from seqdf for all phases in refined model """

  """ making a list of weight_fractions for all phases. """
  for col in notebook.seqdf.columns:
    if "Weight_Fraction" in col and not col.endswith("_err"):
      notebook.newlist.append(col)

  """ reducing the number of displayed datapoints to 20 """
  view = [int(i) for i in np.linspace(0, notebook.seqdf.shape[0]-1, 20)]

  """ initializing axes object """
  ax = None

  """ choosing plotting style """
  plt.style.use("seaborn-darkgrid") # plt.style.available

  """ plotting phase volume fraction for all phases in model """
  for phase, col in zip(notebook.phases, notebook.newlist):
    if ax == None:
      ax = notebook.seqdf.iloc[view].plot(y=col,yerr=col+"_err", label = phase, figsize = cm2inch(8,6) )
    else:
      notebook.seqdf.iloc[view].plot(y=col,yerr=col+"_err", ax = ax, label = phase)

  """ handling graph text """
  ax.set_xlabel("frame [index]")
  ax.set_ylabel("Phase Volume Fraction [%]")
  ax.set_title("PVF_" + notebook.taskname)

  """ ensure output directory exists """
  try:
    os.makedirs(outpath)
  except:
    pass


  plt.tight_layout()
  """ saving graph """
  plt.savefig(os.path.join(outpath, notebook.taskname+"_PVF.png"), dpi = 500)

  """ avoid memory leak """
  plt.close()
  return

def size_plot(notebook, outpath):
  """ plotting the app. cryst. sizes found in sizedf """


  """ setting all elements with value higher than 200 nm to NaN
  because values above 100 nm are already out of the instrumental resolution"""
  notebook.sizedf = notebook.sizedf.where(notebook.sizedf < 200)
  notebook.sizedf = notebook.sizedf.dropna()

  """ check if sizedf is empty """
  if notebook.sizedf.size == 0:
    message = "notebook.sizedf.size = " + str(notebook.sizedf.size)
    with open(os.path.join(outpath,notebook.taskname+".txt"), "w") as writing:
      writing.write(message)
    print("        " + message)
    return

  """ initilizaing axes object used to plot multiple data in same graph """
  ax = None

  """ choosing plotstyle """
  plt.style.use("seaborn-darkgrid") # plt.style.available

  """ some string names """
  absize = "ab-size"
  lorsize = "Y-cos"

  """ reducing the number of points displayed to 20 """
  view = [int(i) for i in np.linspace(0, notebook.sizedf.shape[0]-1, 20)]

  """ plotting app. cryst. sizes for all phases in refined model """
  for phase, col in zip(notebook.phases, notebook.lorsizelist):
    target = absize + col.strip(lorsize)
    if ax == None:
      ax = notebook.sizedf.iloc[view].plot(y=target,yerr=target+"_err", label = phase, figsize = cm2inch(8,6))
    else:
      notebook.sizedf.iloc[view].plot(y=target,yerr=target+"_err", ax = ax, label = phase)

  """ setting up graph text """
  ax.set_xlabel("frame [index]")
  ax.set_ylabel("app. cryst. size [nm]")
  ax.set_title(notebook.taskname)

  """ ensure outputh directory exists """
  try:
    os.makedirs(outpath)
  except:
    pass

  """ ensuring every text is within plot """
  plt.tight_layout()
  """ saving plot in ./root/_mytest """
  plt.savefig(os.path.join(outpath,notebook.taskname+".png"), dpi = 500)

  """ avoiding memory leak """
  plt.close()
  return


from datetime import datetime
import pandas as pd, os, numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker

def plotting_PETRApredata(df, outpath, minute_range = "tuple_of_low_high", printsize = "two_in_docx"):
  """plotting of saved pd.DataFrame as .csv prepared from dioptas .dat"""

  """ checking if dataframe is empty """
  if df.empty:
    print("--no data frames have been found!")
    return

  """preparing pd.DataFrame"""
  # os.chdir(path)
  # os.chdir("_python_output")
  # csv = [csv for csv in os.listdir() if csv.endswith(".csv")][-1]
  # df = pd.read_csv("_dats.csv")
  index = "angle"
  df = df.set_index(index)


  """ prepare minutes array"""
  duration_frame = 5 # seconds, blindly hardcoded...
  nb_of_frames = len(df.columns.values)

  """ converts the frames, e.g. frame18, frame19, .. frameN to integer list [18, 19, .., N] """
  myframes = [int(index.strip("frame")) for index in df.columns]

  """ blindly defines the first frame e.g. frame193 to be zero point in time """
  myframes = [integ - myframes[0] for integ in myframes]
  # print("myframes[0:10] =",myframes[0:10])
  # import pdb; pdb.set_trace();
  # minutes = np.arange(1, nb_of_frames + 1) * (duration_frame / 60.0)
  minutes = [frame * (duration_frame / 60.0) for frame in myframes]

  """ truncate DataFrame if user asks for it
  truncation is done by indicating what (x1,x2) minutes to include"""
  if type(minute_range) is type(tuple()):
    lower_bound, higher_bound = minute_range
    con1 = minutes > lower_bound
    df = df.iloc[:, con1]
    minutes = minutes[con1]
    con2 = minutes < higher_bound
    df = df.iloc[:, con2]
    minutes = minutes[con2]

    """check if any values are left"""
    if len(minutes) == 0:
      print("no values to plot for",minute_range, "in", path)
      # import pdb; pdb.set_trace()
      return 1

  """prepare meshgrids and plotting parameters"""
  angles = df.index.values
  angle_mesh,time_mesh=np.meshgrid(angles, minutes)
  signals = df.values.T
  styles = [style for style in 'jet gnuplot'.split()]

  """ these are styles that have better contrast:
  choosen_cmaps = "gnuplot gnuplot2 jet ocean viridis Paired Oranges PuBu " +\
      "PuBuGn PuRd Reds YlGn YlGrBu YlOrRd cool"
  """

  """higher number for nbin yields higher level of detail in plot"""
  nbins = [20,100] # 10 does not show the weak features... no difference between 100 and 200


  """ sizes of figure, ticks, labels and legends """
  factor = 2

  figsize = cm2inch(8,6) # two in word
  figsize = cm2inch(17,17*3/4) # one in word
  xlabelsize = 5 * factor
  ylabelsize = 5 * factor
  xticksize =  5 * factor
  yticksize =  5 * factor # made
  titlesize =  5 * factor
  # import pdb; pdb.set_trace();

  """ doing the actual plotting """
  for nbin in nbins:
    levels = MaxNLocator(nbins=nbin).tick_values(signals.min(), signals.max())
    for style in styles:
      plt_cmap = plt.get_cmap(style)
      fig = plt.figure(figsize=figsize)
      CS = plt.contourf(angle_mesh, time_mesh, signals,
                        cmap=plt_cmap,
                        levels = levels
                        )

      """ getting the axis object """
      ax = plt.gca()

      """ setting up xlabel and ylabel """
      plt.xlabel(r'2$\theta$-Value', size = xlabelsize)
      ylabel = plt.ylabel('time [min]', size = ylabelsize)


      """ changing the size of x ticks"""
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(xticksize)

      """ changing yticks and their size"""
      minutes_simplified = [int(i) for i in minutes]
      plt.yticks(minutes_simplified)

      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(yticksize)


      """ adding visual clue for each frame
        ADDS:
          a dotted red lines for each timestamp
        NOTE:
          do not use fo x-ray data. dataframes are too frequent"""
      # xlist = [min(angles), max(angles)]
      # for y in minutes: # dotted lines
      #     plt.plot(xlist,[y, y], "--r", linewidth=1) # dotted lines

      """ setting up second y-axis for temperature
      NOTE:
        no temperature data for PETRA x-rays"""
      # ax2 = ax.twinx()
      # ylabel2 = ax2.set_ylabel("temp [$^o$C]", size = ylabelsize)
      # plt.yticks(minutes, temp_simplified, rotation = 0)
      # for tick in ax2.yaxis.get_ticklabels():
      #     tick.set_fontsize(yticksize)
        # tick.set_fontsize('large')
        # tick.set_fontname('Times New Roman')
        # tick.set_color('blue')
        # tick.set_weight('bold')

      """ showing only time-yticklabel every tick_spacing """
      limit = max(minutes) - min(minutes)
      if limit <= 20:
        tick_spacing = 1 # min
      if limit <= 60:
        tick_spacing = 5 # min
      else:
        tick_spacing = 10 # min


      ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

      """ removing every second temp-yticklabel """
      # for label in ax2.yaxis.get_ticklabels()[0::2]:
      #     label.set_visible(False)

      """ rotating and repositioning the ylabels """
      ax.yaxis.set_label_coords(0,1.05)
      ylabel.set_rotation(0)
      # ax2.yaxis.set_label_coords(1,1.1)
      # ylabel2.set_rotation(0)

      """ setting title """
      system = os.getcwd().split("\\")[-1] # this is the first supra-folder
      title_ypos = 1.03 # percent of canvas.
      plt.title(system, size = titlesize, y = title_ypos)

      """ enable tight layout """
      plt.tight_layout()  # do not use with altered ylabels.


      """ saving plot , outfolder has already been created """
      figname = style + "_nbin" + str(nbin) + ".png"
      fig.savefig( os.path.join(outpath,figname), dpi = 500 )
      plt.close() # save pc from crashing!
  return 0


















# end
