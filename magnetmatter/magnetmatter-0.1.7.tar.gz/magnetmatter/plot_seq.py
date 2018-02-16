# plot_seq.py

import shutil, sys, os, pandas as pd

""" magnetmatter modules """
from find_tools import *
import plot_seq_tools
import seqfile2csv
import datfiles2csv
import extract_pcr
import seqcsv2sizecsv


class Notebook():
  """ reduce the need to pass several arguments to different functions """
  def __init__(self):
    self.lorsizelist = []
    self.newlist = []
    self.phases = []
    self.wavelength = 0
    self.taskname = ""
    self.seqdf = pd.DataFrame
    self.sizedf = pd.DataFrame


def plot_seq(workingdir = ""):
  """ workingdir is ./root of project.
  Searches all subfolders,
  creates plots and store in ./root/_mytest in separate experiment folders. """

  workingdir = workingdir if workingdir != "" else os.getcwd()

  """ important: setting working directory """
  os.chdir(workingdir)

  """ cleaning up output folder """
  try:
    sys.stdout.write("... removing \"_mytest\" folder")
    shutil.rmtree("_mytest")
    sys.stdout.write(" - SUCCESFULLY REMOVED!\n")
  except:
    sys.stdout.write(" - FAILURE!\n")
    pass

  """ finding all folders with presumed experimental data """
  experiment_folders = findfolders_abspath()
  for experiment in experiment_folders:
    print("--inside experiment folder:", os.path.basename(experiment))
    """ ignore certain experiments. should be removed later """
    if os.path.basename(experiment) in [exp for exp in "400oC_a 400oC_c".split()]:
      print("    skipping current experiment.")
      continue

    """ important: setting working folder """
    os.chdir(experiment)
    """ defining the folder where plots will be saved """
    outpath = os.path.join(workingdir, "_mytest", os.path.basename(experiment))
    try:
      os.makedirs(outpath)
    except:
      pass

    """ generating or reading in data frames """
    print("    working on visualization of dat files")
    if "_dats.csv" in os.listdir():
      datdf = pd.read_csv("_dats.csv")
    else:
      datdf = datfiles2csv.genereate_CSV_from_dioptas_dat(workingdir = experiment)

    """ plotting data frames """
    plot_seq_tools.plotting_PETRApredata(datdf, outpath, minute_range = "tuple_of_low_high")

    """ finding all folders with a sequentially refined model """
    refinement_folders = findfolders_abspath()

    """ parsing seq file to extract information and calculating the
    app. cryst. size to plot along with phase volume fractions """
    for refinement in refinement_folders:
      print("    working on:", os.path.basename(refinement))
      # if os.path.basename(refinement) != "_Fe_272_to_205":
      #   print("    skipping")
      #   continue

      """ important: setting new working directory """
      os.chdir(refinement)

      """ defining object to store information passed between functions. """
      notebook = Notebook()
      seq = findfile_abspath(".seq")

      """ find the pcr with shortest filename """
      pcr = findfiles(".pcr")
      pcr.sort(key=lambda x: len(x))
      pcr = pcr[0]

      """ extracting list with phasenames """
      notebook.phases = extract_pcr.getphases(pcr)

      """ extracting wavelength """
      notebook.wavelength = extract_pcr.getwavelength(pcr)

      """ storing the folder name of the sequentially refined model """
      notebook.taskname = os.path.basename(os.getcwd())

      """ check if _seq.csv exists and if it has been changed later than its
      parent .pcr file. This saves some computing power and man-hour.
      """
      try:
        seqcsvpath = os.path.abspath("_seq.csv")
        seqcsv_creation_time = os.stat(seqcsvpath).st_mtime
        pcr_creation_time = os.stat(pcr).st_mtime
        if seqcsv_creation_time < pcr_creation_time:
          seqcsvpath = seqfile2csv.seq2csv(seq)
      except:
        """ generate _seq.csv if none is found """
        seqcsvpath = seqfile2csv.seq2csv(seq)

      """ reading the the existing or newly created _seq.csv """
      notebook.seqdf = pd.read_csv(seqcsvpath, index_col = "NEW_REFINEMENT")

      """ finding the lorentizian size broadening parameters used for
      calculating the app. cryst. sizes """
      for col in notebook.seqdf.columns:
        if col.startswith("Y-cos") and not col.endswith("_err"):
          notebook.lorsizelist.append(col)
      plot_seq_tools.plotphasevolumefractions(notebook, outpath)

      """ check if _size.csv exists and if it has been changed compared to
      the parent .pcr. """
      try:
        sizecsvpath = os.path.abspath("_size.csv")
        sizecsv_creation_time = os.stat(sizecsvpath).st_mtime
        pcr_creation_time = os.stat(pcr).st_mtime
        if sizecsv_creation_time < pcr_creation_time:
          notebook.sizedf = seqcsv2sizecsv.calculate_size(notebook)
        else:
          notebook.sizedf = pd.read_csv(sizecsvpath, index_col = "NEW_REFINEMENT")
      except:
        notebook.sizedf = seqcsv2sizecsv.calculate_size(notebook)

      # if os.path.basename(refinement) == "_Fe_272_to_205":
      #   import pdb; pdb.set_trace();

      # if os.path.basename(refinement) == "_Fe_1407_to_208":
      #   import pdb; pdb.set_trace();

      """ plotting and saving the app. cryst. size informations. """
      plot_seq_tools.size_plot(notebook, outpath)

    """ checking if no plots have been generated. If not, output folder is deleted. """
    if os.listdir(outpath) == []:
      try:
        os.rmdir(outpath)
        print("    removed " + str(os.path.basename(outpath)) + " from " + str(os.path.dirname(outpath)) )
      except:
        print("    failed to remove " + str(os.path.basename(outpath)) + " from " + str(os.path.dirname(outpath)) )
    # return # premature return to save time when debugging.
  return






# print("\n\nEND_OF_SCRIPT")
# print(sys.version_info)
# print(sys.executable)
