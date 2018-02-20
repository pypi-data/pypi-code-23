import os, sys,re, pandas as pd, matplotlib.pyplot as plt
sys.path.append(r"C:\AU-PHD\General_Data\_python\PyPi\magnetmatter\magnetmatter\modules")

class Container():
  """ note, if round brackets are _not_ used, no new instance
  of the class is created.
  _Without_ round brackets the first class object is used over and over.
  my code worked for generating the seq.csv file, but that was
  a pure coincidence. """

  def __init__(self, value = None, error = None):
    """ construct with None was necessary to avoid python to
    reuse an earlier initilized Container object.
    The expressions in the initializing part of a function is
    only called _once_ over an entire process. """
    self.value = value if value != None else []
    self.error = error if error != None else []

  def iterators(self):
    """ returns a tuple of iterators for the value and error lists """
    return (iter(self.value), iter(self.error))

  def __repr__(self):
    """ determines what is shown with built-in repr() or using interactive prompt """
    return "size of container (value, error) = (" + str(len(self.value)) + "," + str(len(self.value)) + ")"

  def __str__(self):
    """ determines what is shown with built-in print() """
    return repr(self)

  def __getitem__(self,key):
    """  overwrites default getitem command, e.g.
    list slicing alist[0], alist[0:10], alist[::-1] etc. """
    return Container(self.value[key], self.error[key])

  """ legacy code... """
  # def __lt__(self, object):
  #   """ define the lesser than < operator  """
  #   return self.value[0] < object.value[0]
  #
  # def __gt__(self,object):
  #   """ define the greater than > operator  """
  #   return self.value[0] > object.value[0]
  #
  # def __eq__(self, object):
  #   """ define the == operator """
  #   return self.value == object.value

class Mydict():
  """  """
  def __init__(self):
    """  """
    self.mydict = {}

  def check_repeating_elements(self):
    """ checking if multiple runs of sequential refinement have been
    carried out (refinement results are stupidly appended to existing .seq file) """

    mylist = self.mydict["NEW_REFINEMENT"].value
    # print("mylist =",mylist)
    # import pdb; pdb.set_trace();
    first_element = mylist[0]
    first_index = 0
    for num, element in enumerate(mylist):
      """ if sequential refinement has been carried out a second or more times
      the .seq file is just appended by FullProf, therefore introducion
      multiple occurences of same frame number. """
      if first_element == element:
        first_index = num
    # import pdb; pdb.set_trace();
    for key,item in self.mydict.items():
      # print(self.mydict[key].value[0:10])
      self.mydict[key] = self.mydict[key][first_index:]
      # print(self.mydict[key].value[0:10])
      # print("key =",key)


  def check_reverse(self):
    """ checking if sequential refinement was carried out
    from last to first frame. """
    mylist = self.mydict["NEW_REFINEMENT"].value
    first_element = mylist[0]
    first_index = 0
    # print("checking_reverse")
    # print("mylist[0] = ",mylist[0])
    # print("mylist[-1] = ",mylist[-1])
    # import pdb; pdb.set_trace();
    if int(mylist[0]) > int(mylist[-1]):
      # print("did we move on??")
      """ reversing the list of every refined parameter and excluding any starting duplicates. """
      for key,item in self.mydict.items():
        # print(self.mydict[key].value[0:10])
        self.mydict[key] = self.mydict[key][::-1]
        # print(self.mydict[key].value[0:10])
        # import pdb; pdb.set_trace();


  def add(self, var, value, error):
    """ adds <value, error> to the self.mydict under the tag <var> """
    if var in self.mydict.keys():
      self.mydict[var].value.append(value)
      self.mydict[var].error.append(error)
    else:
      self.mydict[var] = Container()
      # print("self =",self)
      # print("self.mydict =",self.mydict)
      # import pdb; pdb.set_trace();
      self.add(var,value,error)


  def dump(self, workingdir = ""):
    """ generates a csv readable by pandas

    ignores refined background parameters
    """
    workingdir = os.getcwd() if workingdir == "" else workingdir
    csvpath = os.path.join(workingdir, "_seq.csv")
    handle = open(csvpath,"w")
    myiterators = []
    writeval = ""
    """ checking if multiple sequential refinements has occured
    and if the lists should be reversed
    (i.e. sequential refinement was done from last to first frame) """
    self.check_repeating_elements()
    self.check_reverse()
    """ writing refined parameters to .csv file """
    for key in self.mydict.keys():
      """ first writing all column names """
      if key.startswith("Bck"): continue
      writeval += key + ","
      val_ite, err_ite = self.mydict[key].iterators()
      myiterators.append(val_ite)
      if not key in ["NEW_REFINEMENT", "GLOBAL_CHI_2"]:
        writeval += key + "_err,"
        myiterators.append(err_ite)
    writeval = writeval[:-1] + "\n"
    handle.write(writeval)
    writeval = ""
    # import pdb; pdb.set_trace();
    # import pdb; pdb.set_trace();
    while True:
      """ write all values and errors """
      try:
        for iterator in myiterators:
          writeval += str( iterator.__next__() ) + ","
        writeval = writeval[:-1] + "\n"
        if "NaN" in writeval:
          continue
        handle.write(writeval)
      except StopIteration:
        break
      finally:
        writeval = ""

    """ managing dangling file """
    handle.close()

    return csvpath


  def __repr__(self):
    retval = "keys of Mydict (" + str( len(self.mydict) ) + ") = ["
    for key in self.mydict.keys():
      retval += key + ",\n"
    retval += "\b\b] "
    return retval

  def __str__(self):
    return repr(self)



