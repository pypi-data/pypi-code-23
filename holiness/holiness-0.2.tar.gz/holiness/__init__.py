"""
Produce nice headlines

    * head

head will create a headline for you, basically in the form

==============================  H E A D L I N E  ===============================

"""

def headline(
        in_string,
        surround  = False,
        width     = 72,
        nr_spaces = 2,
        spacesym  = ' ',
        char      = '=',
        border    = None,
        uppercase = True,
    ):
    """return in_string capitalized, spaced and sandwiched:

    ==============================  T E S T  ===============================

    Parameters are the following:

    * char (one-letter string, default='='):

      changes the character the title is put between.

    * surround (boolean, default=False):

      adds additional lines above and under in_string:

            ====================================================
            ====================  T E S T  =====================
            ====================================================

    * width (int, default=72):

      defines the width of each line.

    * nr_spaces (int, default=2):

      defines number of nr_spaces between in_string and the 
      char as indicated in ..====__T I T L E__====.. .

    * spacesym (one-letter string, default=' '):

      instead of using a whitespace to seperate the 'title' letters,
      one can use every other character, e.g. '_'.

    * border (either string or list/tuple of two strings; defaults to char):

      If this is a single character string, it will be used at the left
      and right end of the headline.
      If this is multiple character string, it will be used at the left
      and mirrored at the right. This way you can easily introduce additional
      space if you prefer and use, for example c style like inline comments
      with border="/*".
      If this is not enough for you, the left and right borders can be given
      seperately, like in border=("<!--", "-->")

    * uppercase (boolean, default=True):

      if True, headline will capitalize the letters given by in_string.
      if False, in_string will be used as it is given.
    """

    if isinstance(border, tuple) or isinstance(border, list):
        left_border = border[0]
        right_border = border[1]
    else:
        if border is None:
            border = char
        left_border = border
        right_border = border[::-1]

    nr_sym_spaces = len(left_border + right_border)

    headline_text = spacesym.join(
        l.upper() if uppercase else l for l in in_string
    )

    headline_text_sandwiched = '{:{}^{}}'.format(
        headline_text,
        spacesym,
        2 * (len(in_string) + nr_spaces) - 1
    )

    headline_without_sym = '{:{}^{}}'.format(
        headline_text_sandwiched,
        char,
        width - nr_sym_spaces
    )

    headline_full = '{1}{0}{2}'.format(
        headline_without_sym,
        left_border,
        right_border
    )

    if surround:
        line = '{1}{0}{2}'.format(
            (width - nr_sym_spaces) * char,
            left_border,
            right_border
        )
        output = line + '\n' + headline_full + '\n' + line
    else:
        output = headline_full

    return output
