# prf_plot_tools.py

from decimal import Decimal
import re, os, math, numpy as np
from wrappers import TraceCalls
from find_tools import findfile, findfiles

@TraceCalls()
def get_spacegroups():
  """
  Creates a dictionary with spacegroups from FullProf .pcr file

  Returns:
    Dictionary of all spacegroups found bundled with a numeric key
    that correspond to the spacegroup's placement in the .pcr file.

  """
  pcr = findfile(".pcr")
  spacegroups = dict()
  with open(pcr,"r") as reading:
    i = 1
    for line in reading:
      if "<--Space group symbol" in line:
        spacegroup = line.split("<--Space group symbol")[0].strip()
        spacegroups[str(i)]=spacegroup
        i+=1
  return spacegroups

def excluded_regions():
  """
  Searches Fullprof .pcr file for code indicating exclusion of diffraction pattern.

  Returns:
    integer number of excluded regions.
    "0" = no excluded regions
    "1" = one excluded region
    etc.

  """
  pcr = findfile(".pcr")
  nb_excluded_regions = 0
  with open(pcr,"r") as reading:
    for line in reading:
      if "Excluded regions (LowT  HighT) for Pattern#" in line:
        while True:
          if reading.readline()[0] != "!": nb_excluded_regions += 1
          else: break
  return nb_excluded_regions



@TraceCalls()
def extract_out_file():
  """
  Extracts wavelengths, phase fractions, phases and refined parameters from FullProf .out file

  Returns:
    A tuple with the following 4 objects

    wavelength:
      floating point number of wavelength. The possible K alpha1
      and K alpha2 ratio is taken into account.

    frac_info: Dictionary of phase volume fractions.
      keys: phase name extracted in .out file.
      values: tuple of value and its error.

    phases: Dictionary of phases found in .out file bundled with numeric
            integer indication phase relationship.
      keys: phase number extracted from .out file.
      values: string of phase name as writting in .pcr file.

    refined_par: Dictionary of refined parameters.
      keys: FP notation of refined parameters.
      values: tupe with value and its error.

  """

  out = findfile(".out")
  with open(out,"r") as reading:
    """ extracting the relevant parameters """
    refined_par = dict()
    phases = dict()
    frac_info = dict()
    read_phase = False
    start = False; found = False
    for line in reading:
      if "Conventional Rietveld Rp,Rwp,Re and Chi2:" in line: #  => Conventional Rietveld Rp,Rwp,Re and Chi2:   13.1      16.9      6.06      7.765
        line = line.strip().split()
        rwp, chi2 = line[-3::2]
        refined_par["R wp / chi2"] = (float(rwp), float(chi2))
        continue
      if "Fract(%):" in line:
        line = line.strip().split("Fract(%):")[-1]
        #   => Bragg R-factor:   28.0       Vol:  591.768( 0.238)  Fract(%):   11.41( 2.25)
        frac, frac_error = [number.strip() for number in line.strip(")").split("(")]
        #  => Phase:  1     $\gamma$-Fe$_2$O$_3$ nuclear
        phasename = re.search("=> Phase:\s*\d+\s*([^\s].+)", prev_line.strip()).group(1)
        frac_error = "100.00" if frac_error == "*****" else frac_error
        frac_info[phasename] = (float(frac), float(frac_error))
      prev_line = line

      if "Wavelengths:" in line:
        w1, w2 = line.strip().split()[-2:]
      if "Alpha2/Alpha1 ratio:" in line:
        ratio = line.strip().split()[-1]
        wavelength = (float(w1) + float(w2)*float(ratio)) / (1+float(ratio))
      if read_phase:
        phases[phase_nr] = line.strip()
        read_phase = False
      if "=> Phase  No." in line:
        phase_nr = line.strip().split()[-1]
        read_phase = True
      if not start:
        start = re.search("SYMBOLIC NAMES AND FINAL VALUES AND SIGMA OF REFINED PARAMETERS:",line)
      if start:
        if re.search("Number of bytes for floating point variables",line):
          break
        """       ->  Parameter number    7 :      L-Size_ph1_pat1     1.4556953    ( +/-     1.4023348     ) """
        found = re.search(":\s*([^\s]+)\s*([^\s]+)\s*\( \+/-\s*([^\s]+)\s*\)",line)
      if found:
        key,value,error = found.group(1),found.group(2),found.group(3)
        refined_par[key] = (float(value), float(error))
  return wavelength, frac_info, phases, refined_par

