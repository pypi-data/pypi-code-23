from . import tax_types

def NoTax():
    res = tax_types.NoTax(None)
    res._vat_percentager = 0
    res._eu_reverse_charge = False
    return res

def EUReverseCharge():
    res = tax_types.EUReverseCharge(None)
    res._vat_percentage = 0
    res._eu_reverse_charge = True
    return res

def VATPercentage(percentage):
    res = tax_types.VATPercentage(None)
    res._eu_reverse_charge = False
    res.percentage = percentage
    return res
