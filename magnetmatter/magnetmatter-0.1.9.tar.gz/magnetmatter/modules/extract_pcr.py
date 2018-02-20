# extract_pcr.py

def getwavelength(pcrpath):
  """ searches .pcr file for wavelength

  example snippet from pcrpath:
    ! Lambda1  Lambda2    Ratio    Bkpos    Wdt    Cthm     muR   AsyLim   Rpolarz  2nd-muR -> Patt# 1
    0.207000 0.207000  1.00000   40.000 25.0000  0.9999  0.0000    0.00    0.0000  0.0000

  """
  with open(pcrpath, "r") as reading:
    for line in reading:
      if "Lambda1  Lambda2    Ratio" in line:
        line = next(reading)
        w1, w2, ratio = [float(item) for item in line.split()[:3]]
        wavelength = (float(w1) + float(w2)*float(ratio)) / (1+float(ratio))
        return wavelength
  return

def getphases(pcrpath):
  """ searches .pcr file for phases.

  example snippet from pcrpath:
    !-------------------------------------------------------------------------------
    !  Data for PHASE number:   2  ==> Current R_Bragg for Pattern#  1:   110.90
    !-------------------------------------------------------------------------------
    Fe$_3$O$_4$

  returns:
    list with phases in ordered sequence"""
  with open(pcrpath, "r") as reading:
    retlist = []
    for line in reading:
      if "Data for PHASE number:" in line:
        line = next(reading)
        line = next(reading).strip()
        retlist.append(line)
    return retlist
  return