@TraceCalls()
def calculate_size(wavelength = "", phases = "", refined_par = ""):
  """
  returns a dictionary containing ab- and c-size for each phase calculated from Y-cos and L-size.

  Args:
    phases: Dictionary
      keys: index
      value: string of phasename
    refined_par: Dictionary
      key: FP name of refined parameter
      value: tuple(value, error)
  Returns:
    dictionary:
      key: phase
      value:
        dict(key=ab- or c-size, value = tuple(value, error))

  What is calculated:
    Extracted from Anna's Excel Sheet. Do not change!

    CITATIONS MISSING!

    Y[°]	from .out as "Y-cos_ph1_pat1"

    σ_Y[°]	from .out error for above

    S_z[Å^-1]	from .out as "L-Size_ph1_pat1"

    σ_sz[Å^-1]	from .out error for above.

    Y[Å^-1] = Y[°] * PI^2 / 180 / 2 / wavelength[Å] * 1000

    σ_Y[Å^-1] = σ_Y[°] * PI^2 / 180 / 2 / wavelength * 1000

    # ab size

    a,b-size[nm] = 100 / Y[Å^-1]

    σ_a,b-size[nm] = 100 * (σ_Y[Å^-1]^2 / Y[Å^-1]^4)^0.5

    # c size

    c-size[nm] = 100 / (Y[Å^-1] + S_Z[Å^-1])

    σ_c-size[nm] = =100 * ((σ_Y[Å^-1]^2 + σ_sz[Å^-1]^2) / (Y[Å^-1] + S_z[Å^-1])^4)^0.5

  """
  res_dict = dict()
  ycos = list()
  gsize = list()
  for key in refined_par.keys():
    if "Y-cos" in key:
      ycos.append(key)
    elif "G-Size" in key:
      gsize.append(key)
  for key in ycos:
    phase_pattern = re.search("_ph(\d+)_pat\d+",key)
    lsize_key = "L-Size" + phase_pattern.group(0)
    phase_nr = phase_pattern.group(1)
    phase = phases[phase_nr]
    for i, gsizeitem in enumerate(gsize):
      phase_nr2 = re.search("_ph(\d+)_pat\d+",gsizeitem).group(1)
      if phase_nr2 == phase_nr:
        gsize.pop(i)
        break
    Y, sigma_Y = refined_par[key]
    Sz,sigma_Sz = refined_par[lsize_key] if lsize_key in refined_par.keys() else (0,0)

    """ calculating the ab/c sizes. """
    Y_degree = Y
    Y_AA = Y_degree * math.pi**2 / 180 / 2 / wavelength * 1000
    sigma_Y = sigma_Y * math.pi ** 2 / 180 / 2 / wavelength * 1000

    try:
      absize = 100 / Y_AA
      sigma_absize = 100 * (sigma_Y ** 2 / Y_AA ** 4) ** 0.5
      csize = 100 / (Y_AA + Sz)
      sigma_csize = 100 * ((sigma_Y ** 2 + sigma_Sz ** 2) / (Y_AA + Sz) ** 4) ** 0.5
    except ZeroDivisionError:
      absize = np.nan
      csize = np.nan
      sigma_absize = np.nan
      sigma_csize = np.nan
    """ prepare dictionary """
    tmp_dict = {"app.cry. ab-size": (absize, sigma_absize), "app.cry. c-size": (csize, sigma_csize)}
    res_dict[phase] = tmp_dict

  """ the calculation performed below are done according to the docstring explanation """
  for key in gsize:
    """ find calculated appearent size from .mic """
    mics = findfiles(".mic")
    phase_pattern = re.search("_ph(\d+)_pat\d+",key)
    phase_nr = phase_pattern.group(1)
    phase = phases[phase_nr]
    mics = [mic for mic in mics if mic[-5] == phase_nr]
    for mic in mics:
      with open(mic, "r") as reading:
        for line in reading:
          if "Phase No:" in line:
            phasename = re.search("Phase No:\s*\d+\s*(.*)", line)
            phasename = phasename.group(1).strip()
          if "standard deviation (anisotropy):" in line:
            found = re.search(":\s*([^\s]+)\s*\(\s*([^\s]+)\)", line)
            size,error = found.group(1),found.group(2)
            absize,sigma_absize = (float(size)/10.0, float(error)/10.0) # div 10 to go Å to nm.
            csize,sigma_csize = (float(size)/10.0, float(error)/10.0) # div 10 to go Å to nm.
            break
    tmp_dict = {"app.cry. ab-size": (absize, sigma_absize), "mic": (csize, sigma_csize)}
    res_dict[phase] = tmp_dict

  return res_dict

