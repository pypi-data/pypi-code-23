# plot_seq_tools.py

import pandas as pd, numpy as np, math
# from plot_seq_tools import Notebook # amazingly we don't need to import Notebook!



def calculate_size(notebook):
  """
  df:
    pandas.dataframe with columns of refined parameters extracted from FullProf's .seq file
  wavelength:
    floating point number in Ångstrøm.

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
  def calc_inverse_lorentzian(ydegree):
    """ helper function (can also be used for ydegree_error!)

    Y[Å^-1] = Y[°] * PI^2 / 180 / 2 / wavelength[Å] * 1000

    this function only works because <wavelength> is already defined in the parent function

    """
    yinverseangstroem = ydegree * math.pow(math.pi, 2) / 36.0 / notebook.wavelength * 100
    return yinverseangstroem

  def multiply_invers_100(somevalue):
    """ helper function

    a,b-size[nm] = 100 / Y[Å^-1]

    """
    try:
      absize = 100 / somevalue
    except ZeroDivisionError:
      absize = np.nan
    return absize


  columnnames = []

  for col in notebook.lorsizelist:
    """ working with Y-cos_ph1_pat1
    to create L-Size_ph1_pat1, ab-size and c-size
    plus all errors """
    lorsize = "Y-cos"
    columnnames.append(col)
    columnnames.append(col + "_err")
    stripped = col.strip(lorsize)
    lorsizedistribution = "L-Size"
    columnnames.append(lorsizedistribution+stripped)
    columnnames.append(lorsizedistribution+stripped+"_err")
    absize = "ab-size"
    columnnames.append(absize+stripped)
    columnnames.append(absize+stripped+"_err")
    csize = "c-size"
    columnnames.append(csize+stripped)
    columnnames.append(csize+stripped+"_err")

  """ creating the outlay for the sizedf filled with zeros """
  myzeros = np.zeros( shape=(notebook.seqdf[notebook.lorsizelist[0]].size, 8*len(notebook.lorsizelist)) )

  """ initializing sizedf with columns from columnnames"""
  newdf = pd.DataFrame(myzeros, index = notebook.seqdf.index, columns = columnnames)
  for col in newdf.columns:
    try:
      """ importing columns from seqdf to sizedf """
      newdf[col] = notebook.seqdf[col]
    except KeyError:
      pass
  for col in columnnames:
    """ filling out the columns corresponding to ab- and c-size """
    if lorsize in col and not col.endswith("_err"):
      newdf[col] = newdf[col].apply(calc_inverse_lorentzian)
      newdf[col+"_err"] = newdf[col+"_err"].apply(calc_inverse_lorentzian)
      stripped = col.strip(lorsize)
      newdf[absize+stripped] = newdf[col].apply(multiply_invers_100)
      """ σ_a,b-size[nm] = 100 * (σ_Y[Å^-1]^2 / Y[Å^-1]^4)^0.5 """
      target = absize+stripped+"_err"
      newdf[target] = newdf[col+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target].div(newdf[col].apply(lambda x: math.pow(x,4)))
      newdf[target] = newdf[target].apply(lambda x: math.sqrt(x))
      newdf[target] = newdf[target].apply(lambda x: x*100)
      """ c-size[nm] = 100 / (Y[Å^-1] + S_Z[Å^-1]) """
      target = csize+stripped
      newdf[target] = newdf[col] + newdf[lorsizedistribution+stripped]
      newdf[target] = newdf[target].apply(multiply_invers_100)
      """ σ_c-size[nm] = =100 * ((σ_Y[Å^-1]^2 + σ_sz[Å^-1]^2) / (Y[Å^-1] + S_z[Å^-1])^4)^0.5 """
      target = csize+stripped+"_err"
      newdf[target] = newdf[col+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target] \
        + newdf[lorsizedistribution+stripped+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target] \
        .div((newdf[col] + newdf[lorsizedistribution+stripped]).apply(lambda x: math.pow(x,4)))
      newdf[target] = newdf[target].apply(lambda x: math.sqrt(x))
      newdf[target] = newdf[target].apply(lambda x: x*100)
      # celebrate!



  """ cleaning up if NaNs have been introduced by the multiply_invers_100 function"""
  indices_with_nan = set(np.where(np.isnan(newdf))[0])
  indices_to_keep  = [index for index in range(newdf.index.size) if index not in indices_with_nan]
  newdf = newdf.iloc[indices_to_keep]
  """ saving to .csv """
  newdf.to_csv("_size.csv")
  """ return the sizedf dataframe """
  return newdf







# end