def seq2csv(csvpath):
  """ what is iterated over? Example:

  NEW_REFINEMENT       frame616
  NUMPAR    13
  N_PATT     1
  NPHASE     2
  PARVAL   408      0.0000        0
  GLOBAL_CHI_2      0.561820
       1         R_Bragg(%):     2.3198311         2.5157762
       1   Unit_Cell_Volume:     23.899607        0.95912709E-03
       1    Weight_Fraction:     13.881724        0.16681060
       2         R_Bragg(%):     8.1540928         5.6447506
       2   Unit_Cell_Volume:     599.82324        0.22575069E-01
       2    Weight_Fraction:     86.118271        0.61252558
       1     Cell_A_ph1_pat1     2.8804715        0.66740329E-04
       2     Cell_A_ph2_pat1     8.4334984        0.18325378E-03
       3           Zero_pat1   -0.35518815E-02    0.32384731E-03
       4          Bck_0_pat1     45.707390        0.18409243
       5          Bck_1_pat1    -31.257633        0.30232862
       6          Bck_2_pat1     13.554113        0.27447793
       7          Bck_3_pat1    -8.8670788        0.26058340
       8          Bck_4_pat1     3.7743287        0.22627439
       9          Bck_5_pat1    -1.3671141        0.21322817
      10      Scale_ph1_pat1    0.70008887E-05    0.77171720E-07
      11      Y-cos_ph1_pat1    0.82928445E-02    0.48348296E-03
      12      Scale_ph2_pat1    0.12760545E-06    0.67161066E-09
      13      Y-cos_ph2_pat1    0.30908650E-01    0.36040161E-03

  """
  # os.chdir(r"C:\AU-PHD\General_Data\Hamburg_2016May\gammaFe2O3_integrated\done_refined")
  workingdir = os.path.dirname(csvpath)
  mydict = Mydict()
  with open(csvpath,"r") as reading:
    for line in reading:
      found = re.match("\w",line)
      if found:
        found = re.match("GLOBAL_CHI_2\s+([^\s]+)",line)
        if found:
          found = found.group(1)
          mydict.add("GLOBAL_CHI_2", found, 0)
        found = re.match("NEW_REFINEMENT\s+[^\s]+?(\d+)$",line)
        if found:
          found = found.group(1)
          # print("found =",found)
          # import pdb; pdb.set_trace();
          mydict.add("NEW_REFINEMENT", found, 0)
      else:
        found = re.match("\s+(\d+)\s+([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*", line)
        if found:
          number = found.group(1)
          var = found.group(2)
          var = "".join( re.split("_pat\d+",var) )
          value = found.group(3)
          error = found.group(4)
          if var.endswith(":"):
            var = var[:-1] + "_ph" + str(number)
          var = re.sub("\(%\)","", var)
          mydict.add(var, value, error)
  csvname = mydict.dump(workingdir)
  return csvname

def visualize_csv(csvpath):
  """ plots every refined parameter from FullProf that is found in csv

  csvpath:
    path to comma-separated-file
  """
  # plt.figure()
  df = pd.read_csv(csvpath, index_col = "NEW_REFINEMENT")
  for colname in df.columns:
    try:
      if colname.endswith("_err"): continue
      if colname + "_err" in df.columns:
        df.plot(y=colname, yerr = colname + "_err")
      else:
        df.plot(y=colname)
      plt.savefig(colname + ".png")
    except Exception as e:
      print(e)
      import pdb; pdb.set_trace();
  return