def find_significant_figure(error_value_as_string):
  """
  Calculates the number of signification digits allowed from a given error.

  Args:
      error_value_as_string: String of an error value

  Returns:
      length of error value given as edible integer index for the decimal.Decimal module
      Is used to shorten the actual value.

  Examples:
      Eg. value = 1.0034 but error = 0.1, then returned index will be
      1. Value is displayed as 1.0(1).

      Eg. value = 0.1001 and error = 2.0, then returned index is -1.
      Value is displayed as 0(2).

  """
  try:
    error_value_as_string = str(error_value_as_string)
    if error_value_as_string[0] == "-":
      error_value_as_string = error_value_as_string[1:]
    if not re.search("\.", error_value_as_string):
      return -len(error_value_as_string)+1
    if error_value_as_string[0] != "0":
      return -len(error_value_as_string.split(".")[0])+1
    error_value_as_string = error_value_as_string.rstrip("0")
    no_period = re.sub("\.","",error_value_as_string)
    integer = int(no_period)
    return len(no_period) - len(str(integer))
  except Exception as e:
    import pdb; pdb.set_trace(); print(e); print("error_value_as_string =", error_value_as_string, "\n")

def round2significant_error(value, error, length = ""):
  """ Combines a value and its error to a compactly formatted string.

  Args:
    value: the refined parameter value
    error: the error of the refined parameter value.
    length: the maximum allowed lenght of return string

  Returns:
    String that has been formatted to only to the point of
    the significant figure according to the FullProf provided error.
    See examples below.

  example 1:
    value = 34.5623
    error = 0.03
    length = 15
    output = 34.56(3)

  example 2:
    value = -34.5623
    error = 11.03
    length = 15
    output = -3(1)e+01 --> always at least 9 chars to describe equal length value/error.

  example 3:
    value = 34.5623
    error = 0.03
    length = 5
    output = 35(0)

    """
  if error is not np.nan:
    error = abs(error)
  strvalue = "{:.100f}".format(value)
  strerror = "{:.100f}".format(error)
  if (value == 0.0) and (error == 0.0):
    return "0(0)"
  if (value is np.nan) or (error is np.nan):
    return "NaN"
  if (str(value).lower() == "nan") or (str(error).lower() == "nan"):
    return "NaN"
  if length != str():
    roundvalue = round(Decimal(strvalue), length)
    rounderror = round(Decimal(strerror), length)
    result = round2significant_error(float(roundvalue), float(rounderror))
    i = 1
    while len(result) > length:
      strvalue = "{:.100f}".format(float(roundvalue))
      strerror = "{:.100f}".format(float(rounderror))
      roundvalue = round(Decimal(strvalue), length-i)
      rounderror = round(Decimal(strerror), length-i)
      result = round2significant_error(float(roundvalue), float(rounderror))
      i+=1
    return result
  if error == 0:
    if "e" in str(value):
      """ this option called if round2significant_error calls itself
      with a zero error. """
      pre,post = str(value).split("e")
      return "{}{}e{}".format(pre,"(0)",post)
    else:
      return "{}({})".format(str(value),"0")

  sign = "" if value >= 0 else "-"
  strvalue = "{:.100f}".format(value)
  strerror = "{:.100f}".format(error)
  significant_value = find_significant_figure(strvalue)
  significant_error = find_significant_figure(strerror)
  roundvalue = round(Decimal(strvalue), significant_error)
  rounderror = round(Decimal(strerror), significant_error)
  if significant_error < 0:
    rounderror = "{:.100f}".format(float(rounderror))
    significant_error = find_significant_figure(rounderror)
    significant_value = find_significant_figure(strvalue)
    roundvalue = round(Decimal(strvalue), significant_error)
    rounderror = round(Decimal(strerror), significant_error)
    exponent = str(-significant_error) if abs(significant_error) > 10 else "0" + str(-significant_error)
    index = len(str(abs(int(roundvalue)))) - len(str(int(rounderror))) + 1
    if index == 0:
      index = 1
      roundvalue = 0
    string = "{}{}({})e+{}".format(sign,str(int(abs(roundvalue)))[:index],str(rounderror)[0],exponent)
    return string
  else:
    if abs(roundvalue) <= abs(rounderror):
      roundvalue = round(Decimal(strvalue), significant_error)
      rounderror = round(Decimal(strerror), significant_error)
      if roundvalue != 0:
        roundvalue = str(roundvalue).rstrip(".0")
      if rounderror != 0:
        rounderror = str(rounderror).rstrip(".0")
    """ investigate if new significant figure of error,
    if so, update roundvalue and rounderror """
    if "E" in str(rounderror):
      newposition = int(re.search("E[+-0](\d+)",str(rounderror)).group(1))
      rounderror = re.search("(\d)[.\d]*E",str(rounderror)).group(1)
    else:
      # try:
      #     rounderror = "{:.20f}".format(float(rounderror))
      # except:
      #     import pdb; pdb.set_trace(); print("rounderror =",rounderror)
      newposition = find_significant_figure(rounderror)
      rounderror = str(round(Decimal(rounderror),newposition))
      if "." in rounderror:
        rounderror = rounderror[1+newposition]
      if "E" in rounderror:
        """ ugly workaround """
        pre,post = rounderror.split("E")
        tmp_post = int(post)
        roundvalue = int((float(roundvalue)-(float(roundvalue)%10**tmp_post))/10**tmp_post)
        if len(str(tmp_post)) == 1:
          post = post[0] + "0" + post[1]
        return "{}({})e{}".format(roundvalue,pre,post)
    roundvalue = round(Decimal(roundvalue),newposition)
    """ taking care that roundvalue is not expressed in scientific terms... """
    if "E" in str(roundvalue):
      roundvalue = "{:.20f}".format(float(roundvalue)).rstrip("0")
    return "{}({})".format(roundvalue,rounderror)

