# Source: http://code.activestate.com/recipes/81611-roman-numerals/
# License: Python Software Foundation (PSF) license

def roman_to_int(n):
    """Convert a roman numeral to an integer."""
    numeral_map = zip(
        (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
        ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I'))

    idx = total = 0
    for integer, glyph in numeral_map:
        width = len(glyph)
        while n[idx:idx + width] == glyph:
            total += integer
            idx += width
    return total
