from enforsml.text import word


def normalize(txt):
    """Return a normalized copy of txt.
    """

    txt = normalize_whitespace(txt)
    txt = unify_sentence_dividers(txt)

    return txt


def unify_sentence_dividers(txt):
    """Return copy of txt with ? and ! replaced with .
    """

    for ch in ["!", "?"]:
        txt = txt.replace(ch, ".")

    return txt


def remove_junk_chars(txt):
    """Return copy of txt without unneeded chars.
    """

    for ch in [": ", "; "]:
        txt = txt.replace(ch, " ")

    for ch in [".", ",", "(", ")", '"']:
        txt = txt.replace(ch, "")

    return txt


def remove_words(txt, words_to_remove):
    """Return a copy of the txt string with the specified words (not Words)
    removed.
    """

    output = ""

    for wrd in txt.split(" "):
        if wrd not in words_to_remove:
            output += wrd + " "

    return output.strip()


def split_sentences(txt):
    """Attempt to split a txt into sentences.
    """

    txt = normalize_whitespace(txt)
    txt.replace("!", ".")
    txt.replace("?", ".")
    sentences = [sentence.strip() for sentence in txt.split(". ")]

    sentences[-1] = sentences[-1].rstrip(".")

    return sentences


def split_sentence(txt):
    """Given a normalized sentence, return a list of Words.
    """

    words = []
    for part in txt.split(" "):
        words.append(word.Word(part))

    return words


def normalize_and_split_sentences(txt):
    """Return normalized sentences.

    >>> normalize_and_split_sentences("Foo bar. Another small sentence.")
    ['Foo bar', 'Another small sentence']
    >>> normalize_and_split_sentences(" Foo bar. Another  small sentence.")
    ['Foo bar', 'Another small sentence']
    >>> normalize_and_split_sentences("Foo bar . Another  small sentence.")
    ['Foo bar', 'Another small sentence']
    """

    txt = normalize(txt)
    sentences = split_sentences(txt)

    return sentences


def normalize_whitespace(txt):
    """Return a copy of txt with one space between all words, with all
    newlines and tab characters removed.

    >>> print(normalize_whitespace("some text"))
    some text
    >>> print(normalize_whitespace(" some text "))
    some text
    >>> print(normalize_whitespace(" some   text"))
    some text
    >>> print(normalize_whitespace('\t\tsome text'))
    some text
    >>> print(normalize_whitespace("  some       text "))
    some text
    """

    new_txt = txt.replace("\n", " ")
    new_txt = new_txt.replace("\r", "")
    new_txt = new_txt.replace("\t", " ")

    words = [word.strip() for word in new_txt.split(" ") if len(word) > 0]
    new_txt = " ".join(words)
    return new_txt