@TraceCalls()
def prepare_refinement_result(phases = "", refined_par = "", size_info = "", frac_info = "", spacegroups = "", wavelength = ""):
  """
  preparing information such as refined parameters, phases, phase fractions
  crystallite sizes and so to be printed on canvas.

  Args:
    phases: Dictionary
      keys: integer number
      values: phase names

    refined_par: Dictionary
      keys: FullProf named parameter
      values: tuple of value and its error

    size_info: dictionary
      keys: phase name
      values:
        tuple of ab and c appearent crystallite sizes
        calculated from Lorentzian line broadening and (if available)
        Lorenzian anisotropic parameter

    frac_info: dictionary of phase volume fractions.
      keys: phase name.
      values: value and its error.

    spacegroups: dictionary
      keys: integer number
      values: string of spacegroup name as written in .pcr file.

  Returns:
    string formatted to be printed on canvas, non-phase parameters on the top,
    then each phase (listed in sorted order) is listed with corresponding parameters.

    No support for showing linked parameters.
    Parameters associated with more phases are only plotted once.

  """

  """ preparing entry in dictionary for non-phase related pars """
  insert_text = {"0": []}
  """ preparing entries in a dictionary for information on the different phases """
  for phase_key in phases.keys():
    insert_text[phase_key] = ["{:16.15} {}".format(spacegroups[phase_key], phases[phase_key])]

  """ subfunction to prepare text for insertion """
  def insert_text2(newline, name, value, error):
    """
    Prepares a single stringline. Values and errors are rounded up.

    Args:
      newline: '\n' if needed.

      name: commonly the name of refined parameter. can also be phase name etc

      value: the predicted value from FP

      error: the calculated error from FP. The first non-zero index from error is used to determine the maximum shown value of 'value'.
    Returns:
      a single stringline that has name of refined parameter and value + error.

      e.g. value = 8.357975 error = 0.00049791916 for refined parameter Cell_A_ph1_pat is shown as

      'Cell_A_ph1_pat  8.3580(5)   [$\\AA$]\n'

      The (5) should be translated to 8.3580 +/- 0.0005

    """

    """ note on .format
    https://pyformat.info/

    note on strftime
    http://strftime.org/
    """

    """ finding correct unit for parameter """
    unitdict = {"unit" : "[$\\AA$]", "phase vol. frac." : "[%]", "app." : "[nm]"}
    unit = ""
    for key in unitdict.keys():
      if name.startswith(key):
        unit = unitdict[key]
        break
    """ checking if R wp / chi2 """
    if (name == "R wp / chi2"):
      """ restructuring the R wp and chi2 manually... """
      return "{}{}{:<11.10}{}{}{}".format(r"R$_{wp}$"," = ", value, r"$\chi^2$"," = ", error)
      # return "{}{:17.16}{:3.3} / {:3.3}".format(newline, name, value, error )
    string = round2significant_error(value, error, 13) # 13 corresponce to showing eight characters of str(value).
    result = "{}{:17.16}{:14.13}{}".format(newline, name, string, unit)
    return result
    # END of internal function

  """ unpacking refined parameters phase-wise, skipping background pars """
  for key, (value, error) in refined_par.items():
    if "bck_" in key.lower():
      continue
    phase_pattern = re.search("_ph(\d+)",key)
    if not phase_pattern:
      if key == "R wp / chi2":
        insert_text["0"].append( insert_text2("",key, value, error) )
        """ manually inserting the wavelength information """
        unit = "[$\\AA$]"
        insert_text["0"].append( "{}{:<17.16}{:<14.9}{}".format("\n","wavelength", wavelength, unit) )
      else:
        key = key.split("_pat")[0]
        if key == "Zero":
          key = "zero shift"
        if key == "zero shift":
          """ I decided to stop showing the zero shift. adds no information... """
          continue
        insert_text["0"].append( insert_text2("\n",key, value, error) )
      continue
    """ if parameter not special, we transform to appropiate names """
    key = key.split("_ph")[0]
    if key == "Bover":
      key = "debye-waller f."
    if key == "Scale":
      key = "scale factor"
    if key == "Y-cos":
      key = "lor. line broad."
    if key == "Cell_A":
      key = "unit cell A"
    if key == "Cell_C":
      key = "unit cell C"
    if key == "Cell_B":
      key = "unit cell B"
    if key == "L-Size":
      key = "lor. size distr."

    """ inserting refined parameters from FullProf """
    insert_text[phase_pattern.group(1)] += [insert_text2("\n",key, value, error)]
  """ inserting phase fraction informations """
  reversed_phases = {y:x for x,y in phases.items()}
  for key, (value,error) in frac_info.items():
    insert_text[reversed_phases[key]] += [insert_text2("\n","phase vol. frac.", value, error)]
  """ inserting crystallite size information """
  for key, sizes in size_info.items():
    if "mic" in sizes.keys():
      value, error = sizes["app.cry. ab-size"]
      insert_text[reversed_phases[key]] += [insert_text2("\n","mic-abc-size", value, error)]
    elif sizes["app.cry. ab-size"] == sizes["app.cry. c-size"]:
      value, error = sizes["app.cry. ab-size"]
      insert_text[reversed_phases[key]] += [insert_text2("\n","app. cryst. size", value, error)]
    else:
      for size in sizes:
        value, error = size_info[key][size]
        insert_text[reversed_phases[key]] += [insert_text2("\n",size, value, error)]
  """ combine all the different phase informations """
  combined_text = ""
  """ sorting phases for consistent output """
  tmp_keys = [key for key in insert_text.keys()]
  tmp_keys.sort(key = lambda x: insert_text[x][0].split("   ")[-1].split())
  tmp_keys.remove("0")
  tmp_keys = ["0"] + tmp_keys

  for key in tmp_keys:
    combined_text += insert_text[key].pop(0)
    tmp_list = [value for value in insert_text[key]]
    """ sorting the output according primarily to the first character
    and secondarily to the last character (if unit is included, parameter is put last)"""
    tmp_list.sort(key = lambda x: x[1::len(x)-2][::-1])
    combined_text += "".join(tmp_list) + "\n\n"

  return combined_text

# END
