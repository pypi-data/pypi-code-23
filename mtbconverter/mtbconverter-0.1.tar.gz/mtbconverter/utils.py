"""
Utility collection with helper methods
"""
import os
import re

BARCODE_REGEX = "Q[A-X0-9]{4}[0-9]{3}[A-X][A-X0-9]"

def getbarcode(path):
    """Extract an OpenBis barcode from the file name.
    If a barcode is found, return it. Raise ValueError if no barcode,
    or more that one barcode has been found.
    Barcodes must match this regular expression: [A-Z]{5}[0-9]{3}[A-Z][A-Z0-9]
    """
    stem, suffix = os.path.splitext(os.path.basename(path))
    barcodes = re.findall(BARCODE_REGEX, stem)
    valid_barcodes = [b for b in barcodes if is_valid_barcode(b)]
    if not barcodes:
        raise ValueError("no barcodes found")
    if len(set(barcodes)) > 1:
        raise ValueError("more than one barcode in filename")
    return barcodes[0]


def is_valid_barcode(barcode):
    """Check if barcode is a valid OpenBis barcode."""
    if re.match('^' + BARCODE_REGEX + '$', barcode) is None:
        return False
    csum = sum(ord(c) * (i + 1) for i, c in enumerate(barcode[:-1]))
    csum = csum % 34 + 48
    if csum > 57:
        csum += 7
    if barcode[-1] == chr(csum):
        return True
    return False