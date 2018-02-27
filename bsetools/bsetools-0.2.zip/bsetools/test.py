from bsetools import bsetools
import pdb

if __name__ == '__main__' :
    obj = bsetools()
    #rewsdfggbcsss
    quote, difference = obj.get_quote("Tech Mahindra")
    bse_data = obj.get_BSE_index()
    print(quote, difference)
    print(bse_data.bse_index, bse_data.diff)